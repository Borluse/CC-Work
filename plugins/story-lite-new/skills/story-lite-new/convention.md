# 工作约定

## `.agent` 目录结构

```text
.agent/
├── milestones.yaml
├── library/
│   ├── overall.md
│   └── <主题>.md
└── story/
    ├── quick/
    │   └── <milestone>/
    │       ├── 任务短语.md
    │       └── index.yaml
    └── <slug>/
        ├── 原始需求.md
        ├── 总览.md
        ├── index.yaml
        └── <milestone>/
            ├── 需求N_标题.md
            ├── bug/
            │   └── BugN_标题.md
            └── review/
                ├── 需求N_标题_设计review.md
                └── 需求N_标题_代码review.md
```

- `.agent` 固定在当前工作目录根部，只使用当前工作区的 `.agent`。
- `<slug>` 是正式主题的短名称，最多 5 个中文词，不带日期前缀；`quick` 是保留名称。
- `index.yaml` 中的 `file`、`design_review`、`code_review` 使用相对于主题根 `<slug>` 的正斜杠路径。

## YAML

`.agent` 下只有下面三类 YAML，字段集合、类型和状态枚举固定，不增加未定义字段；日期用 `YYYY-MM-DD`，空的可选字段不写入；编号只来自账本计数器，不扫描目录。`story.py` 写入时自动满足这些规则，读取时逐项校验。

### `.agent/milestones.yaml`

```yaml
current: 切片1
milestones:
  切片1:
    created: 2026-08-05
```

### `.agent/story/<slug>/index.yaml`

```yaml
requirement: 1
bug: 1
items:
  - id: 1
    title: 入口 skill 概念化核心工作流
    milestone: 切片1
    status: 阻塞
    keywords:
      - 自主路由
      - 概念职责
    file: 切片1/需求1_入口skill概念化核心工作流.md
    design_review: 切片1/review/需求1_入口skill概念化核心工作流_设计review.md
    continues: [2]
    continued_by: [3]
    prior_status:
      - 实现中
bugs:
  - id: 1
    title: 入口未被正确加载
    req: 1
    milestone: 切片1
    status: 已验证
    file: 切片1/bug/Bug1_入口未被正确加载.md
```

- `requirement`、`bug`：已分配的最大需求点编号和 Bug 编号。
- `continues`、`continued_by`：只引用需求点编号，脚本不维护，直接编辑。
- `req`：Bug 关联的需求点编号，没有关联时省略。
- `prior_status`：脚本维护的阻塞前状态栈，不手改。
- `keywords`：只用于正式需求，供后续定位时检索。设计完成后从设计文档中提取 3–8 个短词或短语，选检索者最可能输入的词：模块名、类名、Skill 名保留原名；不写「需求」「设计」「实现」这类每个需求都适用的泛词，也不写整句。设计发生实质变化时重新提取，并向用户展示与原有关键字的差异。

### 正式需求状态

- `待设计`：已在总览中规划并占号，尚无详细设计。
- `设计中`：详细设计已落盘，尚未确认。
- `已确认`：设计已确认，可以进入实现。
- `实现中`：正在修改实际产物。
- `已完成`：实现完成且有验证证据。代码 Review 的发现修复并验证后，也回到这个状态。
- `已Review`：代码 Review 完成，没有需要修复的发现，或发现已记录为暂不处理。
- `阻塞`：临时状态。用 `--status 阻塞` 进入时脚本把当前状态压入 `prior_status`，用 `--restore` 解除时弹出写回。

Review 进行中不改变状态，结论通过 `--review-kind` 与 `--review-path` 记录报告路径。设计发生实质变化时回到 `设计中`，并用 `--clear-review` 删除 Review 路径（历史报告文件保留），因为旧 Review 结论不再适用于新设计。以上未列出的流转按各状态的含义判断。

### Bug 状态

- `待确认`：现象已报告，尚未确认属于 Bug。
- `已确认`：确认是行为偏离已确认意图；修复需要改变方案时保持该状态，先完成设计与实现再继续。
- `修复中`、`已修复`、`已验证`：依次表示正在修复、修复完成、修复已被证据验证。

### `.agent/story/quick/<milestone>/index.yaml`

```yaml
items:
  - title: 修复日志输出
    status: 已完成
```

每个条目只有 `title` 和 `status`；`status` 只能是 `待确认`、`已确认` 或 `已完成`，新建时默认 `已确认`。

## Review 报告

Review 结论需要可追踪，使后续修复和复查能够引用同一条发现：

- 按严重程度分组，依次使用 `### 🔴 高`、`### 🟡 中`、`### 🟢 低`；没有发现的等级省略，不虚构空发现。
- 编号从 `R1` 开始，按高到低的顺序在整份报告内连续递增，各等级不重置编号。
- 每条发现至少记录关联文件或范围、问题、原因、影响和建议。
- 复查沿用原报告编号，新增发现从当前最大编号继续，已修复或关闭的发现保留原编号。
