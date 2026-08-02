#!/usr/bin/env python3
"""p4-hook-install：把 p4 编辑 hook 安装/卸载到指定项目目录（幂等、可逆）。

安装：install.py install <目标目录> [--cursor]
卸载：install.py uninstall <目标目录> [--cursor]
"""

import argparse
import difflib
import json
import os
import shutil
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL_DIR, "assets")
PYTHON = "/usr/bin/python3"
PLACEHOLDER = "__PROJECT_ROOT__"
HOOK_SCRIPT_NAME = "p4-edit-hook.py"


def asset(name):
    return os.path.join(ASSETS, name)


def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"[p4-hook-install] 无法解析 {path}: {exc}")


def render(template_name, project_root):
    with open(asset(template_name), "r", encoding="utf-8") as f:
        text = f.read()
    return text.replace(PLACEHOLDER, project_root)


def diff_text(old, new, path):
    lines = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"{path} (旧)",
        tofile=f"{path} (新)",
    )
    return "".join(lines)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    old = None
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            old = f.read()
    if old == text:
        return False
    if old is not None:
        print(diff_text(old, text, path))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    with open(tmp, "r", encoding="utf-8") as f:
        json.load(f)  # 回读校验，保证产物可解析
    os.replace(tmp, path)
    print(f"[p4-hook-install] 写入 {path}")
    return True


def copy_script(project_root, rel_dir):
    dest_dir = os.path.join(project_root, rel_dir)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, HOOK_SCRIPT_NAME)
    src = asset(HOOK_SCRIPT_NAME)
    with open(src, "r", encoding="utf-8") as f:
        src_text = f.read()
    if os.path.exists(dest):
        with open(dest, "r", encoding="utf-8") as f:
            if f.read() == src_text:
                return False
    shutil.copy2(src, dest)
    os.chmod(dest, 0o755)
    print(f"[p4-hook-install] 写入 {dest}")
    return True


def upsert_entry(entries, entry):
    matcher = entry.get("matcher")
    for i, existing in enumerate(entries):
        if existing.get("matcher") == matcher:
            if existing == entry:
                return False
            entries[i] = entry
            return True
    entries.append(entry)
    return True


def codex_entry(project_root):
    data = json.loads(render("hooks.codex.json", project_root))
    return data["hooks"]["PreToolUse"][0]


def claude_entry(project_root):
    data = json.loads(render("settings.claude.json", project_root))
    return data["hooks"]["PreToolUse"][0]


def cursor_entry(project_root):
    data = json.loads(render("cursor.hooks.json", project_root))
    return data["hooks"]["preToolUse"][0]


def install(project_root, with_cursor):
    written = []
    if copy_script(project_root, os.path.join(".codex", "hooks")):
        written.append(os.path.join(project_root, ".codex", "hooks", HOOK_SCRIPT_NAME))

    codex_path = os.path.join(project_root, ".codex", "hooks.json")
    codex_data = load_json(codex_path)
    if codex_data is None:
        codex_data = json.loads(render("hooks.codex.json", project_root))
        write_json(codex_path, codex_data)
        written.append(codex_path)
    else:
        codex_data.setdefault("hooks", {})
        entries = codex_data["hooks"].setdefault("PreToolUse", [])
        if upsert_entry(entries, codex_entry(project_root)):
            write_json(codex_path, codex_data)
            written.append(codex_path)

    claude_path = os.path.join(project_root, ".claude", "settings.json")
    claude_data = load_json(claude_path)
    if claude_data is None:
        claude_data = json.loads(render("settings.claude.json", project_root))
        write_json(claude_path, claude_data)
        written.append(claude_path)
    else:
        claude_data.setdefault("hooks", {})
        entries = claude_data["hooks"].setdefault("PreToolUse", [])
        if upsert_entry(entries, claude_entry(project_root)):
            write_json(claude_path, claude_data)
            written.append(claude_path)

    if with_cursor:
        if copy_script(project_root, os.path.join(".cursor", "hooks")):
            written.append(os.path.join(project_root, ".cursor", "hooks", HOOK_SCRIPT_NAME))
        cursor_path = os.path.join(project_root, ".cursor", "hooks.json")
        cursor_data = load_json(cursor_path)
        if cursor_data is None:
            cursor_data = json.loads(render("cursor.hooks.json", project_root))
            write_json(cursor_path, cursor_data)
            written.append(cursor_path)
        else:
            cursor_data.setdefault("hooks", {})
            entries = cursor_data["hooks"].setdefault("preToolUse", [])
            if upsert_entry(entries, cursor_entry(project_root)):
                write_json(cursor_path, cursor_data)
                written.append(cursor_path)

    if written:
        print(f"[p4-hook-install] 安装完成，共写入 {len(written)} 项：")
        for path in written:
            print(f"  - {path}")
    else:
        print("[p4-hook-install] 已是最新，无变更（幂等）。")
    print(
        "[p4-hook-install] 信任说明：Codex 需在 /hooks 审查信任；"
        "Claude Code 首次运行可能弹审批（已预置 permission: allow）。"
    )


