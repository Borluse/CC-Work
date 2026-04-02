---
name: update-version
description: 根据上下文判断涉及哪个插件，更新其 plugin.json 版本号，同步 README，可选提交推送。TRIGGER: 当用户说"更新版本号"、"bump version"、"发版"时使用。
---

根据会话上下文判断本次改动涉及哪个插件，更新对应的版本号、同步 README，并可选提交推送。

## 流程

### Phase 1: 定位目标插件

- 回顾本次会话上下文，分析用户修改了哪些文件
- 根据修改文件的路径，判断涉及哪个插件目录（可能涉及多个）
- 使用 `fd "plugin.json" --type f` 搜索仓库中所有 `.claude-plugin/plugin.json`
- 将修改的文件路径与找到的插件目录做匹配，确定需要更新版本的插件
- 如果无法自动判断或涉及多个插件，让用户确认

### Phase 2: 读取当前版本

- 读取目标插件的 `.claude-plugin/plugin.json`
- 提取当前 `version` 字段值

### Phase 3: 确定新版本号

- 根据本次会话的改动内容，推荐 semver bump 类型：
  - **patch**：bug 修复、小调整、文档更新
  - **minor**：新功能、新 skill、新 agent
  - **major**：破坏性变更
- 向用户展示当前版本和推荐的新版本，让用户确认或自定义

### Phase 4: 更新版本号

- 修改目标插件的 `.claude-plugin/plugin.json` 中的 `version` 字段为新版本号

### Phase 5: 更新 README

- 调用 Skill 工具执行 `readme-update`，同步版本号和项目信息到 README

### Phase 6: 可选提交推送

- 询问用户是否要提交并推送
- 如果用户同意，调用 Skill 工具执行 `git-commit`
