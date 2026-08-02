#!/usr/bin/env python3
"""PreToolUse hook：编辑文件前尝试 `p4 edit` 解锁（best-effort）。

兼容 Codex apply_patch 与 Claude Code Write/Edit/MultiEdit 的 stdin 形态。
任何失败都只向 stderr 告警并 exit 0，绝不阻断编辑。
"""

import json
import os
import re
import shutil
import subprocess
import sys

P4_CANDIDATES = [
    "/usr/local/bin/p4",
    "/opt/homebrew/bin/p4",
    os.path.expanduser("~/bin/p4"),
    "/Applications/p4v.app/Contents/Resources/p4",
]

PATCH_PATH_RE = re.compile(
    r"^\s*\*\*\*\s+(?:Add File|Update File|Delete File|Move to):\s*(.+?)\s*$",
    re.MULTILINE,
)


def warn(message):
    print(f"[p4-edit-hook] {message}", file=sys.stderr)


def parse_patch_paths(text):
    if not isinstance(text, str):
        return []
    return [m.group(1) for m in PATCH_PATH_RE.finditer(text)]


def scan_json_paths(obj, seen=None):
    """递归收集 file_path / path / paths 键的值（兼容 Cursor 等未知形态）。"""
    if seen is None:
        seen = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in ("file_path", "path") and isinstance(value, str) and value:
                seen.append(value)
            elif key == "paths" and isinstance(value, list):
                seen.extend(p for p in value if isinstance(p, str) and p)
            else:
                scan_json_paths(value, seen)
    elif isinstance(obj, list):
        for item in obj:
            scan_json_paths(item, seen)
    return seen


def collect_paths(data):
    paths = set()
    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    if isinstance(file_path, str) and file_path:
        paths.add(file_path)
    patch = tool_input.get("command") or tool_input.get("patch") or tool_input.get("input")
    paths.update(parse_patch_paths(patch))
    paths.update(scan_json_paths(data))
    for env_name in ("CLAUDE_FILE_PATHS", "CLAUDE_FILE_PATH"):
        env_value = os.environ.get(env_name, "")
        if env_value:
            paths.update(env_value.split())
    return paths


def locate_p4():
    override = os.environ.get("CODEX_P4_HOOK_P4")
    if override and os.path.isfile(override) and os.access(override, os.X_OK):
        return override
    found = shutil.which("p4")
    if found:
        return found
    for candidate in P4_CANDIDATES:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def resolve_path(raw_path, cwd):
    if not os.path.isabs(raw_path):
        return os.path.normpath(os.path.join(cwd, raw_path))
    return os.path.normpath(raw_path)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError):
        sys.exit(0)

    cwd = data.get("cwd") or os.getcwd()
    paths = sorted(collect_paths(data))
    if not paths:
        sys.exit(0)

    p4 = locate_p4()
    if p4 is None:
        warn("未找到 p4，跳过解锁（请安装 p4 或设置 CODEX_P4_HOOK_P4）")

    for raw_path in paths:
        try:
            path = resolve_path(raw_path, cwd)
            if not os.path.exists(path) or os.access(path, os.W_OK):
                continue  # 新文件 / 已可写，无需解锁
            if p4 is None:
                continue
            proc = subprocess.run(
                [p4, "edit", path],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if proc.returncode != 0:
                detail = (proc.stderr or proc.stdout or "").strip()[:300]
                warn(f"p4 edit 失败: {path} — {detail}")
        except Exception as exc:  # noqa: BLE001 - hook 永不阻断
            warn(f"p4 edit 异常: {raw_path} — {exc}")
            continue

    sys.exit(0)


if __name__ == "__main__":
    main()
