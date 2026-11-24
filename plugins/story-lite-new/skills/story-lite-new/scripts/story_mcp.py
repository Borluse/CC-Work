#!/usr/bin/env python3
"""story-lite-new 的 MCP 服务（stdio）。

协议只实现 initialize、notifications/initialized、tools/list、tools/call 四种消息，
按 JSON-RPC 一行一条收发。工具调用把参数翻译成 `story.py` 的命令行参数后交给
`story_core`，因此参数校验、默认值和输出格式只有一处定义。

stdout 只写协议消息，日志与异常栈写 stderr。
"""

import contextlib
import io
import json
import os
import sys
import threading
import time
import traceback
from pathlib import Path

import story_core

# 协议版本必须属于客户端接受的范围，pi 的客户端支持到 2025-11-25。
PROTOCOL_VERSION = "2025-11-25"
SERVER_INFO = {"name": "story", "version": "1"}

# 空闲多久后主动退出：没有调用的会话不必一直抱着索引内存。
# 客户端在下次调用时会重新连接，代价是重新建一次索引。
IDLE_TIMEOUT_SECONDS = 30 * 60
IDLE_CHECK_SECONDS = 60

INSTRUCTIONS = (
    ".agent 文档库服务。init 定位项目与 milestone，search 检索账本条目，find 检索正文，"
    "status 汇总进度，next-id 取号，set-status 改状态，milestone 管理里程碑。"
    "所有工具接受可选 project（STORY_ROOTS 中的别名或项目根绝对路径），"
    "省略时使用服务进程的工作目录。"
)

# 每个工具统一的 project 参数说明。
PROJECT_SCHEMA = {
    "type": "string",
    "description": "项目根：STORY_ROOTS 中的别名，或项目根的绝对路径；省略时用服务进程的工作目录",
}


class ToolError(Exception):
    """工具执行失败：文本原样回给模型，并把结果标记为 isError。"""


# 各工具的必填参数；缺失时在调用前直接报错，避免落到 argparse 的用法提示。
REQUIRED = {
    "init": (),
    "search": ("query",),
    "find": ("query",),
    "status": (),
    "milestone": ("action", "name"),
    "next-id": ("slug", "kind", "title"),
    "set-status": ("kind",),
}

TOOLS = [
    {
        "name": "init",
        "description": "定位项目和当前 milestone，列出正式主题与 Quick；给出 slug 时输出该主题条目完整字段",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": PROJECT_SCHEMA,
                "slug": {"type": "string", "description": "主题短名称"},
            },
        },
    },
    {
        "name": "search",
        "description": "在正式主题账本里按标题与 keywords 检索需求点与 Bug，返回编号、状态和文档路径",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": PROJECT_SCHEMA,
                "query": {"type": "string", "description": "检索词，空格分隔"},
                "slug": {"type": "string", "description": "只检索该主题"},
                "status": {"type": "string", "description": "只保留该状态的条目"},
                "limit": {"type": "integer", "description": "最多返回条数，默认 10"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "find",
        "description": "在 .agent 的 md 正文里检索，命中按文件聚合，返回文件、标题层级、行号和片段",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": PROJECT_SCHEMA,
                "query": {"type": "string", "description": "检索词，空格分隔；大小写不敏感"},
                "slug": {"type": "string", "description": "只检索 story 下的该主题"},
                "milestone": {"type": "string", "description": "只检索路径中包含该 milestone 的文档"},
                "limit": {"type": "integer", "description": "最多返回文件数，默认 10"},
                "hits": {"type": "integer", "description": "每个文件最多显示的命中处数，默认 3"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "status",
        "description": "按状态分组汇总需求点与 Bug 的进度，回答做到哪了、有哪些阻塞",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": PROJECT_SCHEMA,
                "kind": {"type": "string", "enum": ["formal", "quick", "all"], "description": "汇总范围，默认 formal"},
                "slug": {"type": "string", "description": "只汇总该主题"},
                "milestone": {"type": "string", "description": "只汇总该 milestone"},
            },
        },
    },
    {
        "name": "milestone",
        "description": "创建或切换 milestone；create 遇到同名时报错而不覆盖",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": PROJECT_SCHEMA,
                "action": {"type": "string", "enum": ["create", "use"]},
                "name": {"type": "string", "description": "milestone 名"},
                "noSwitch": {"type": "boolean", "description": "create 时不切换 current"},
            },
            "required": ["action", "name"],
        },
    },
    {
        "name": "next-id",
        "description": "从账本计数器取号并追加条目，返回新编号；返回内容已写明编号，收到错误时先 init 核对再重试",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": PROJECT_SCHEMA,
                "slug": {"type": "string", "description": "主题短名称"},
                "kind": {"type": "string", "enum": ["requirement", "bug"]},
                "title": {"type": "string", "description": "条目标题"},
                "milestone": {"type": "string", "description": "省略时取 current"},
                "status": {"type": "string", "description": "requirement 默认 待设计，bug 默认 已确认"},
                "file": {"type": "string", "description": "文档相对主题根的路径，{id} 会替换为新编号"},
                "req": {"type": "integer", "description": "仅 bug：关联的需求点编号"},
            },
            "required": ["slug", "kind", "title"],
        },
    },
    {
        "name": "set-status",
        "description": "更新条目状态、keywords 与 Review 路径；quick 还可用 create 新增条目。重复执行结果相同，失败可直接重试",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": PROJECT_SCHEMA,
                "kind": {"type": "string", "enum": ["requirement", "bug", "quick"]},
                "slug": {"type": "string", "description": "requirement、bug 必填"},
                "id": {"type": "integer", "description": "requirement、bug 必填"},
                "title": {"type": "string", "description": "仅 quick：以标题定位条目"},
                "milestone": {"type": "string", "description": "仅 quick：省略取 current"},
                "status": {"type": "string", "description": "目标状态，按各账本的枚举校验"},
                "create": {"type": "boolean", "description": "仅 quick：新增条目"},
                "restore": {"type": "boolean", "description": "弹出 prior_status 栈顶写回，与 status 互斥"},
                "keywords": {"type": "string", "description": "仅 requirement：逗号分隔，整体替换；空串删除该字段"},
                "reviewKind": {"type": "string", "enum": ["design", "code"], "description": "与 reviewPath 同时给出"},
                "reviewPath": {"type": "string", "description": "Review 报告相对主题根的路径"},
                "clearReview": {"type": "boolean", "description": "删除两个 Review 路径字段，历史报告保留"},
            },
            "required": ["kind"],
        },
    },
]


