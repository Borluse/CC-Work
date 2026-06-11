---
name: story-story
description: "整理清理需求文档。TRIGGER: 当用户说'整理需求'、'清理需求文档'、'生成slug'、'整理原始需求'时使用。"
---

- **前置**：加载 `${CLAUDE_SKILL_DIR}/../common/basic.md`（同会话已读则跳过）。

根据用户提供的需求内容：
1. 清理格式
2. 去除无用内容（无效贴图链接等）。
3. 生成 slug 候选，按 `basic.md`「Slug 检索流程」查重：
   - 命中已有 slug：询问追加还是另起新名。
   - 未命中：与用户确认 slug 名称。
4. 将整理后内容写入 current milestone 下 slug 目录的 `原始需求.md`。
