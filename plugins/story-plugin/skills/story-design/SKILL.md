---
name: story-design
description: 理解拆解需求并生成设计文档。TRIGGER WHEN 当用户需要分析需求、理解需求、拆解功能、产出边界，根据项目情况书写设计文档。
---

### Phase 1: 需求理解与方案设计
- 加载依赖：`${CLAUDE_SKILL_DIR}/../common/basic.md`，`${CLAUDE_SKILL_DIR}/../common/gamedesign.md`。如有 TDD 则加载 `./tdd-instruct.md`。
- 行为：从 UE5 系统策划角度分析功能边界、测试用例，不涉及具体代码细节。
- 约束：梳理出所有未决的设计分歧，**并向用户提出澄清问题，最终输出整体结论后，等待确认后再进入下一步。**

### Phase 2: 更新设计文档
- 加载模板：`.agent/references/document-template.md`。
- 行为：将确认后的方案写入对应的需求文件中。同步更新 TDD 文档（如有变更）。
- 结束：提示用户可进入实现阶段。