---
name: story-implement
description: "根据设计文档实现代码。TRIGGER WHEN 当用户已完成需求设计文档、开始编码实现时使用，或需要修改代码时使用。"
fork: true
model: deepseek-v4-pro
---

# Phase 0: 环境初始化 [强制执行，禁止跳过]

**此步不可被推理跳过。无论任务看起来多简单，都必须先完成 Phase 0。**

1. 调用 `/story-init`
2. 记录其输出中的 `<slug_dir>` 和 `<current_milestone>`
3. **门禁**：`/story-init` 完成前，禁止进入 Phase 1。已执行过的会话可跳过，但仍需从输出中确认 slug_dir 的值。

---

# Phase 1: 执行实现

**slug_dir 的值来自 Phase 0 的 story-init 输出，不得自行判断该选哪个场景。**

### 场景 A: 正式需求 (Story) — `<slug_dir>` 有具体路径
1. 读取 `<slug_dir>` 下需求文档，重点「实现方案」「涉及文件」「伪代码」章节。
2. 修改意图与文档设计冲突 → **禁止直接实现**，须调用 `/story-design` 重新设计。
3. 严格遵循文档接口设计（函数签名、参数、返回值）。

### 场景 B: 临时需求 (Quick) — `<slug_dir>=N/A`
1. **禁止**直接修改目标源文件。
2. 先在对话中输出具体修改方案（伪代码或 Diff 预估）。
3. 等待用户确认后方可操作文件。
4. 完成后将需求和方案写入 `.agent/story/<current milestone>/快速需求`，文件名从需求中抽 slug 短语，内容：日期、需求简介、方案。
5. 多轮修改须始终更新文档。

# Phase 2: 完成与交付

代码完成后向用户提示：
1. 关联需求文档路径（若有）。
2. 本次修改/新增源文件列表。
3. "可进入 Review 阶段，或继续修改代码"。
