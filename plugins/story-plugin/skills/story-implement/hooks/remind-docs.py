#!/usr/bin/env python3
"""PostToolUse hook: 通知模型在 Edit/Write 后更新需求文档。"""
import json
import sys
import os


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    cwd = data.get("cwd", os.getcwd())
    tool_name = data.get("tool_name", "")

    # 跳过 doc 文件自身的编辑
    if file_path.endswith((".md", ".MD")):
        sys.exit(0)

    # 跳过无意义的临时/配置路径
    skip_dirs = {"node_modules", ".git", "__pycache__", ".codebuddy"}
    if any(p in skip_dirs for p in file_path.replace("\\", "/").split("/")):
        sys.exit(0)

    # 无 story 目录则跳过
    story_dir = os.path.join(cwd, ".agent", "story")
    if not os.path.isdir(story_dir):
        sys.exit(0)

    # 构建上下文提醒
    rel_path = file_path
    if file_path.startswith(cwd):
        rel_path = os.path.relpath(file_path, cwd)

    reminder = (
        f"[文档同步提醒] 已 {tool_name} 文件: {rel_path}。"
        "请检查 .agent/story/ 下相关需求/设计文档是否需要更新，保持文档与代码一致。"
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": reminder,
        }
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
