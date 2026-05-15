读取需求文档和涉及到的代码文件

从以下方面
- 需求文档与代码实现的一致性
- 代码健壮性与性能
- 是否符合项目规范
- 跨平台兼容性（DS 服务器、手机、编辑器）
- 可简化或重构的部分
- 接口设计是否符合最小暴露原则

**注意** 非本次需求相关的代码不要review

## 输出 YAML 字段映射

代码 Review 的产出是一份 YAML 文件（不再是 .md / .json），由本 skill 主流程调用 `report-html/generate.py` 渲染为 HTML。字段骨架参考 `report-html/example.yaml`，关键映射：

| Review 内容 | YAML 字段 |
|---|---|
| 关联需求 / Review 日期 / 涉及文件 / 问题数量统计 / 结论简述 | `header.meta[]`（每条带 label + value，可选 tint：tint-accent / tint-crit / tint-warn / tint-opt / tint-info；长字段加 `span2: true` 跨两列） |
| 总体评价段落 | `summary.paragraphs[]`（数组，每段一句话） |
| 关键风险 1~3 条（每条标注 R 编号 + 简述） | `summary.key_risks[]`（每条 `severity: crit/warn/opt`） |
| 必须修改条目 | `issues.crit[]` |
| 建议修改条目 | `issues.warn[]` |
| 可选优化条目 | `issues.opt[]` |
| 已撤销 / 已复议条目 | `issues.revoked[]`（字符串数组） |
| 结论二选一勾选 | `verdict.options[]`（被选中那条加 `active: true`） |
| 右上角圆形印章主词 / 副词 | `verdict.status_big`（如 `RESUBMIT` / `APPROVED`）+ `verdict.status_small`（如 `R1 · BLOCKING`） |
| 变更记录 | `footer.changelog` |

每条 issue 字段：
- `id`：R1 / R2 / ...（与 Step 1 的统一编号一致）
- `tag`：≤ 3 字短词（如 阻塞 / 规范 / 性能 / 头文件 / 注释 / 细节）
- `file`：涉及的文件名
- `line`：行号或行号区间（如 `L 12 – 21`）
- `desc`：问题描述（现象、根因、影响）
- `fix`：修复建议（具体到代码 / 字段）

文本内联格式：
- 反引号包裹的 `` `code` `` 渲染为天蓝色代码块
- 双星号包裹的 `**strong**` 渲染为高亮粗体
- 其余 HTML 字符自动转义，无需手动处理