def story_roots():
    """读取 STORY_ROOTS 环境变量中的别名映射。

    @return: {别名: 项目根路径}；未配置时为空映射。
    """
    raw = os.environ.get("STORY_ROOTS", "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ToolError(f"STORY_ROOTS 不是合法 JSON: {error}")
    if not isinstance(data, dict) or not all(isinstance(value, str) for value in data.values()):
        raise ToolError("STORY_ROOTS 必须是 别名 -> 项目根路径 的映射")
    return data


def resolve_project(name):
    """把 project 参数解析成项目根目录。

    @param name: STORY_ROOTS 中的别名、项目根绝对路径，或 None。
    @return: 项目根 Path。
    """
    roots = story_roots()
    if not name:
        root = Path(os.getcwd())
    elif name in roots:
        root = Path(roots[name])
    else:
        root = Path(name)
    if not (root / ".agent").is_dir():
        known = "、".join(sorted(roots)) or "（未配置）"
        raise ToolError(f"{root} 下没有 .agent；已配置的别名：{known}")
    return root


def require(arguments, *keys):
    """校验必填参数非空。

    @param arguments: 工具参数映射。
    @param keys: 必填参数名。
    """
    missing = [key for key in keys if not str(arguments.get(key) or "").strip()]
    if missing:
        raise ToolError("缺少参数: " + ", ".join(missing))


def build_argv(name, arguments, root):
    """把工具参数翻译成 story.py 的命令行参数。

    翻译后交给 story_core 的解析器，参数默认值与校验只有一处定义。

    @param name: 工具名。
    @param arguments: 工具参数映射。
    @param root: 项目根目录。
    @return: 参数列表。
    """
    argv = ["--cwd", str(root), name]

    if name == "init":
        if arguments.get("slug"):
            argv.append(str(arguments["slug"]))
        return argv

    if name in ("search", "find"):
        argv.append(str(arguments["query"]))
        options = (("slug", "--slug"), ("status", "--status"), ("milestone", "--milestone"),
                   ("limit", "--limit"), ("hits", "--hits"))
        for key, option in options:
            if arguments.get(key) is not None:
                argv += [option, str(arguments[key])]
        return argv

    if name == "status":
        for key, option in (("kind", "--kind"), ("slug", "--slug"), ("milestone", "--milestone")):
            if arguments.get(key) is not None:
                argv += [option, str(arguments[key])]
        return argv

    if name == "milestone":
        argv += [str(arguments["action"]), str(arguments["name"])]
        if arguments.get("noSwitch"):
            argv.append("--no-switch")
        return argv

    if name == "next-id":
        argv += [str(arguments["slug"]), str(arguments["kind"]), str(arguments["title"])]
        for key, option in (("milestone", "--milestone"), ("status", "--status"),
                            ("file", "--file"), ("req", "--req")):
            if arguments.get(key) is not None:
                argv += [option, str(arguments[key])]
        return argv

    if name == "set-status":
        argv += ["--kind", str(arguments["kind"])]
        for key, option in (("slug", "--slug"), ("id", "--id"), ("title", "--title"),
                            ("milestone", "--milestone"), ("status", "--status"),
                            ("keywords", "--keywords"), ("reviewKind", "--review-kind"),
                            ("reviewPath", "--review-path")):
            if arguments.get(key) is not None:
                argv += [option, str(arguments[key])]
        for key, option in (("create", "--create"), ("restore", "--restore"), ("clearReview", "--clear-review")):
            if arguments.get(key):
                argv.append(option)
        return argv

    raise ToolError(f"未知工具 {name}")


def run_tool(name, arguments):
    """执行一个工具，返回要回给模型的文本。

    命令实现写的是 stdout，出错写 stderr 并返回非零退出码；两者都捕获，
    失败时合并成 `error:` 文本交给调用方标记 isError。

    @param name: 工具名。
    @param arguments: 工具参数映射。
    @return: 命令输出文本。
    """
    root = resolve_project(arguments.get("project"))
    argv = build_argv(name, arguments, root)
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = story_core.main(argv)
        except SystemExit as request:  # 用法错误由解析器直接退出
            code = request.code if isinstance(request.code, int) else 1
    text = (out.getvalue() + err.getvalue()).strip()
    if code != 0:
        raise ToolError(text or f"命令以退出码 {code} 结束且没有输出")
    return text


def reply(request_id, result):
    """组装 JSON-RPC 成功响应。

    @param request_id: 请求 id。
    @param result: 结果对象。
    @return: 响应字典。
    """
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def fail(request_id, code, message):
    """组装 JSON-RPC 错误响应。

    @param request_id: 请求 id。
    @param code: JSON-RPC 错误码。
    @param message: 错误说明。
    @return: 响应字典。
    """
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(request):
    """处理一条消息。

    @param request: 解析后的 JSON-RPC 消息。
    @return: 响应字典；收到通知时返回 None。
    """
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        return reply(request_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
            "instructions": INSTRUCTIONS,
        })
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return reply(request_id, {"tools": TOOLS})
    if method == "tools/call":
        params = request.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        try:
            if name not in REQUIRED:
                raise ToolError(f"未知工具 {name}")
            require(arguments, *REQUIRED[name])
            text = run_tool(name, arguments)
            return reply(request_id, {"content": [{"type": "text", "text": text}]})
        except ToolError as error:
            return reply(request_id, {"content": [{"type": "text", "text": f"error: {error}"}], "isError": True})
        except Exception:  # 未预期异常：栈进 stderr，结果仍然回给模型
            traceback.print_exc(file=sys.stderr)
            return reply(request_id, {
                "content": [{"type": "text", "text": "error: 服务内部错误，详见服务端 stderr"}],
                "isError": True,
            })
    if request_id is not None:
        return fail(request_id, -32601, f"unknown method {method}")
    return None


