---
name: story-lite-learn
description: "从 story-lite 需求上下文、Bug 报告与核实源中提炼可跨需求复用的知识，经预览确认后写入 .agent/library。在本会话已显式启用 story-lite 且正式需求完成、Bug 验证关闭或发现值得沉淀的知识时由主技能委托；用户显式点名 story-lite-learn，或说提炼方法论、沉淀经验、写入 library 时也使用。"
---

# 定位

独立知识沉淀 skill：识别、核实、去重并写入 library。story-lite 只判触发时机并委托本 skill，不内嵌提炼/写入规则。

# 约定

路径与访问边界与 `story-lite` 约定对齐；冲突以主技能为准。下列为 learn 自用子集。

```
.agent/library/overall.md
.agent/library/<主题>.md
.agent/story/<milestone>/Archive/
.agent/story/<milestone>/quick/YYYY-MM-DD_任务短语.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/原始需求.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/需求N_标题.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/总览.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/bug/BugN_标题.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/review/需求N_标题_设计review.md
.agent/story/<milestone>/<YYYY-MM-DD_slug>/review/需求N_标题_代码review.md
```

- `<cwd>`：当前工作目录；`.agent` 固定为 `<cwd>/.agent`，只直接访问该树，禁止扫描其他目录的 `.agent`。路径不存在时停止并提醒在当前工作目录根部创建
- `Archive/`：若存在则忽略，不碰触；解析 story 时忽略各 milestone 下全部 `quick/`
- **代码核实**：允许在当前工程内按入口函数/类名/文件路径线索用 `rg`/`fd` 检索；不因此放开对其它目录 `.agent` 的扫描
- **触发**：
  - story-lite 委托（正式需求完成、Bug 验证关闭且存在可复用知识、或用户路由「沉淀 / 提炼方法论 / 写入 library」）时执行
  - 用户显式点名本 skill，或说「提炼方法论 / 沉淀经验 / 写入 library」时执行
  - 未启用 story-lite 且用户未点名（含同义触发）时，不主动执行
- **输入默认**：
  - 由 story-lite 委托且已有上下文时，沿用其 `<slug_dir>`
  - 用户点名且未指定 story 时，默认仅用当前对话
  - 用户指定 story 时，在 `<cwd>/.agent/story/` 下跨 milestone 解析对应 `<slug_dir>`（`Archive/`、`quick/` 见上）
- **确认**：全部在普通对话中完成，禁止调用 `AskQuestion` 或同类提问工具

# 提炼规则

- 使用中文
- 只保留可跨需求复用的模式、约束与搜索线索；需求特有逻辑不提取
- **厚度**：每条 ≤1–2 句原则（方法论/指引）+ 一条核实线索；流程步骤、选项枚举、禁令原文、表格字段等执行细则留在 skill，不写入 library
- 采用「职责描述 + 入口函数名/类名/文件路径」的线索形式，不罗列完整 API 签名与参数清单
- 从对话和 story 文档收集候选知识，并按核实源核对；未实现方案、无法验证的推断不写入
- **核实源**：业务行为以代码为准；Skill/约定类知识以对应 skill 或约定文档为准，并标明核实线索

# 流程

## 1. 收集与核实

1. 读取当前对话上下文。
2. 有 `<slug_dir>` 时读取原始需求、设计文档、总览、Bug 报告和 review 报告。
3. 沿候选知识线索核实：业务查代码；Skill/约定查对应文档。

## 2. 对比 library

1. 检查 `<cwd>/.agent/library/overall.md`；不存在则视为空 library，不提前创建。
2. 存在时读取索引和相关子文档。
3. 将候选项分类：
   - **新增**：现有 library 未覆盖
   - **增强**：已有条目需要补充或纠正
   - **跳过**：已充分覆盖、不可复用或无法验证

若无新增且无增强（仅跳过或全空），直接说明「无可沉淀内容」并结束，不创建文件。

## 3. 预览与确认

直接在对话中以表格逐项展示（编号从 1 起连续编号）：

| 编号 | 分类 | 目标文档 | 写入内容预览 / 跳过理由 | 核实线索 |
|------|------|----------|-------------------------|----------|

- 新增、增强须给出写入内容预览；跳过可只写精简理由
- 等待用户确认：可按编号选择（如「全部」「只写 1,3」「全拒」）；支持调整后再次确认；全部拒绝则不写入并结束
- 确认前不得写入 library

## 4. 写入

- 仅写入用户确认的新增与增强项
- 优先追加或修订已有主题文档，保持现有风格
- 新主题创建 `<cwd>/.agent/library/<主题>.md`，并更新 `overall.md` 索引
- library 首次创建时生成最小索引：

```markdown
# Library

- [<主题>](<主题>.md)：<一句话范围>
```

- 写入后报告改动文件与新增/增强条目
