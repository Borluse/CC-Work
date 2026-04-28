---
name: story-review
description: "Review 需求或者代码。TRIGGER: 当用户说'开始 Review'、'审查代码'、'检查实现'时使用。"
---


- **必须** 加载 skills/common/basic.md 获取必要信息
**强制要求** ：使用 `ue5-reviewer` agent 进行Review

- 找用户了解是review代码还是review需求

# Step 1. Review
- 读取需求文档，理解功能需求和实现方案
- 所有的条目按统一的标号。例如 R1, R2, R3

- 如果是review设计，参考 `./references/design-review.md`
- 如果是review代码，参考 `./references/code-review.md`

- 等待用户逐项确认。**严禁**自行决定修改内容。

# Step 2 生成报告

- 加载 `./references/document-template.md`格式来生成review文档并写出
- 将 Review 报告生成后总结并呈现给用户。

# Step 3 提醒用户
- 提示用户Review文档，并询问哪些问题需要修复。

# Step 4 修复问题
- 修复问题后，更新文档。并重新输出文档报告。回到Step 3
- 如果所有问题都修复了，结束Review。