---
name: story
description: "需求工作流入口。根据用户描述自动路由到对应的子流程。TRIGGER WHEN: 用户描述需求时使用。"
---

- @../common/basic.md
- @../common/gamedesign.md

# Story 路由

根据用户描述判断意图并路由到对应 skill。

## 路由表

| 路由目标 | 职责 | 适用场景 |
|---|---|---|
| `/story-milestone` | Milestone 管理 | 创建、切换、列出、重命名 milestone |
| `/story-tdd` | 大需求拆分与 TDD 文档 | 大需求（新 Boss、新系统），需整体理解、拆分、产出 TDD |
| `/story-story` | 整理原始需求 | 用户粘贴原始需求文本，需清理格式、生成 slug、存入目录 |
| `/story-design` | 单个需求点设计 | 对单需求点进行理解、方案设计、产出设计文档；或临时修改设计 |
| `/story-ask` | 探索答疑 | 用户提问、了解现有实现、排查问题，检索文档与代码后直接回答，不产文档 |
| `/story-implement` | 编码实现 | 设计文档已就绪，开始写代码 |
| `/story-review` | 审查 | Review 设计文档或代码实现 |
| `/story-consolidate` | 文档整合 | 多份需求文档合并为总览，以实际代码为准去重校对 |
| `/story-wiki` | 生成 Wiki | 从设计/总览文档生成团队精简 Wiki |
| `/story-learn` | 提炼方法论 | 从对话或 story 文档提炼可复用模式写入 library |

## 流程

1. **阅读描述**：分析用户原始输入。
2. **Slug 预判**：若用户仅提供**短语**，优先判定是否为 Slug。**严格按 `basic.md`「Slug 检索流程」执行**。
   * **是已有 Slug**：完成命中后必读流程，汇总进度并引导下一步。
   * **非已有 Slug / 常规输入**：进入意图判定。
3. **意图判定**：
   * 明确 → 直接调用对应子 skill，原始描述作为 args。
   * 模糊 → 列出可能选项供用户确认后调用。
