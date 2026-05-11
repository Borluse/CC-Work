---
name: story-implement
description: 根据设计文档实现代码。TRIGGER WHEN 当用户已完成需求设计文档、开始编码实现时使用，或需要修改代码时使用
---

根据设计文档实现代码。

- **必须** 加载 skills/common/basic.md 获取必要信息
- **必须** 加载 `.agent/library/common/ue5-cpp-rule.md` 获取代码规范

# Phase 1 理解与确认

- 根据用户判断是story还是临时需求。
- 如果是story，加载 ${CLAUDE_SKILL_DIR}\story-instruct.md
- 如果是临时需求，加载 ${CLAUDE_SKILL_DIR}\quick-instruct.md

# Phase 2 完成实现
代码编写完成后，提醒用户：
- 当前需求文档路径
- 已修改的源文件列表
- 提示用户：可进入 Review 阶段，或继续修改代码
