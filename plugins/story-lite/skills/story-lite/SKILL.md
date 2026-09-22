---
name: story-lite
description: "轻量需求工作流核心：维护 .agent/story 下的需求/设计/总览/bug/review 文档，支持大需求规划与拆分、设计、实现、Bug、Review、总结与知识沉淀。仅当用户显式点名 story-lite，或显式调用 story 并由其委托时使用；不要根据普通任务内容自动命中。"
---

# 启用

1. 先执行「1 定位」并展示结论。
2. 若定位尚未完成：不得讨论内容、不得改文件。
3. 凡改文件（含元任务改本技能）一律走工作流。
4. 同一会话只执行一次定位；后续模式沿用已定位的 slug 与路径。仅当切换需求主题、报新 Bug 或状态可疑漂移时重新定位。

# 做什么

正式需求：整理 → 设计 → 实现 → Review（按需）→ 整合/总结（按需）。Bug：录入 → 根因 → 修复 → 验证。Quick：需求文档 → 确认 → 实现。目的：agent 维护文档，而非只写代码或只做设计。

# 约定

```
.agent/milestones.yaml
.agent/library/overall.md
.agent/library/<主题>.md
.agent/story/quick/<milestone>/任务短语.md
.agent/story/quick/<milestone>/index.yaml
.agent/story/<slug>/原始需求.md
.agent/story/<slug>/总览.md
.agent/story/<slug>/index.yaml
.agent/story/<slug>/<milestone>/需求N_标题.md
.agent/story/<slug>/<milestone>/bug/BugN_标题.md
.agent/story/<slug>/<milestone>/review/需求N_标题_设计review.md
.agent/story/<slug>/<milestone>/review/需求N_标题_代码review.md
```

- `<cwd>`：当前工作目录。`.agent` 固定为 `<cwd>/.agent`。只直接访问该树。禁止扫描其他目录的 `.agent`。
- `<slug_dir>`：`.agent/story/<slug>/`；`<ms_dir>`：`.agent/story/<slug>/<milestone>/`。
- `<quick_doc>`：`.agent/story/quick/<milestone>/任务短语.md`。
- slug：≤5 词中文短语，创建前确认，无日期前缀；`quick` 为保留名。
- 命名：文件名见路径列表。需求点与 Bug 在整个 slug 内分别连续编号；Quick 不产设计文档。
- 追踪与取号：正式需求以 `<slug_dir>/index.yaml` 为状态、Review、延续和编号的单一数据源；Quick 以同目录 `index.yaml` 追踪状态。正式 `requirement` / `bug` 是已分配最大编号，新增时递增并追加条目（只写有数据的字段）。禁止扫描 `<ms_dir>` 取号。旧文件若只有 `需求` / `bug`，读取时兼容 `需求` 为 `requirement`；下一次写入该文件时改为英文键。不批量回填历史条目。延续、无总览单点迁入总览、或整合写入前，若目标 id 尚无 `items` 条目，按总览或设计文档补这一条（只写有数据的字段）。
- 变更记录：`- <YYYY-MM-DD HH:mm>：…`。原始需求记追加。设计记变更。总览记聚合。Quick/Review 不记。
- 文档先行：实质性变更先更新文档再改代码。文档与代码冲突以代码为准并标注。
- 正式状态枚举：待设计 / 设计中 / 已确认 / 实现中 / Review 中 / 已完成 / 已Review / 阻塞。
- Bug 状态枚举：待确认 / 已确认 / 修复中 / 已修复 / 已验证。
- 状态承载：正式需求写 `items[].status`，Bug 写 `bugs[].status`，Quick 写 `items[].status`。`prior_status` 是状态栈：进入 `Review 中` 或 `阻塞` 时把当前 `status` 追加进去；恢复时弹出末项写回 `status`。旧文件没有对应条目时，仍从总览、设计文档或 Bug 报告读取和更新，直至该 id 被单条补全或后续回填。
- 字段值：条目必写 `id` / `title` / `milestone` / `status`（Bug 另写 `req`）。`file` 与 Review 字段有路径才写，写相对 `<slug_dir>` 的路径。`continues` / `continued_by` / `prior_status` / `keywords` 有元素才写。读时缺字段视为无。由有变无则删除该键，不写 `""` 或 `[]`。顶层 `items` / `bugs` 为空则省略，读时视为 `[]`。Quick 的 `status` 使用简短状态文字。
- 关键字：正式 `items[].keywords` 供检索参考。从对应设计文档的需求简介、功能说明、设计细节抽出 3–8 个短词或短语：模块/类名/skill 名可保留原名，其余 ≤8 字。去重；不写「需求」「设计」「实现」「文档」「状态」等泛词，不写整句。无设计或无该字段视为无。落盘时抽出写入。改设计时重抽并展示与现有的差异，确认后才覆盖；用户要求保留则不覆盖，要求重抽则写入。不另做手改标记。补条目时若已有设计则当场抽出，否则不写。不批量回填。Quick 与 Bug 不写。
- 检索正式 story 时忽略 `.agent/story/quick/`。

## 模板门禁

每次创建或更新目标前读取对应模板。模板文件与本文件同级。

