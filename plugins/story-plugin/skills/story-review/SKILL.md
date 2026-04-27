---
name: story-review
description: "Review 需求或者代码。TRIGGER: 当用户说'开始 Review'、'审查代码'、'检查实现'时使用。"
---


- **必须** 加载 skills/common/basic.md 获取必要信息

**强制要求** ：使用 subagent 执行

## Review 规则

本 Skill 负责需求生命周期的 **Review 阶段**，包括两种独立流程：
- **设计 Review**：审查需求文档的设计质量，生成 `需求<N>_设计Review.md`
- **代码 Review**：审查代码实现与需求文档的一致性，生成 `需求<N>_代码Review.md`

- 如果是C++代码，加载 .agent/library/common/ue5-cpp-rule.md 获取规范

### 路径

- 从上下文中获取Slug和需求编号，如果用户没有提供，则询问用户
- 路径为 `.agent/story/<Slug>/Review/`

# Step 1. Review
- 读取需求文档，理解功能需求和实现方案
- 所有的条目按统一的标号。例如 R1, R2, R3


- 如果是review设计，参考 `./references/design-review.md`
- 如果是review代码，参考 `./references/code-review.md`

- 等待用户逐项确认。**严禁**自行决定修改内容。

# Step 2 生成报告

- 如果是设计review，在需求文档同目录下生成 `需求<N>_设计Review.md`，否则 `需求<N>_代码Review.md`。
- 如果需要书写review文档，加载 `./references/document-template.md`
- 将 Review 报告生成后呈现给用户。

# Step 3 提醒用户
- 提示用户Review文档，并询问哪些问题需要修复。

# Step 4 修复问题
- 修复问题后，更新文档。并重新输出文档报告。回到Step 3
- 如果所有问题都修复了，结束Review。