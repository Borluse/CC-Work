---
name: p4-review-cl
description: "Review P4 pending changelist 的代码质量。Use when the user says 'review p4 CL' / 'review p4 changelist' / '审查 p4 CL' / 'review下 p4 CL'，或提供了一个 CL 编号要求审查时触发。"
---

**必须** 仅查看符合当前的workspace的 CL。若当前workspace没有CL，则提示用户并退出。

### step 1

1. 通过 `p4 info` 获取 P4 用户名。
2. 通过 `p4 clients -u <用户名>` 获取所有客户端。并根据当前目录判断具体的workspace
3. 通过 `p4 changes -s pending -c <workspace>` 获取所有 pending CL。
4. 通过 `p4 -c <workspace> opened -c default` 检查 default CL 是否有文件。


### step 2
- 将 所有 pending CL 和 default CL（如果有文件）一起列出供用户选择。
- 列出每一个 CL 的文件列表。
使用`AskUserQuestion`询问用户选择要审查的 CL。

### step 3

并行启用2-3个Agent工具

逐文件使用：
```bash
p4 -c <客户端名> diff -du "<depot路径>"
```

对收集到的 diff，按以下维度逐一审查：
如果是C++代码，加载 `.agent/library/common/ue5-cpp-rule.md` 获取规范

### step 4
汇总所有的agent结论，生成 review 报告。

使用以下**固定格式**输出：

```markdown
## CL <编号|default> Review — <一句话描述变更主题>

### 变更概述

<2-3 句话概述这次改动做了什么，为什么这样做>

| 文件 | 变更类型 |
|---|---|
| `文件名` | 新增/删减/修改：简要说明 |
| ... | ... |

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
