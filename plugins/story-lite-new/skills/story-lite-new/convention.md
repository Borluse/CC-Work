# 工作约定

本文档定义 Story 工作区中稳定的文档、路径和 YAML 账本约定。处理 `.agent` 文档、文件路径或 YAML 账本时，以本文档为准。

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
- `<slug>` 是正式主题的短名称，最多 5 个中文词，不带日期前缀。
- `quick` 是保留名称，不能作为正式主题 slug。
- `.agent/story/<slug>/` 是主题根目录；`<milestone>` 位于主题根目录下。
- `原始需求.md` 保存用户原始意图；`总览.md` 保存跨需求的当前摘要。
- 需求点、Bug 和 Review 文档位于对应 milestone 目录。
- `library/` 保存可跨需求复用的方法论，不替代具体需求文档。
- 正式主题检索时忽略 `.agent/story/quick/`。

## 文件命名和路径

- 正式需求点：`需求N_标题.md`
- Bug：`bug/BugN_标题.md`
- 设计 Review：`review/需求N_标题_设计review.md`
- 代码 Review：`review/需求N_标题_代码review.md`
- Quick 文档：`story/quick/<milestone>/任务短语.md`
- 需求点和 Bug 在同一主题内分别连续编号。
- `index.yaml` 中的 `file`、`design_review`、`code_review` 使用相对于主题根 `<slug>` 的正斜杠路径。

## YAML 总则

`.agent` 下的工作流 YAML 只有以下三类：

1. `.agent/milestones.yaml`
2. `.agent/story/<slug>/index.yaml`
3. `.agent/story/quick/<milestone>/index.yaml`

每类 YAML 的字段集合、字段类型、状态枚举、路径规则和空集合规则固定。未定义字段不作为扩展机制。

- YAML 字段使用规定的大小写和拼写。
- 日期使用 `YYYY-MM-DD` 字符串。
- 编号使用不小于 0 的整数。
- 空的可选字段不写入，不写 `null` 或空数组。
- 不通过扫描目录分配编号。

## `milestones.yaml`

位置：`.agent/milestones.yaml`

### 允许的顶层字段

```yaml
current: string
milestones: mapping
```

### 固定结构

```yaml
current: 切片1
milestones:
  切片1:
    created: 2026-08-05
```

规则：

- `current` 必填，值必须对应 `milestones` 中的一个 key。
- `milestones` 必填且为映射。
- 每个 milestone 条目只允许 `created` 字段。
- `created` 必填，格式为 `YYYY-MM-DD`。
- 不允许增加其他顶层字段或 milestone 字段。

## 正式主题 `index.yaml`

位置：`.agent/story/<slug>/index.yaml`

### 允许的顶层字段

```yaml
requirement: integer
bug: integer
items: array
bugs: array
```

`items` 或 `bugs` 没有条目时，省略对应顶层字段；该省略规则是固定结构的一部分。

### 固定结构示例

```yaml
requirement: 1
bug: 0
items:
  - id: 1
    title: 入口 skill 概念化核心工作流
    milestone: 切片1
    status: 已完成
    keywords:
      - 自主路由
      - 概念职责
    file: 切片1/需求1_入口skill概念化核心工作流.md
    design_review: 切片1/review/需求1_入口skill概念化核心工作流_设计review.md
    code_review: 切片1/review/需求1_入口skill概念化核心工作流_代码review.md
    continues: [2]
    continued_by: [3]
    prior_status:
      - 已确认
bugs:
  - id: 1
    title: 入口未被正确加载
    req: 1
    milestone: 切片1
    status: 已验证
    file: 切片1/bug/Bug1_入口未被正确加载.md
```

### 顶层字段

- `requirement`：必填整数，表示已分配的最大需求点编号。
- `bug`：必填整数，表示已分配的最大 Bug 编号。
- `items`：正式需求条目数组；无条目时省略。
- `bugs`：Bug 条目数组；无条目时省略。

### 正式需求条目

必填字段：

```yaml
id: integer
title: string
milestone: string
status: formal-status
```

允许的可选字段：

```yaml
keywords: string[]
file: string
design_review: string
code_review: string
continues: integer[]
continued_by: integer[]
prior_status: formal-status[]
```

约束：

- 同一主题内 `items[].id` 唯一且连续分配。
- `keywords` 只用于正式需求，设计完成后填写 3–8 个短词或短语。
- `file`、`design_review`、`code_review` 均为相对于主题根的路径。
- `continues` 和 `continued_by` 只引用需求点编号。
- `prior_status` 只保存正式需求状态。

### Bug 条目

必填字段：

```yaml
id: integer
title: string
req: integer | ""
milestone: string
status: bug-status
```

允许的可选字段：

```yaml
file: string
prior_status: bug-status[]
```

约束：

- 同一主题内 `bugs[].id` 唯一且连续分配。
- `req` 填关联需求点编号；没有关联需求点时使用空字符串。
- Bug 不使用 `keywords`、`design_review` 或 `code_review`。
- `file` 为相对于主题根的路径。

### 正式需求状态

```text
待设计
设计中
已确认
实现中
Review 中
已完成
已Review
阻塞
```

### Bug 状态

```text
待确认
已确认
修复中
已修复
已验证
```

## Quick `index.yaml`

位置：`.agent/story/quick/<milestone>/index.yaml`

### 允许的顶层字段

```yaml
items: array
```

### 固定结构示例

```yaml
items:
  - title: 修复日志输出
    status: 已完成
```

规则：

- `items` 必填且为数组。
- 每个条目只允许 `title` 和 `status`。
- `title` 为字符串。
- `status` 只能是 `待确认`、`已确认` 或 `已完成`。
- Quick 不使用 `requirement`、`bug`、`id`、`keywords`、`file`、`design_review`、`code_review`、`continues`、`continued_by` 或 `prior_status`。

## 文档与代码一致性

- 文档保存意图、方案、约束和重要决策。
- 代码和实际验证证据是行为判断的最终依据。
- 关键理解、方案或实际行为发生变化时，相关文档应与事实保持一致。
- 文档与代码不一致时，记录差异并以实际代码行为为准。 
