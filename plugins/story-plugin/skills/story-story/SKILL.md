---
name: story-story
description: 整理清理需求文档
---

- **前置**：加载 `${CLAUDE_SKILL_DIR}/../common/basic.md`（同会话已读则跳过）。

根据用户提供的需求内容，作如下事情
1. 清理格式
2. 去除无用的内容，如无效的贴图链接等。
3. 生成一个 slug 候选，按 `basic.md` 的「Slug 检索流程」查重：
   - 命中已有 slug：询问用户是追加到已有 slug 还是另起新名。
   - 未命中：与用户确认 slug 名称。
4. 将整理后的内容写入到 current milestone 下的 slug 目录的 `原始需求.md`。
