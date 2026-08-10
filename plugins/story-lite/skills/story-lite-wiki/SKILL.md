---
name: story-lite-wiki
description: "从 story-lite 需求/设计/总览文档生成面向团队的精简 Wiki。TRIGGER: 当用户说'生成wiki'、'总结为wiki'、'写wiki文档'、'导出wiki'，或显式点名 story-lite-wiki 时使用。"
---

# 定位

独立 Wiki 生成 skill：从正式需求文档提炼面向策划/程序/QA 的精简 Wiki。不改写 `story-lite` 主流程；靠本 skill 的 TRIGGER 与显式点名启用。

# 约定

路径与访问边界与 `story-lite` 约定对齐；冲突以主技能为准。下列为本 skill 自用子集。

```
.agent/milestones.yaml
.agent/story/<milestone>/Archive/
.agent/story/<milestone>/quick/YYYY-MM-DD_任务短语.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/原始需求.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/需求N_标题.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/总览.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/wiki/<标题>.md
```

- `<cwd>`：当前工作目录；`.agent` 固定为 `<cwd>/.agent`，只直接访问该树，禁止扫描其他目录的 `.agent`。路径不存在时停止并提醒在当前工作目录根部创建
- `Archive/`：若存在则忽略，不碰触；解析 story 时忽略各 milestone 下全部 `quick/`
- **代码核实**：允许按入口函数/类名/文件路径线索核实当前工程代码；**默认派子任务检索**，主 agent 只消费结论；已知精确路径的单文件可读可主 agent 直接读。不因此放开对其它目录 `.agent` 的扫描
- **触发**：用户显式点名本 skill，或说「生成wiki / 总结为wiki / 写wiki文档 / 导出wiki」时执行
- **输入默认**：
  - 用户指定 story 时，在 `<cwd>/.agent/story/` 下跨 milestone 解析对应 `<slug_dir>`（`Archive/`、`quick/` 见上）
  - 未指定时优先沿用当前对话已确认的 `<slug_dir>`；仍不明则询问
- **确认**：全部在普通对话中完成，禁止调用 `AskQuestion` 或同类提问工具
- **读者与文风**：项目组成员（策划、程序、QA）；语言简洁、无冗余、禁止哲学说明、实事求是

# 流程

## Phase 0 门禁

1. 检查 `<cwd>/.agent` 与 `milestones.yaml`；缺失则提醒创建/配置并停止。
2. 读取 `current` milestone；向用户展示工作目录与 milestone。
3. 定位目标 `<slug_dir>`（见约定「输入默认」）。

## Phase 1 定位源文档

1. 判断多点 / 单点：
   - **多需求点**（存在 `总览.md` 或明确多份设计文档且以总览为准）：读 `总览.md`；缺失 → 提示先走 story-lite「整合」，结束。
   - **单需求点**：无总览时读 `需求N_*.md`；设计文档也缺失 → 提示先补设计/整合，结束。
2. 摘要源范围与可提取主题，**必须**经用户确认后再进入 Phase 2。

## Phase 2 确认输出结构

向用户确认 Wiki 章节。默认结构：

1. **需求简介** — 一段话概述系统做什么、核心状态/模式
2. **功能说明** — 每个子功能用文字 + mermaid 图辅助：
   - 触发条件与判定逻辑
   - 关键参数与可选模式
   - 边界条件处理
   - 性能考虑
   - 网络同步方案
3. **配置方法** — ConfigData 属性表、触发配置、CVar 表、调试绘制说明（源文档有则写）

用户可增删章节。**必须**确认后再进入 Phase 3。同时确认 Wiki 标题（系统名或短名）。

## Phase 3 生成文档

### 写作原则

- 每个功能先 1~3 句描述做什么/怎么触发/核心逻辑，再用图表辅助
- 前置条件用文字串联，不用列表堆砌
- 判定逻辑用 mermaid flowchart，时序用 sequenceDiagram，参数/配置用表格
- mermaid 节点文本要短：缩写或中文概括
- **禁止伪代码**：所有逻辑用 mermaid 图或文字描述
- **禁止哲学说明**
- **不含实现文件列表**
- **实事求是**：只写源文档中有的内容

### 格式规范

- 一级标题：系统名称
- 二级标题：章节编号 + 名称（如 `## 1. 需求简介`）
- 三/四级标题：子功能编号 + 名称
- 章节间用 `---` 分隔
- 表格对齐，mermaid 标注语言

## Phase 4 写入文档

- 输出路径：`<slug_dir>/wiki/<标题>.md`；必要时创建 `wiki/` 目录
- 已存在同名文件 → 询问覆盖还是新建（新建可加后缀）
- 写完后提醒用户打开确认
