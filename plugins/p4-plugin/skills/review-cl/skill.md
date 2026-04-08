---
name: review-cl
description: Review P4 pending changelist 的代码质量。Use when the user says "review CL" / "review changelist" / "审查CL" / "review下CL"，或提供了一个 CL 编号要求审查时触发。
---

对指定的 Perforce pending changelist 执行代码审查，输出结构化的 review 报告。

## 前置条件

- 当前环境已配置 `p4` 命令行工具
- 用户的 P4 客户端名称可通过 `p4 info` 获取（字段 `Client name`）
- 加载 `.agent/library/p4.md` 获取客户端等信息

## 输入

用户提供 **CL 编号**（如 `641455`）。如果用户没有提供，先列出 pending CL 让用户选择：

```bash
p4 changes -s pending -u <username>
```

## 工作流程

### 1. 获取 CL 信息

```bash
# 获取 P4 客户端名称
p4 -ztag -F "%client%" info

# 获取 CL 描述和文件列表
p4 describe -s <CL号>
```

从 `p4 describe -s` 输出中提取：
- CL 描述
- 受影响文件列表（depot 路径）

### 2. 获取每个文件的 diff

对 pending CL，`p4 describe -du` 不会输出 diff。必须逐文件使用：

```bash
p4 -c <客户端名> diff -du "<depot路径>"
```

**注意**：
- 如果文件数量 > 8，使用 Agent 工具并行读取 diff，加速处理
- 如果单个文件 diff 超过 500 行，先看整体结构再聚焦关键改动
- 编码问题：P4 中文描述可能乱码（GBK），不影响 review，忽略即可

### 3. 分析代码

对收集到的所有 diff，按以下维度逐一审查：
如果是C++代码，加载 `.agent/library/common/ue5-cpp-rule.md` 获取规范

### 4. 输出 Review 报告

使用以下**固定格式**输出：

```markdown
## CL <编号> Review — <一句话描述变更主题>

### 变更概述

<2-3 句话概述这次改动做了什么，为什么这样做>

| 文件 | 变更类型 |
|---|---|
| `文件名` | 新增/删减/修改：简要说明 |
| ... | ... |

---

### 好的方面

1. **<亮点标题>** — 具体说明
2. ...

---

### 必须修复的问题

#### 1. <问题标题>

```cpp
// 有问题的代码片段
```

**问题**：具体说明为什么有问题
**建议**：给出修复方案或代码示例

#### 2. ...

---

### 建议改进

#### N. <建议标题>

具体说明 + 建议方案

---

### 总结

| 级别 | 数量 | 说明 |
|---|---|---|
| 必须修 | N | 简要列举 |
| 建议改 | N | 简要列举 |

<一句话总结评价>
```

## 注意事项

- **用中文**输出 review 报告
- 必须修复 vs 建议改进 的区分标准：
  - **必须修复**：逻辑错误、会导致 bug 或 crash、行为意外变更
  - **建议改进**：代码风格、可读性、潜在优化、非阻塞性问题
- 不要虚构问题，每个指出的问题都必须有 diff 中的代码依据
- 对于大型 CL（>15 个文件），先给出整体架构评价，再逐模块 review
- 如果 CL 中包含纯机械性改动（如批量 rename、格式化），简要提及即可，不必逐行 review
