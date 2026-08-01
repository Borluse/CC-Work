---
name: story
description: "需求工作流入口, 根据用户描述自动路由到对应的子流程。TRIGGER WHEN: 用户描述需求时使用。"
---

- @../common/basic.md


# 获取基础信息
- 获取当前目录，标记为`<cwd>`（已知则跳过）
- 获取如下信息：
   - 查看 `<cwd>/vcs.md`（若存在），确认并输出版本库信息。
   - 查看 `<cwd>/.agent/milestones.yaml` 获取当前milestone；不存在则提示用户执行 `/story-milestone`。 
- 定位 slug（**仅在当前 milestone 下搜索**）：
   - 在 `<cwd>/.agent/story/<milestone>/` 下查找已有 slug。
   - `quick`: 临时需求，在`<cwd>/.agent/story/<milestone>/quick` 目录
   - 若命中: 标记为 `<slug_dir>`。
   - 未命中: 标记 `<slug_dir>N/A`。

- 获取完后输出信息给用户
# 规则
## 思考原则
- **最小化设计（YAGNI）**：每个设计须有明确当前需求支撑，**禁止**"以防万一"式过度设计。

## 向用户提问
- 与用户讨论方案/设计细节时，对每个细节持续深度追问，直到达成完全一致理解。遍历设计树每个分支，逐一梳理解决各决策依赖关系。每个问题附推荐解答/建议。若问题可通过探索代码库得答案 → 主动用 ast-grep、rg、fd 检索相关逻辑再做决策。
- 提问时禁止使用 `askuserquestion` 工具。
- 提问需包含如下信息：标题，原因，可选项，推荐选项及其原因 

# 模式
包含如下模式，根据用户的意图命中如下的模式

需确定场景类型：
- 若能确定slug，则为正式需求，标记为`formal`
- 否则为临时需求，slug为`quick` 标记为`quick`
- 与用户确认场景

## Story模式
帮用户初始化一个需求，若slug为空，或slug下没有`原始需求.md`，进入该模式

## Design 模式:
根据已提供的需求描述或指引，帮用户进行设计工作，并产生设计文档
- 加载 `references\design.md`
## Implement 模式
根据已提供的设计文档，完成开发
- 加载 `references\implement.md`
## Review 模式
根据已提供的设计文档和代码，完成代码或设计的review
- 加载 `references\review.md`
