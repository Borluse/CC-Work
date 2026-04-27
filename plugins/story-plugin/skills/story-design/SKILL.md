---
name: story-design
description: 理解拆解需求并生成设计文档。TRIGGER WHEN 当用户需要分析需求、理解需求、拆解功能、产出边界，根据项目情况书写设计文档。
---

- 加载 skills/common/basic.md 获取必要信息
- 如果用户提供了 Epic 文档路径或提及了 Epic：加载 `epic-instruct.md`
- 如果用户提供了 TDD 文档路径或提及了 TDD：加载 `tdd-instruct.md`

- 如果没有 Epic 或 TDD 上下文，正常进入 Phase 1。

### Phase 1 理解需求

- 根据如下的流程工作，每一步都需用户确认。在用户未确认时，等待用户确认。

从如下角度进行需求理解
  - 需求的目的
  - 需求的设计边界，功能边界，
  - 需求的测试方式，测试场景

**不要**设计到具体的代码细节，本阶段只对其需求和用户意图

**必须**向用户提出澄清问题，并与用户对齐需求理解。
**必须**得到用户的明确确认，才能进入下一步。

### Phase 2 设计

- 加载 skills\common\gamedesign.md 以了解如何进行游戏设计
**必须**得到用户的明确确认，才能进入下一步。

### Phase 3 更新设计文档

- 加载 skills\common\storydocrule.md 以了解如何准备文档
- 文档方式：目录 `.agent/story/<slug>`，统计已有文档数 N，新文件命名 `需求<N+1>_<功能名>.md`。
- 加载 `./references/document-template.md` 来生成文档。
- 提示用户：可进入实现阶段或 Review 阶段。