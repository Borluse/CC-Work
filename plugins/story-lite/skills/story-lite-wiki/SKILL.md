---
name: story-lite-wiki
description: "从 story-lite 需求文档生成或迭代团队 Wiki。模式：export（从总览/设计导出精简 Wiki）、tdd（从原始需求按需求点讨论方案并写入 Wiki）。TRIGGER: 生成wiki、总结为wiki、写wiki文档、导出wiki、写TDD、讨论方案、从原始需求写wiki，或显式点名 story-lite-wiki。"
---

# 做什么

面向策划、程序与 QA 维护精简 Wiki；支持从已确认设计导出 Wiki，或从原始需求按需求点持续讨论方案。不改写 `story-lite` 主流程。

# 定位

独立 Wiki skill：靠 TRIGGER 与显式点名启用。模式用 reference 拆开，本文件只负责门禁与路由；命中模式后再读对应文件，禁止一次读完所有 reference。

# 约定

路径与访问边界与 `story-lite` 对齐。默认可跨 milestone 读取；默认只向用户确认的目标 Wiki 写入。

```
.agent/milestones.yaml
.agent/story/<slug>/原始需求.md
.agent/story/<slug>/总览.md
.agent/story/<slug>/index.yaml
.agent/story/<slug>/<milestone>/需求N_标题.md
.agent/story/<slug>/wiki/<标题>.md
.agent/story/<slug>/<标题>TDD.md
```

- `<cwd>`：当前工作目录；`.agent` 固定为 `<cwd>/.agent`。只直接访问该树。
- 解析 story 时忽略 `.agent/story/quick/`。
- 未指定 story 时沿用当前对话已确认的 `<slug_dir>`；仍不明则询问。
- 确认全部在普通对话中完成，禁止调用 `AskQuestion`。
- 文风：简洁、无冗余、禁止哲学说明、实事求是；只写已确认或源文档已有的内容。
- **Wiki 边界**：Wiki 不改需求状态；不占需求或 Bug 编号，不写入 `index.yaml` 账本，不参与正式 story 检索命中，不改 `index.yaml` 中的需求、Bug 或 Quick 状态。用户明确要求同步状态时除外。

# 模式路由

先完成 Phase 0，再按下表选模式。用户口头指定模式时以用户为准。命中模式后只读取「读取」列指定的 reference；写作前再按需读取 `WRITING.md`。

| 用户说法 | 模式 | 读取 |
|----------|------|------|
| 生成 wiki / 总结为 wiki / 写 wiki 文档 / 导出 wiki | `export` | [EXPORT.md](EXPORT.md) |
| 写 TDD / 讨论方案 / 从原始需求写 wiki / 按需求点写方案 | `tdd` | [TDD.md](TDD.md) |
| 合入历史 Wiki/TDD、挪章节 | `tdd`（维护） | [TDD.md](TDD.md) |

- 对话已在 `tdd` 且用户继续补某个需求点的方案：保持 `tdd`，不要切回 `export`。
- 用户明确说「从原始需求生成」时：不要走 `export` 的总览门禁，改走 `TDD.md`。

# Phase 0 门禁

1. 检查 `<cwd>/.agent` 与 `milestones.yaml`；缺失则提醒并停止。
2. 定位 `<slug_dir>`，展示工作目录、当前 milestone、slug 与主题根路径。
3. 宣布当前模式与将读取的 reference。
4. 完成门禁后进入对应模式文件；除当前模式和写作所需的 reference 外，不读取其他模式文件。