| 目标 | 模板 |
|------|------|
| `原始需求.md` | [FORMAL-TEMPLATES.md](FORMAL-TEMPLATES.md)“原始需求” |
| `总览.md` | [FORMAL-TEMPLATES.md](FORMAL-TEMPLATES.md)“总览” |
| `需求N_标题.md` | [FORMAL-TEMPLATES.md](FORMAL-TEMPLATES.md)“需求点” |
| Quick 文档 | [QUICK-TEMPLATE.md](QUICK-TEMPLATE.md) |
| Bug 报告 | [BUG-TEMPLATE.md](BUG-TEMPLATE.md) |
| Review 报告（新建、更新、Quick 对话输出） | [REVIEW-TEMPLATE.md](REVIEW-TEMPLATE.md) |

## Milestone（`.agent/milestones.yaml`）

```yaml
current: 切片1
milestones:
  切片1:
    created: 2026-05-20
  MS10:
    created: 2026-04-15
```

- `current` 指向当前活跃 milestone。新需求点写入当前 `<ms_dir>`，Quick 写入当前 milestone 的 Quick 目录；已有需求点操作沿用对应 `items[].milestone`，无该条目时用总览里程碑列。
- 若该文件不存在：展示上述模板并确认当前 milestone。用户确认后由 agent 创建，再重新执行定位。
- 若 `<cwd>/.agent` 不存在：停止流程，提醒用户创建 `.agent`。

# 提问规范

对影响需求、验收或实现路径的未决策事项坚持访谈直至达成共识。将决策梳理为设计树：每一个决策都会衍生出依附于它的后续决策。

1. 若事项已是明确的用户需求、可查证事实或纯执行步骤：不进入访谈。
2. 所有问题、选项、推荐答案和确认请求直接写在普通对话中。禁止调用 `AskQuestion` 或同类提问工具。此规则适用于定位、需求拆分、设计、实现、Review、整合及其他需要用户决策的环节。
3. 待处理前沿 = 所有前提已确定、可直接提出、无需猜测尚未知晓答案的决策。每轮集中提出整个待处理前沿。用户作答后重算前沿，进入下一轮。若某题答案依赖本轮尚未解决的另一题：不得放入本轮。用户作答若改了模块归属、同步方式、是否复用已盘点系统，或否定了推荐项里的实现路径，这些都是新前沿；本轮不得落盘或改代码。
4. 每题必须给出推荐答案。若用户明确作答：以用户为准。若用户未明确回答：按该题推荐选项确认，并在进入下一轮或落盘前向用户复述这些默认确认项。禁止脑补推荐之外的未决事实。不得把编译宏、循环依赖、新子系统、跨模块 include 当成已选项的实现细节；这些必须单独成题。
5. 总览或 library 已盘点、且职责相近的现成系统，详细设计访谈必须做成选项。推荐项须说明复用、扩展还是只参考。不得在选项外另发明一套跨模块读数路径。
6. 若前沿为空且用户确认已达成共识：提问会话结束（设计树分支均已遍历）。此前不得写设计文档、总览或代码。
7. 若用户已明确表达原始需求或 Quick 需求：可先整理为草稿并展示确认。未确认的设计细节不写入设计文档或总览。全部确认后一次性落盘，再走文档确认循环。

问题格式（每题）。有可选项时每个选项独占一行。无离散选项可省略 A/B/C。每轮题号从 Q1 起编。题干、选项、推荐不重复已陈述事实。

❓ **Q1** - **<标题>**: <正文：原因；可多段>

A. …
B. …
C. …

➡️ <推荐答案及原因>

# 工作流程

各模式步骤只写本模式动作。写状态：按状态规则把对应 `index.yaml` 条目的 `status` 写成 `<状态>`。无该条目时写总览、设计文档或 Bug 报告。路径、访问、命名、状态承载、文档先行按约定。

## 状态规则

- 正式主链：总览规划新增需求点为 `待设计`，详细设计落盘为 `设计中`；随后 `设计中 → 已确认 → 实现中 → 已完成`。未同步状态即未完成。
- Review：设计 Review 为 `设计中/已确认/Review 中 → Review 中 → 进入前状态`；收尾不因 Review 结束而写成 `已确认`。代码 Review 为 `已完成/已Review/Review 中 → Review 中 → 已Review`。
- Review 例外：无法创建子任务时保持原状态、不改 `prior_status`；进入 `Review 中` 后无可用报告则弹出 `prior_status` 恢复，栈空则删除该键；当前已是 `Review 中` 时复查不再追加栈；改设计回 `设计中` 并删除 `prior_status`，修代码回 `已完成`；当前 Review 字段删除，历史报告保留。
- 设计回退：从 `已确认/实现中/已完成/已Review` 删除 `prior_status` 后回 `设计中 → 已确认 → 实现中 → 已完成`；原状态为 `已Review` 时重做代码 Review。
- 阻塞：把当前 `status` 追加到 `prior_status` 后写 `阻塞`；解除时弹出末项写回。当前已是 `Review 中` 时同样追加，不覆盖更早的栈项。
- Quick：只更新 Quick `index.yaml` 中对应条目的 `status`；Quick Review 不写正式状态。
- Bug：小修走 `已确认 → 修复中 → 已修复 → 已验证`；大修保持 `已确认`，完成 Design 与实现后返回 Bug 写 `已修复 → 已验证`。`待确认` 只作枚举，创建前不落盘；全新需求记录衍生关系后回定位；可复用内容委托 learn。
- 首次 `已完成`：仅在存在可跨需求复用知识时提示一次并等用户决定是否沉淀；不自动调用 `story-lite-learn`。

