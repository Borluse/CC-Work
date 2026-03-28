---
name: story
description: 需求工作流入口。TRIGGER: 根据用户描述自动路由到子流程：设计(design)、实现(implement)、审查(review)、经验提炼(learn)。 
---

# Story 路由

根据用户的描述，判断意图并路由到对应的 skill。

## 路由表

| 路由目标 | 适用场景 |
|---|---|
| `/story-design` | 新需求、分析需求、拆解功能、设计方案 |
| `/story-implement` | 开始实现、写代码、编码、改代码 |
| `/story-review` | review、审查、检查 |
| `/story-learn` | 提炼方法论、沉淀经验、写入 library |

## 流程

1. 阅读用户的描述
2. 意图明确则直接推荐，意图模糊则列出所有选项，用 AskUserQuestion 让用户确认
3. 确认后，使用 Skill 工具调用对应的子 skill，将用户的原始描述作为 args 传递
