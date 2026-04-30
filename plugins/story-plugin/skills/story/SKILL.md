---
name: story
description: 需求工作流入口。TRIGGER WHEN 根据用户描述自动路由到子流程：设计(design)、实现(implement)、审查(review)、经验提炼(learn)。 
---

# Story 路由

根据用户的描述，判断意图并路由到对应的 skill。

## 路由表

| 路由目标 | 职责 | 适用场景 |
|---|---|---|
| `/story-tdd` | 大需求拆分与 TDD 文档 | 拿到一个大需求（如新 Boss、新系统），需要整体理解、拆分子需求、产出 TDD 文档 |
| `/story-story` | 整理原始需求 | 用户粘贴了一段原始需求文本，需要清理格式、生成 slug、存入需求目录 |
| `/story-design` | 单个需求点设计 | 对单个需求点进行需求理解、方案设计、产出设计文档 |
| `/story-implement` | 编码实现 | 设计文档已就绪，开始写代码；或临时修改代码 |
| `/story-review` | 审查 | Review 设计文档或代码实现 |
| `/story-consolidate` | 文档整合 | 多份需求文档合并为一份总览，以实际代码为准去重校对 |
| `/story-wiki` | 生成 Wiki | 从设计/总览文档生成面向团队的精简 Wiki |
| `/story-learn` | 提炼方法论 | 从对话上下文或 story 文档中提炼可复用模式写入 library |

## 流程

1. 阅读用户的描述
2. 意图明确则直接推荐，意图模糊则列出所有选项让用户确认
3. 确认后，使用 Skill 工具调用对应的子 skill，将用户的原始描述作为 args 传递