def send(message):
    """把一条消息写回 stdout。

    @param message: JSON 可序列化的对象。
    """
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def idle_timeout():
    """读取空闲退出时长，可由 STORY_IDLE_TIMEOUT 覆盖，0 表示不退出。

    值非法时保留默认值并写 stderr，配置写错不应阻止服务启动。

    @return: 秒数。
    """
    raw = os.environ.get("STORY_IDLE_TIMEOUT", "").strip()
    if not raw:
        return float(IDLE_TIMEOUT_SECONDS)
    try:
        return max(0.0, float(raw))
    except ValueError:
        print(f"warning: STORY_IDLE_TIMEOUT={raw!r} 不是数字，改用默认 {IDLE_TIMEOUT_SECONDS} 秒",
              file=sys.stderr, flush=True)
        return float(IDLE_TIMEOUT_SECONDS)


def start_idle_watchdog(state):
    """启动空闲退出看门狗。

    看门狗只写 stderr，stdout 留给主线程写协议消息，避免两条线程交错破坏消息。

    @param state: 单元素列表，state[0] 是最近一次收到消息的 monotonic 时间戳。
    """
    timeout = idle_timeout()
    if timeout <= 0:
        return

    def watch():
        interval = min(IDLE_CHECK_SECONDS, timeout)
        while True:
            time.sleep(interval)
            if time.monotonic() - state[0] >= timeout:
                print(f"idle for {timeout:.0f}s, exiting", file=sys.stderr, flush=True)
                # 主线程可能阻塞在读 stdin 上，用 _exit 直接结束进程。
                os._exit(0)

    threading.Thread(target=watch, name="idle-watchdog", daemon=True).start()


def main():
    """从 stdin 逐行读消息，处理并写回 stdout。

    @return: 进程退出码。
    """
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    state = [time.monotonic()]
    start_idle_watchdog(state)
    for line in sys.stdin:
        state[0] = time.monotonic()
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as error:
            print(f"error: 无法解析消息: {error}", file=sys.stderr)
            continue
        if not isinstance(request, dict):
            continue
        response = handle(request)
        if response is not None:
            send(response)
    return 0


if __name__ == "__main__":
    sys.exit(main())
