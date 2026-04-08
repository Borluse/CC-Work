---
name: story-review
description: "Review 需求或者代码。TRIGGER: 当用户说'开始 Review'、'审查代码'、'检查实现'时使用。"
user-invocable: false
---

Review 需求或者代码。

## ⚠️ 强制要求：使用 subagent 执行

**你必须使用 Agent tool 来 spawn `story:ue5-reviewer` subagent 执行 Review 任务。**
**严禁在主会话中直接执行 Review 逻辑。**

### 执行步骤

1. 先与用户确认 Review 范围和参数（Slug、需求编号、设计 Review 还是代码 Review）
2. 收集完信息后，调用 Agent tool，参数如下：
   - `subagent_type`: `story:ue5-reviewer`
   - `prompt`: 包含以下全部内容的完整指令：
     - Review 类型（设计 / 代码）
     - 需求文档路径
     - 报告输出路径
     - 下方「Review 规则」章节的全部内容
3. 等待 subagent 返回结果后，将报告呈现给用户

---

## Review 规则（传递给 subagent）

本 Skill 负责需求生命周期的 **Review 阶段**，包括两种独立流程：
- **设计 Review**：审查需求文档的设计质量，生成 `需求<N>_设计Review.md`
- **代码 Review**：审查代码实现与需求文档的一致性，生成 `需求<N>_代码Review.md`

- 如果是C++代码，加载 .agent/library/common/ue5-cpp-rule.md 获取规范

### 路径

- 从上下文中获取Slug和需求编号，如果用户没有提供，则询问用户
- 路径为 `.agent/story/<Slug>/Review/`

### 硬性约束

- 所有 Review 报告生成后**必须停下来**，将报告呈现给用户，等待用户逐项确认。**严禁**自行决定修改内容。
- 读取需求文档，理解功能需求和实现方案
- 所有的条目按统一的标号。例如 R1, R2, R3

- 如果是review设计，参考 `./references/design-review.md`
- 如果是review代码，参考 `./references/code-review.md`

### 生成报告

- 如果是设计review，在需求文档同目录下生成 `需求<N>_设计Review.md`，否则 `需求<N>_代码Review.md`。
- 如果需要书写review文档，加载 `./references/document-template.md`

### 阶段完成提示
Review 完成后，提醒用户：生成的报告路径、需求文档路径、如有必须修改项可再次使用 `/story-review`。