## 模式路由（触发词 → 模式 → 读取）

路由在定位完成后生效。命中模式后只读取「读取」列指定的文件，不要一次读完全部模式文件。

| 用户触发 | 命中模式 | 读取 |
|----------|----------|------|
| 描述新需求 / 「做 XX」 | 1 定位与需求整理 | 本文件 |
| 「报 Bug」/「缺陷」/「崩溃」/「行为异常」/ Review 问题转 Bug | 3 Bug | [BUG.md](BUG.md) |
| 非 Bug 的简单独立任务 / 无规则与接口变更的中小任务（加日志、debug、小改动等） | 2 Quick（先判断是否符合条件，再与用户确认） | [QUICK.md](QUICK.md) |
| 「拆分」/「生成 TDD」/「写 TDD 文档」/「大需求规划」/ 多需求点大需求 | 4 Design（确认范围与拆分，按需整体规划） | [DESIGN.md](DESIGN.md) |
| 「设计」/「写设计文档」 | 4 Design | [DESIGN.md](DESIGN.md) |
| 「实现」/「开工」 | 5 实现与同步维护 | [IMPLEMENT.md](IMPLEMENT.md) |
| 正式需求或 Quick 的「review」/「审查」 | 6 Review（先确认类型与目标） | [REVIEW.md](REVIEW.md) |
| 「整合」/「生成总览」/ 里程碑收尾 /「总结」 | 7 整合与总结 | [CONSOLIDATE.md](CONSOLIDATE.md) |
| 「沉淀」/「提炼方法论」/「写入 library」 | 8 知识沉淀 | [LEARN.md](LEARN.md) |

## 检索既有设计

- 本会话用 `fd` 列出各正式 `<slug_dir>/index.yaml`（忽略 `quick/`）后缓存；之后只复用已读入的 yaml，按当前描述重新匹配，不复用上次命中列表。
- 主题词与 `items[].keywords`、`title`、slug 目录名匹配；匹配前去掉双方空白；单字及泛词（状态、Review、learn、设计、实现、文档、需求）不单独命中。
- 先展示命中摘要（slug / id / title / keywords / status）；无 `file` 只列条目、不打开。
- 默认深读最多 3 篇最贴的设计（最贴：命中字段数，`title` / skill 全名优先于包含）；同一 slug 只深读最贴 1 篇；当前目标设计另读、不计入这 3 篇；用户点名再加。
- 定位只展示摘要；纯问答与 Design 按限额深读。无主题词命中再按 slug 目录名补查。
- 命中只作参考，不自动续用 slug。不扫设计正文。
- 读取上下文遵循摘要优先、按需深读、范围确认前避免大规模读取；这是决策原则，不设固定读取量门禁。
- 检索正式 story 时忽略 `.agent/story/quick/`。

## 1. 定位与需求整理

入口：启用后第一步。不新增路由优先级。

1. 若本次是无文件产出的纯问答：可跳过定位。先按「检索既有设计」检索并深读相关设计，再读 `<cwd>/.agent/library/`。若随后需要改文件：重新定位。
2. 检查 `<cwd>/.agent`。若不存在：按约定停止并提醒。
3. 读取 `milestones.yaml`。若不存在：按约定展示模板、确认后创建，再从步骤 2 重跑定位。
4. 立即展示工作目录与当前 milestone。分支确认后补充 slug、`<slug_dir>`、目标 `<ms_dir>` 或 `<quick_doc>`。
5. 按模式路由确认目标模式与路径：
   - 若命中 Bug：关联已有 slug 与目标需求点后转 `BUG.md`。若没有候选：询问归属。
   - 若命中 Quick：输出 `<quick_doc>` 后转 `QUICK.md`。
   - 若命中 Quick Review：确认当前 milestone 的目标 Quick 文档，输出路径后转 `REVIEW.md`。
   - 若命中新正式需求：按「检索既有设计」检索同主题或相关 slug，展示命中摘要供参考，确认续用或新建 slug，并转 `DESIGN.md` 确认是否新增需求点。
   - 若命中已有正式需求操作：确认 slug 与目标需求点，从对应 `items` 条目的 `milestone` 定位 `<ms_dir>`；旧 story 没有该条目时用总览的里程碑列定位。随后转对应模式文件。
   - 若命中知识沉淀：转 `LEARN.md`。
6. 若新正式需求已确认：新建 slug 时创建 `<slug_dir>`、`原始需求.md` 与初始内容为 `requirement: 0`、`bug: 0` 的 `index.yaml`；续用 slug 时追加主题根 `原始需求.md`。随后进入 `DESIGN.md`。
