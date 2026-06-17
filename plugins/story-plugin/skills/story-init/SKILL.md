---
name: story-init
description: "初始化需求工作环境。TRIGGER: 当用户说'初始化'、'story init'、'开始需求'、'环境准备'、'准备工作区'时使用。"
user-invocable: false
---

- @../common/basic.md

# 前置必做任务，如已有信息，则跳过

## 模式
根据调用方上下文：
- **默认模式（search-only）**：仅查找 slug，未命中不创建，标记 `<slug_dir>=N/A`。
- **create-slug 模式**：定位 slug，未命中则按 `basic.md`「Slug 规则」创建。

## 步骤
1. 获取当前目录，标记为`<cwd>`（已知则跳过）
2. 查看 `<cwd>/vcs.md`（若存在），确认并输出版本库信息。
3. 查看 `<cwd>/.agent/milestones.yaml` 并获取当前milestone；不存在则提示用户执行 `/story-milestone`。
4. 定位 slug（**仅在当前 milestone 下搜索**）：
   - 在 `<cwd>/.agent/story/<milestone>/` 下查找已有 slug，**禁止搜索其他 milestone**。
   - 命中：标记为 `<slug_dir>`。
   - 未命中（create-slug 模式）：根据用户输入提炼 slug（≤5 词中文短语），与用户确认后创建，标记为 `<slug_dir>`。
   - 未命中（默认/search-only）：标记 `<slug_dir>=N/A`。
5. 将`<cwd>`, vcs, milestone 和 slug 信息简报输出给用户。
