---
name: story-story
description: "整理清理需求文档。TRIGGER: 当用户说'整理需求'、'清理需求文档'、'生成slug'、'整理原始需求'时使用。"
---

### Phase 0: 初始化环境
先调用 `/story-init`（**create-slug 模式**）完成工作环境初始化。
- **门禁**：`/story-init` 完成后方可继续，若已执行则跳过。

### Phase 1: 整理需求
根据用户提供的需求内容：
1. 清理格式
2. 去除无用内容（无效贴图链接等）。
3. 将整理后内容写入 `<slug_dir>/原始需求.md`。