def is_managed_entry(entry, markers):
    # Cursor 形态：{"command": ..., "matcher": ...}（command 在顶层）
    command = entry.get("command")
    if isinstance(command, str) and any(marker in command for marker in markers):
        return True
    # Claude Code / Codex 形态：{"matcher": ..., "hooks": [{"command": ...}]}
    for hook in entry.get("hooks", []):
        if not isinstance(hook, dict):
            continue
        command = hook.get("command", "")
        if any(marker in command for marker in markers):
            return True
    return False


def managed_markers(project_root):
    return [
        os.path.join(project_root, ".codex", "hooks", HOOK_SCRIPT_NAME),
        os.path.join(project_root, ".cursor", "hooks", HOOK_SCRIPT_NAME),
    ]


def uninstall_config(path, event_key, markers):
    """从配置文件中移除本技能管理的 hook 条目；文件清理规则见注释。"""
    data = load_json(path)
    if data is None:
        return
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return
    entries = hooks.get(event_key) or []
    kept = [e for e in entries if not is_managed_entry(e, markers)]
    if len(kept) == len(entries):
        return  # 没有本技能写入的条目
    if kept:
        hooks[event_key] = kept
        write_json(path, data)
        return
    hooks.pop(event_key, None)
    if hooks:
        write_json(path, data)
        return
    data.pop("hooks", None)
    # Cursor 配置可能只剩 {"version": 1}，视为空，删除文件
    if data and set(data.keys()) - {"version"}:
        write_json(path, data)
    else:
        os.remove(path)
        print(f"[p4-hook-install] 删除 {path}")
        try:
            os.rmdir(os.path.dirname(path))
        except OSError:
            pass


def remove_script(project_root, rel_dir):
    script = os.path.join(project_root, rel_dir, HOOK_SCRIPT_NAME)
    if os.path.exists(script):
        os.remove(script)
        print(f"[p4-hook-install] 删除 {script}")
        # 逐级清理空的父目录（hooks/ -> .codex/ -> 项目根为止）
        parent = os.path.dirname(script)
        while parent != project_root and os.path.isdir(parent):
            try:
                os.rmdir(parent)
            except OSError:
                break
            parent = os.path.dirname(parent)


def uninstall(project_root, with_cursor):
    markers = managed_markers(project_root)
    uninstall_config(
        os.path.join(project_root, ".codex", "hooks.json"),
        "PreToolUse",
        markers,
    )
    uninstall_config(
        os.path.join(project_root, ".claude", "settings.json"),
        "PreToolUse",
        markers,
    )
    remove_script(project_root, os.path.join(".codex", "hooks"))
    if with_cursor:
        uninstall_config(
            os.path.join(project_root, ".cursor", "hooks.json"),
            "preToolUse",
            markers,
        )
        remove_script(project_root, os.path.join(".cursor", "hooks"))
    print("[p4-hook-install] 卸载完成。")


def main():
    parser = argparse.ArgumentParser(description="p4 edit hook 安装/卸载工具")
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("install", "uninstall"):
        p = sub.add_parser(action)
        p.add_argument("target", help="目标项目目录")
        p.add_argument("--cursor", action="store_true", help="同时安装/卸载 Cursor hook")
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.expanduser(args.target))
    if not os.path.isdir(project_root):
        raise SystemExit(f"[p4-hook-install] 目录不存在: {project_root}")
    if not os.access(project_root, os.W_OK):
        raise SystemExit(f"[p4-hook-install] 目录不可写: {project_root}")

    if args.action == "install":
        install(project_root, args.cursor)
    else:
        uninstall(project_root, args.cursor)


if __name__ == "__main__":
    main()
