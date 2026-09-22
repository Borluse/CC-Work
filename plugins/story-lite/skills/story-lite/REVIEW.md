# Review 模式（标准报告，必须开子任务）

前置：已完成主技能定位，并已读取主技能的约定、状态规则与模板门禁。

入口：用户要求方案、设计或代码 Review；只审本次确认的范围。

出口：设计 Review 收尾回进入前状态；代码 Review 收尾写为 `已Review`；若 Review 问题转 Bug，转 `BUG.md`。

## 1. 门禁

询问方案或设计 Review，还是代码 Review。

- 正式需求设计 Review：须已有目标设计文档，且状态为 `设计中`、`已确认` 或 `Review 中`；`待设计` 则转 `DESIGN.md` 先落盘设计。不要等待用户把设计改成 `已确认`。
- 正式需求代码 Review：须为 `已完成`、`已Review` 或 `Review 中`，否则转 `IMPLEMENT.md`。
- 当前为 `Review 中` 时按续审进入，不改 `prior_status`。
- Quick 方案 Review：须当前 milestone 的 `index.yaml` 中该条 `status` 为 `已确认` 或 `已完成`；代码 Review 须该条为 `已完成`。无该条目或不满足则转 `QUICK.md`。

## 2. 子任务

- 正式需求：传递 `<slug_dir>`、目标 `<ms_dir>` 文档、需求上下文和涉及文件。若确认可执行：当前 `status` 不是 `Review 中` 时把当前 `status` 追加到 `prior_status`，再写 `Review 中`。
- Quick：传递 Quick 文档、前次报告上下文和涉及文件。
- 若无法创建子任务：保持进入前状态（尚未写成 `Review 中` 则不改）。若已写成 `Review 中` 但无可用报告：按状态规则恢复进入前状态。Quick 直接停止并说明。

## 3. 报告

- 正式需求且无已有报告：按主技能模板门禁写入目标 `<ms_dir>/review/`。
- 正式需求且已有报告：沿用原格式更新。
- Quick：默认按同一模板在对话完整输出。不创建报告文件或链接。若用户要求保存：先确认目标路径。

## 4. 处理

询问哪些问题现在修。

- 正式需求设计 Review 改方案：按状态规则写 `设计中`，删除 `design_review` 与 `prior_status`，按 `DESIGN.md` 更新设计文档后复查，不必先写成 `已确认`。
- 正式需求代码 Review 修复后：按状态规则写 `已完成`，删除 `code_review`。
- Quick：先更新 Quick 文档并展示确认。方案修复后直接复查。代码修复在确认后改代码并复查。超出 Quick 或需转 Bug：先转正式需求。
- 每次复查均开子任务并更新原报告或对话报告，直至清零或用户确认结束。
- 正式需求转 Bug：携带 Review 结论，并确认关联与修复方案。

## 5. 收尾

- 正式设计 Review：若 `prior_status` 非空则弹出末项写回 `status`，栈空则删除该键，否则保持当前 `status`；把报告相对路径写入 `design_review`。不因 Review 结束而写成 `已确认`。
- 正式代码 Review：写 `已Review`，删除 `prior_status`，把报告相对路径写入 `code_review`。
- Quick：只输出最终报告。
- 两者均保留未修问题与全部修复记录。
