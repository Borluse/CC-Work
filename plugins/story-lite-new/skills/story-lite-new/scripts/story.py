#!/usr/bin/env python3
"""story-lite-new 账本脚本。

把 `.agent` 账本里判断成分最低的机械操作固化为子命令：定位、检索、汇总、
milestone 创建与切换、取号、状态流转。格式以同级 `convention.md` 为准；
脚本只做机械写入，不替代 Skill 的设计、决策与 Review 判断。

用法：python story.py [--cwd DIR] <命令> ...，详细参数见 `<命令> --help`。
输出是精简纯文本；出错时向 stderr 写 `error: 原因` 并以退出码 1 结束，且不修改任何文件。
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("error: 需要 PyYAML，请执行 pip install pyyaml")

REQUIREMENT_STATUSES = ["待设计", "设计中", "已确认", "实现中", "Review 中", "已完成", "已Review", "阻塞"]
BUG_STATUSES = ["待确认", "已确认", "修复中", "已修复", "已验证"]
QUICK_STATUSES = ["待确认", "已确认", "已完成"]

# 进入这两个状态时把当前状态压入 prior_status，恢复时弹出。
STACKING_STATUSES = ("Review 中", "阻塞")

QUICK_DIR = "quick"
MILESTONES_PATH = ".agent/milestones.yaml"
STORY_DIR = ".agent/story"

# 条目键序即落盘键序；未列出的键在写回时丢弃，因为 convention 禁止扩展字段。
ITEM_KEY_ORDER = [
    "id", "title", "milestone", "status", "keywords", "file",
    "design_review", "code_review", "continues", "continued_by", "prior_status",
]
BUG_KEY_ORDER = ["id", "title", "req", "milestone", "status", "file", "prior_status"]

# 检索时不算命中的泛词：它们出现在几乎每个需求点上，单独命中没有信息量。
GENERIC_TERMS = {"状态", "review", "learn", "设计", "实现", "文档", "需求", "story", "quick"}


# Windows 保留设备名，不区分大小写；匹配时需先去掉扩展名。
WINDOWS_RESERVED = re.compile(r"(?i)^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$")


class StoryError(Exception):
    """可预期的用户错误：打印 `error: 原因` 后退出，不修改文件。"""


# ── YAML 读写 ────────────────────────────────────────────────────────────────


class _Dumper(yaml.SafeDumper):
    """让块状列表相对父键缩进，与现有账本的书写风格一致，避免无谓的 diff。"""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def read_yaml(path):
    """读取并解析 YAML 文件。

    @param path: 文件路径。
    @return: 解析结果；文件不存在时为 None。
    """
    if not path.is_file():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise StoryError(f"{path} 不是有效 YAML: {error}")
    except (OSError, UnicodeDecodeError) as error:
        raise StoryError(f"无法读取 {path}: {error}")


def read_mapping(path):
    """读取顶层必须是映射的 YAML；空文件视为空映射，文件不存在时为 None。

    顶层类型不符时立即报错，避免后续把不认识的内容当空账本覆盖掉。

    @param path: 文件路径。
    @return: 映射，文件不存在时为 None。
    """
    doc = read_yaml(path)
    if doc is None:
        return None if not path.is_file() else {}
    if not isinstance(doc, dict):
        raise StoryError(f"{path} 顶层必须是映射")
    return doc


def write_yaml(path, data):
    """原子写入 YAML：先写临时文件再替换，避免中途失败留下半截账本；失败时清理临时文件。

    @param path: 目标文件路径，父目录不存在时创建。
    @param data: 待序列化的映射，键序按插入顺序保留。
    """
    # width 设为无穷：默认 80 列会把含空格的长标题折成多行，制造无谓的 diff。
    text = yaml.dump(data, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=float("inf"))
    temp = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temp, path)
    except OSError as error:
        temp.unlink(missing_ok=True)
        raise StoryError(f"无法写入 {path}: {error}")


# ── 账本模型 ─────────────────────────────────────────────────────────────────


def canonical(entry, order):
    """按固定键序重建条目并丢弃空值，落实「空的可选字段不写入」。

    @param entry: 原始条目。
    @param order: 该类条目的字段顺序，同时是允许出现的字段集合。
    @return: 可直接落盘的条目。
    """
    out = {}
    source = entry if isinstance(entry, dict) else {}
    for key in order:
        value = source.get(key)
        if value is None:
            continue
        if isinstance(value, list):
            value = [item for item in value if item is not None]
            if not value:
                continue
        elif isinstance(value, str) and not value.strip():
            continue
        out[key] = value
    return out


def read_counter(path, source, key):
    """读取计数器：缺省为 0，出现时必须是非负整数。

    布尔值虽然是 int 的子类，但不是合法编号，必须显式排除，否则 `true` 会被当成 1 导致跳号。

    @param path: 账本路径，用于错误信息。
    @param source: 账本顶层映射。
    @param key: `requirement` 或 `bug`。
    @return: 计数器值。
    """
    value = source.get(key)
    if value is None:
        return 0
    if type(value) is not int or value < 0:
        raise StoryError(f"{path} 的 {key} 必须是非负整数，收到 {value!r}")
    return value


def read_entries(path, source, key, order, list_fields):
    """读取并校验条目数组，返回规范化后的条目。

    读入时就拒绝损坏条目，避免后续命令以 traceback 退出，或把损坏内容写回账本。
    每个条目必须有整数 id，以及字符串类型的 title、milestone、status。

    @param path: 账本路径，用于错误信息。
    @param source: 账本顶层映射。
    @param key: `items` 或 `bugs`。
    @param order: 该类条目的字段顺序。
    @param list_fields: 出现时必须是列表的可选字段。
    @return: 规范化后的条目列表。
    """
    raw = source.get(key)
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise StoryError(f"{path} 的 {key} 必须是列表")
    entries = []
    for position, item in enumerate(raw, 1):
        where = f"{path} 的 {key} 第 {position} 项"
        if not isinstance(item, dict):
            raise StoryError(f"{where} 必须是映射")
        if type(item.get("id")) is not int:
            raise StoryError(f"{where} 缺少整数 id")
        for field in ("title", "milestone", "status"):
            if not isinstance(item.get(field), str):
                raise StoryError(f"{where} 的 {field} 必须是字符串，收到 {item.get(field)!r}")
        for field in list_fields:
            if item.get(field) is not None and not isinstance(item[field], list):
                raise StoryError(f"{where} 的 {field} 必须是列表")
        entries.append(canonical(item, order))
    return entries


def check_ids(path, key, counter, entries):
    """校验计数器与条目编号一致：id 不重复，且计数器不小于已有最大编号。

    编号只来自计数器，这个前提被破坏（例如旧键 `需求` 被当成 0）时，next-id 会分配出重复编号，
    因此读入时就拒绝。

    @param path: 账本路径，用于错误信息。
    @param key: 计数器名，`requirement` 或 `bug`。
    @param counter: 计数器值。
    @param entries: 该类条目列表。
    """
    ids = [entry["id"] for entry in entries]
    if len(set(ids)) != len(ids):
        raise StoryError(f"{path} 中 {key} 的 id 有重复")
    if ids and counter < max(ids):
        raise StoryError(f"{path} 的 {key} 计数器（{counter}）小于已有最大编号（{max(ids)}），请先修正")


def load_ledger(root, slug):
    """读取一个正式主题的 index.yaml，校验并规范化。

    计数器只取账本里的值，不扫描目录推断，避免与无条目的历史文档冲突。

    @param root: 工作目录。
    @param slug: 主题短名称。
    @return: (账本路径, 账本文件是否存在, 规范化后的账本)。
    """
    path = root / STORY_DIR / slug / "index.yaml"
    source = read_mapping(path) or {}
    if "需求" in source and "requirement" not in source:
        raise StoryError(f"{path} 使用了旧键 需求，请改名为 requirement")
    ledger = {
        "requirement": read_counter(path, source, "requirement"),
        "bug": read_counter(path, source, "bug"),
        "items": read_entries(
            path, source, "items", ITEM_KEY_ORDER, ("keywords", "continues", "continued_by", "prior_status")),
        "bugs": read_entries(path, source, "bugs", BUG_KEY_ORDER, ("prior_status",)),
    }
    check_ids(path, "requirement", ledger["requirement"], ledger["items"])
    check_ids(path, "bug", ledger["bug"], ledger["bugs"])
    return path, path.is_file(), ledger


def save_ledger(path, ledger):
    """写回主题账本；items 与 bugs 为空时省略整个键。

    @param path: 账本路径。
    @param ledger: 规范化后的账本。
    """
    out = {"requirement": ledger["requirement"], "bug": ledger["bug"]}
    if ledger["items"]:
        out["items"] = ledger["items"]
    if ledger["bugs"]:
        out["bugs"] = ledger["bugs"]
    write_yaml(path, out)


def load_milestones(root):
    """读取 milestones.yaml。

    读取阶段对 created 保持容忍（非法值记为 None），让 init、status 仍可用于诊断；
    写回时由 save_milestones 拒绝，保证不会把问题固化成 null。

    @param root: 工作目录。
    @return: (文件是否存在, current, {名称: created 日期})；日期保持 date 对象，写回时不会被加引号。
    """
    path = root / MILESTONES_PATH
    source = read_mapping(path) or {}
    raw = source.get("milestones")
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise StoryError(f"{path} 的 milestones 必须是映射")
    milestones = {}
    for name, value in raw.items():
        created = value.get("created") if isinstance(value, dict) else None
        if isinstance(created, datetime.datetime):
            created = created.date()
        elif isinstance(created, str):
            try:
                created = datetime.date.fromisoformat(created)
            except ValueError:
                created = None
        elif not isinstance(created, datetime.date):
            created = None
        milestones[str(name)] = created
    current = source.get("current")
    return path.is_file(), str(current) if current is not None else "", milestones


def save_milestones(root, current, milestones):
    """写回 milestones.yaml，每个 milestone 只保留 created 字段；created 缺失或非法时报错，不写文件。

    @param root: 工作目录。
    @param current: 当前 milestone。
    @param milestones: {名称: created 日期}。
    """
    for name, created in milestones.items():
        if created is None:
            raise StoryError(f"{MILESTONES_PATH} 中 {name} 的 created 缺失或不是 YYYY-MM-DD，请先修正")
    write_yaml(root / MILESTONES_PATH, {
        "current": current,
        "milestones": {name: {"created": created} for name, created in milestones.items()},
    })


def load_quick(root, milestone):
    """读取某个 milestone 的 Quick 账本，校验 title 与 status 为字符串。

    @param root: 工作目录。
    @param milestone: milestone 名。
    @return: (账本路径, 条目列表)；条目只含 title 与 status。
    """
    path = root / STORY_DIR / QUICK_DIR / milestone / "index.yaml"
    raw = (read_mapping(path) or {}).get("items")
    if raw is None:
        return path, []
    if not isinstance(raw, list):
        raise StoryError(f"{path} 的 items 必须是列表")
    items = []
    for position, item in enumerate(raw, 1):
        if not isinstance(item, dict) or not all(isinstance(item.get(f), str) for f in ("title", "status")):
            raise StoryError(f"{path} 的 items 第 {position} 项必须是含字符串 title 与 status 的映射")
        items.append(canonical(item, ["title", "status"]))
    return path, items


def list_slugs(root):
    """列出正式主题；quick 是保留目录名，不算主题。

    @param root: 工作目录。
    @return: 排序后的 slug 列表。
    """
    story = root / STORY_DIR
    if not story.is_dir():
        return []
    return sorted(
        entry.name for entry in story.iterdir()
        if entry.is_dir() and entry.name != QUICK_DIR and not entry.name.startswith(".")
    )


def resolve_milestone(root, explicit):
    """取显式给出的 milestone，省略时取 milestones.yaml 的 current。

    @param root: 工作目录。
    @param explicit: 命令行传入的 milestone，可为 None。
    @return: 校验通过的 milestone 名。
    """
    if explicit is not None:
        return check_segment("milestone", explicit)
    exists, current, _ = load_milestones(root)
    if not exists or not current:
        raise StoryError(f"没有 current milestone：请创建 {MILESTONES_PATH} 或显式传入 --milestone")
    return current


# ── 校验与纯规则 ─────────────────────────────────────────────────────────────


def check_segment(label, value):
    """校验值是单个路径段，避免 slug 与 milestone 破坏目录结构。

    Windows 设备名（如 CON、NUL.txt）不能作为目录名，创建后难以删除，因此一并拒绝。

    @param label: 字段名，用于错误信息。
    @param value: 待校验的值。
    @return: 去除首尾空白后的值。
    """
    text = (value or "").strip()
    if not text or len(re.split(r"[\\/]", text)) != 1 or text in (".", ".."):
        raise StoryError(f"{label} 必须是单个非空路径段，收到 {value!r}")
    if WINDOWS_RESERVED.match(text.split(".")[0]):
        raise StoryError(f"{label} 不能使用 Windows 保留名，收到 {value!r}")
    return text


def check_slug(value):
    """校验 slug：单个路径段且不能占用保留名 quick。

    「最多 5 个中文词」无法机械判定，交给 Skill 与用户确认。

    @param value: 主题短名称。
    @return: 校验通过的 slug。
    """
    slug = check_segment("slug", value)
    if slug.lower() == QUICK_DIR:
        raise StoryError("slug 'quick' 是 Quick 文档的保留名")
    return slug


def normalize_path(value):
    """把账本里的相对路径统一成正斜杠，因为 convention 规定 file 与 Review 路径只用正斜杠。

    @param value: 命令行传入的路径，可为空。
    @return: 反斜杠已替换为正斜杠的路径；空值原样返回。
    """
    return value.replace("\\", "/") if value else value


def check_status(status, allowed):
    """校验状态属于给定枚举。

    @param status: 待校验状态。
    @param allowed: 该账本允许的状态枚举。
    @return: 校验通过的状态。
    """
    if status not in allowed:
        raise StoryError(f"status 必须是 {' / '.join(allowed)} 之一，收到 {status!r}")
    return status


def transition(status, stack, target, restore):
    """计算一次状态变更后的 (status, prior_status)。

    进入 Review 中 / 阻塞时压栈当前状态；已处于 Review 中时复查不再压栈，避免栈里堆满同一状态。
    写入普通状态时清空栈；restore 弹出栈顶写回，栈空则报错而不是静默通过。

    @param status: 条目当前状态。
    @param stack: 当前 prior_status。
    @param target: 目标状态，restore 为真时忽略。
    @param restore: 是否恢复进入前状态。
    @return: (新状态, 新栈)，空栈表示应删除 prior_status。
    """
    stack = list(stack or [])
    if restore:
        if not stack:
            raise StoryError("prior_status 为空，没有可恢复的状态")
        return stack.pop(), stack
    if target in STACKING_STATUSES:
        if not (target == "Review 中" and status == "Review 中") and status:
            stack.append(status)
        return target, stack
    return target, []


def tokenize(query):
    """把检索式切成有效词元，丢弃单字与泛词，因为它们会让排序失去意义。

    @param query: 检索词列表。
    @return: 去重后的小写词元。
    """
    tokens = []
    for raw in re.split(r"[\s,，、;；/|]+", " ".join(query)):
        token = re.sub(r"\s+", "", raw).lower()
        if len(token) < 2 or token in GENERIC_TERMS or token in tokens:
            continue
        tokens.append(token)
    return tokens


def score_entry(entry, slug, tokens):
    """给条目打检索分，只用于排序：keywords 权重最高，标题全等高于包含。

    @param entry: 账本条目。
    @param slug: 主题名。
    @param tokens: 有效词元。
    @return: 得分，0 表示未命中。
    """
    title = re.sub(r"\s+", "", entry.get("title", "")).lower()
    keywords = [re.sub(r"\s+", "", str(word)).lower() for word in entry.get("keywords", [])]
    slug = slug.lower()
    score = 0
    for token in tokens:
        if token in keywords:
            score += 4
        elif any(token in word for word in keywords):
            score += 2
        if title == token:
            score += 3
        elif token in title:
            score += 2
        if token in slug:
            score += 1
    return score


def stack_note(stack):
    """把 prior_status 渲染成汇总行里的提示。

    @param stack: prior_status 列表。
    @return: 形如 ` (进入前: 已确认→阻塞)` 的文本，栈空时为空串。
    """
    return f" (进入前: {'→'.join(map(str, stack))})" if stack else ""


def entry_details(entry, fields):
    """把条目里有值的可选字段渲染成 ` 名=值`，列表用逗号连接。

    让 init 一次输出条目的完整信息，模型不必为了看 file、keywords 等字段去读 index.yaml。

    @param entry: 账本条目。
    @param fields: 按输出顺序列出的字段名。
    @return: 以空格开头的文本，没有任何字段有值时为空串。
    """
    text = ""
    for name in fields:
        value = entry.get(name)
        if value is None:
            continue
        text += f" {name}=" + (",".join(map(str, value)) if isinstance(value, list) else str(value))
    return text


# ── 命令 ─────────────────────────────────────────────────────────────────────


def cmd_init(root, args):
    """定位工作环境；写任何 .agent 文档之前先调用，缺失时只回报不代为创建。"""
    agent_exists = (root / ".agent").is_dir()
    ms_exists, current, milestones = load_milestones(root)
    slugs = list_slugs(root)
    print(f"cwd {root.as_posix()}")
    print(f"agent {'yes' if agent_exists else 'no'}")
    print(f"current {current or '-'}")
    print("milestones " + (" ".join(f"{name}({created or '-'})" for name, created in milestones.items()) or "-"))
    print("topics " + (" ".join(slugs) or "-"))
    if current:
        _, quick = load_quick(root, current)
        print(f"quick {current}: " + (", ".join(item["title"] for item in quick) or "-"))

    warnings = []
    if not agent_exists:
        warnings.append("工作目录下没有 .agent，先创建它再继续")
    elif not ms_exists:
        warnings.append(f"缺少 {MILESTONES_PATH}，需要确认当前 milestone 后创建")
    elif current not in milestones:
        warnings.append(f"milestones.yaml 的 current（{current or '空'}）不在 milestones 中")

    if args.slug is not None:
        slug = check_slug(args.slug)
        if slug not in slugs:
            warnings.append(f"没有正式主题 {slug}；现有主题：{' '.join(slugs) or '（无）'}")
        else:
            path, _, ledger = load_ledger(root, slug)
            base = f"{STORY_DIR}/{slug}"
            target = f"{base}/{current}" if current else "-"
            print(f"topic {slug} root={base} ledger={base}/index.yaml dir={target}")
            for item in ledger["items"]:
                print(f"{item['id']} {item['title']} {item['status']}"
                      + entry_details(item, ("file", "keywords", "continues", "continued_by", "design_review", "code_review")))
            for bug in ledger["bugs"]:
                print(f"bug{bug['id']} {bug['title']} {bug['status']}" + entry_details(bug, ("req", "file")))
    for warning in warnings:
        print(f"! {warning}")


def cmd_search(root, args):
    """在正式主题账本里检索需求点与 Bug；命中只作参考，不代表要续用某个主题。

    Bug 没有 keywords，只按标题和主题名打分；输出标签用 `slug/bugN` 与需求点区分。
    """
    tokens = tokenize(args.query)
    if not tokens:
        raise StoryError("检索式没有有效词元：单字与泛词不参与匹配，请给出更具体的主题词")
    if args.limit < 1:
        raise StoryError("--limit 必须是正整数")
    slugs = [check_slug(args.slug)] if args.slug else list_slugs(root)
    hits = []
    for slug in slugs:
        _, exists, ledger = load_ledger(root, slug)
        if not exists:
            continue
        for is_bug, entries in ((False, ledger["items"]), (True, ledger["bugs"])):
            for item in entries:
                if args.status and item.get("status") != args.status:
                    continue
                score = score_entry(item, slug, tokens)
                if score > 0:
                    hits.append((score, slug, is_bug, item))
    # 同分时按主题、需求在前 Bug 在后、编号排序，让同一主题的条目聚在一起。
    hits.sort(key=lambda hit: (-hit[0], hit[1], hit[2], hit[3]["id"]))
    if not hits:
        print("无命中")
        return
    for _, slug, is_bug, item in hits[:args.limit]:
        label = f"{slug}/bug{item['id']}" if is_bug else f"{slug}/{item['id']}"
        print(f"{label} {item.get('title', '')} "
              f"[{item.get('status', '')}·{item.get('milestone', '')}] {item.get('file', '-')}")
    if len(hits) > args.limit:
        print(f"! 共 {len(hits)} 条命中，仅显示前 {args.limit} 条")


def cmd_status(root, args):
    """按状态分组汇总账本，回答「做到哪了、有哪些阻塞」，避免逐份翻文档。"""
    rows = []  # (状态, 标签, 标题, 进入前栈)
    if args.kind != "quick":
        slugs = [check_slug(args.slug)] if args.slug else list_slugs(root)
        for slug in slugs:
            _, exists, ledger = load_ledger(root, slug)
            if not exists:
                continue
            for item in ledger["items"]:
                if args.milestone and item.get("milestone") != args.milestone:
                    continue
                rows.append((item.get("status", ""), f"{slug}/{item['id']}", item.get("title", ""), item.get("prior_status")))
            for bug in ledger["bugs"]:
                if args.milestone and bug.get("milestone") != args.milestone:
                    continue
                rows.append((bug.get("status", ""), f"{slug}/bug{bug['id']}", bug.get("title", ""), bug.get("prior_status")))
    if args.kind != "formal":
        _, current, _ = load_milestones(root)
        milestone = args.milestone or current
        if not milestone:
            raise StoryError("无法汇总 Quick：milestones.yaml 里没有 current milestone")
        _, quick = load_quick(root, milestone)
        rows.extend((item.get("status", ""), "quick", item["title"], None) for item in quick)
    if not rows:
        print("无条目")
        return
    groups = {}
    for status, label, title, stack in rows:
        groups.setdefault(status, []).append((label, title, stack))
    for status, entries in sorted(groups.items(), key=lambda pair: -len(pair[1])):
        print(f"{status} {len(entries)}")
        for label, title, stack in entries:
            print(f"  {label} {title}{stack_note(stack)}")


def cmd_milestone(root, args):
    """创建或切换 milestone；不创建目录，目录在写入第一份文档时按需生成。"""
    _, current, milestones = load_milestones(root)
    name = check_segment("name", args.name)
    if args.action == "create":
        if name in milestones:
            raise StoryError(f"milestone {name!r} 已存在于 {MILESTONES_PATH}")
        milestones[name] = datetime.date.today()
        if not args.no_switch or not current:
            current = name
        save_milestones(root, current, milestones)
        print(f"milestone {name} created current={current}")
    else:
        if name not in milestones:
            raise StoryError(f"milestone {name!r} 不存在于 {MILESTONES_PATH}，请先 create")
        save_milestones(root, name, milestones)
        print(f"current {name}")


def cmd_next_id(root, args):
    """取号并追加条目：计数器加一，编号只来自账本计数器，不扫描目录。"""
    slug = check_slug(args.slug)
    if not args.title.strip():
        raise StoryError("title 不能为空")
    if args.kind == "requirement" and args.req is not None:
        raise StoryError("--req 只适用于 bug")
    milestone = resolve_milestone(root, args.milestone)
    path, _, ledger = load_ledger(root, slug)
    allowed = BUG_STATUSES if args.kind == "bug" else REQUIREMENT_STATUSES
    status = check_status(args.status or ("已确认" if args.kind == "bug" else "待设计"), allowed)
    new_id = ledger[args.kind] + 1
    # 文档名（如 需求N_标题.md）依赖取号结果，因此 --file 里的 {id} 在这里替换，避免事后手改 file。
    file = normalize_path(args.file).replace("{id}", str(new_id)) if args.file else None
    if args.kind == "bug":
        ledger["bugs"].append(canonical({
            "id": new_id, "title": args.title, "req": args.req,
            "milestone": milestone, "status": status, "file": file,
        }, BUG_KEY_ORDER))
    else:
        ledger["items"].append(canonical({
            "id": new_id, "title": args.title,
            "milestone": milestone, "status": status, "file": file,
        }, ITEM_KEY_ORDER))
    ledger[args.kind] = new_id
    save_ledger(path, ledger)
    print(f"{args.kind} {new_id} {slug} {status}" + (f" {file}" if file else ""))


def parse_keywords(text):
    """把逗号分隔的 keywords 解析成去重列表；空串表示删除该字段。"""
    words = []
    for word in re.split(r"[,，]", text):
        word = word.strip()
        if word and word not in words:
            words.append(word)
    return words


def cmd_set_status(root, args):
    """更新条目状态、keywords 与 Review 路径；quick 还可用 --create 新增条目。

    只校验枚举，不判断流转是否符合工作流，门禁由 Skill 负责。
    """
    if args.restore and args.status:
        raise StoryError("--restore 与 --status 互斥")
    if args.create and args.kind != "quick":
        raise StoryError("--create 只适用于 quick")
    has_extra = args.keywords is not None or args.review_kind or args.review_path or args.clear_review
    if not args.restore and not args.status and not has_extra and not args.create:
        raise StoryError("至少给出 --status、--restore、--keywords、--review-*、--clear-review 或 --create 之一")
    if bool(args.review_kind) != bool(args.review_path):
        raise StoryError("--review-kind 与 --review-path 必须同时给出")

    if args.kind == "quick":
        set_quick_status(root, args, has_extra)
        return

    if args.keywords is not None and args.kind != "requirement":
        raise StoryError("--keywords 只适用于 requirement")
    if (args.review_kind or args.clear_review) and args.kind != "requirement":
        raise StoryError("Review 路径字段只适用于 requirement")
    if not args.slug or args.id is None:
        raise StoryError(f"kind {args.kind} 需要 --slug 与 --id")
    slug = check_slug(args.slug)
    path, exists, ledger = load_ledger(root, slug)
    if not exists:
        raise StoryError(f"{path} 不存在，请先用 next-id 建立条目")
    is_bug = args.kind == "bug"
    entries = ledger["bugs"] if is_bug else ledger["items"]
    order = BUG_KEY_ORDER if is_bug else ITEM_KEY_ORDER
    index = next((i for i, entry in enumerate(entries) if entry["id"] == args.id), None)
    if index is None:
        raise StoryError(f"{path} 中没有 {args.kind} {args.id}")

    entry = dict(entries[index])
    if args.restore or args.status:
        target = None if args.restore else check_status(args.status, BUG_STATUSES if is_bug else REQUIREMENT_STATUSES)
        entry["status"], entry["prior_status"] = transition(
            entry.get("status", ""), entry.get("prior_status"), target, args.restore)
    if args.keywords is not None:
        entry["keywords"] = parse_keywords(args.keywords)
    if args.clear_review:
        entry.pop("design_review", None)
        entry.pop("code_review", None)
    if args.review_kind:
        entry["design_review" if args.review_kind == "design" else "code_review"] = normalize_path(args.review_path)
    entries[index] = canonical(entry, order)
    save_ledger(path, ledger)

    final = entries[index]
    label = f"bug{args.id}" if is_bug else str(args.id)
    print(f"{slug}/{label} {final['status']}{stack_note(final.get('prior_status'))}")


def set_quick_status(root, args, has_extra):
    """更新或新增 Quick 条目；Quick 只有 title 与 status，因此拒绝其他写入。

    新增时状态缺省为 待确认：Quick 的范围需要先与用户确认。
    """
    if args.restore or has_extra:
        raise StoryError("Quick 条目只有 title 与 status，只支持 --status 与 --create")
    if not args.title or not args.title.strip():
        raise StoryError("kind quick 需要 --title")
    milestone = resolve_milestone(root, args.milestone)
    path, items = load_quick(root, milestone)
    item = next((item for item in items if item["title"] == args.title), None)
    if args.create:
        if item is not None:
            raise StoryError(f"{path} 中已有标题为 {args.title!r} 的 Quick 条目")
        item = {"title": args.title}
        items.append(item)
    elif item is None:
        raise StoryError(f"{path} 中没有标题为 {args.title!r} 的 Quick 条目")
    elif not args.status:
        raise StoryError("kind quick 需要 --status")
    item["status"] = check_status(args.status or "待确认", QUICK_STATUSES)
    write_yaml(path, {"items": items})
    print(f"quick {args.title} {item['status']}")


# ── 入口 ─────────────────────────────────────────────────────────────────────


class _Parser(argparse.ArgumentParser):
    """让命令行用法错误与业务错误使用同一通道：`error: 原因` 加退出码 1，而不是 argparse 默认的退出码 2。"""

    def error(self, message):
        self.exit(1, f"error: {message}\n")


def build_parser():
    """构建命令行解析器；子命令解析器沿用 _Parser。"""
    parser = _Parser(prog="story.py", description="story-lite-new 账本脚本")
    parser.add_argument("--cwd", help="工作目录，默认当前目录；.agent 固定在其根部")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="定位工作环境，可选给出 slug 定位已有主题")
    p.add_argument("slug", nargs="?")

    p = sub.add_parser("search", help="检索正式主题的需求点")
    p.add_argument("query", nargs="+")
    p.add_argument("--slug")
    p.add_argument("--status")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("status", help="按状态分组汇总")
    p.add_argument("--kind", choices=["formal", "quick", "all"], default="formal")
    p.add_argument("--slug")
    p.add_argument("--milestone")

    p = sub.add_parser("milestone", help="创建或切换 milestone")
    p.add_argument("action", choices=["create", "use"])
    p.add_argument("name")
    p.add_argument("--no-switch", action="store_true", help="create 时不切换 current")

    p = sub.add_parser("next-id", help="取号并追加条目")
    p.add_argument("slug")
    p.add_argument("kind", choices=["requirement", "bug"])
    p.add_argument("title")
    p.add_argument("--milestone")
    p.add_argument("--status", help="requirement 默认 待设计，bug 默认 已确认")
    p.add_argument("--file", help="文档相对主题根的路径，其中的 {id} 替换为新编号")
    p.add_argument("--req", type=int, help="仅 bug：关联需求点编号，无关联时省略")

    p = sub.add_parser("set-status", help="更新状态、keywords、Review 路径")
    p.add_argument("--kind", required=True, choices=["requirement", "bug", "quick"])
    p.add_argument("--slug")
    p.add_argument("--id", type=int)
    p.add_argument("--title", help="仅 quick：以标题定位条目")
    p.add_argument("--milestone", help="仅 quick：省略取 current")
    p.add_argument("--status")
    p.add_argument("--create", action="store_true", help="仅 quick：新增条目，状态缺省为 待确认")
    p.add_argument("--restore", action="store_true", help="弹出 prior_status 栈顶写回 status")
    p.add_argument("--keywords", help="逗号分隔，整体替换；空串删除该字段")
    p.add_argument("--review-kind", choices=["design", "code"])
    p.add_argument("--review-path")
    p.add_argument("--clear-review", action="store_true", help="删除 design_review 与 code_review，历史报告文件保留")
    return parser


COMMANDS = {
    "init": cmd_init, "search": cmd_search, "status": cmd_status,
    "milestone": cmd_milestone, "next-id": cmd_next_id, "set-status": cmd_set_status,
}


# 会写账本的命令；它们要求 .agent 目录已存在。
WRITE_COMMANDS = ("milestone", "next-id", "set-status")


def main(argv=None):
    """执行命令并把 StoryError 与文件系统错误转成 stderr 错误与退出码 1。

    @param argv: 参数列表，默认取 sys.argv。
    @return: 进程退出码。
    """
    # Windows 控制台默认编码会破坏中文输出，统一按 UTF-8。
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    root = Path(args.cwd or os.getcwd()).resolve()
    try:
        # .agent 的位置由用户确认，写命令不能借创建文件之名顺带建出它。
        if args.command in WRITE_COMMANDS and not (root / ".agent").is_dir():
            raise StoryError(f"{root / '.agent'} 不存在，请先创建 .agent 目录（脚本不代为创建）")
        COMMANDS[args.command](root, args)
    except (StoryError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
