# CC-Work

Claude Code 插件市场仓库，包含多个面向开发工作流的插件和 Agent。

## 插件列表

### story-plugin (v2.4.0)

需求生命周期管理插件，覆盖需求从设计到实现到 Review 的完整流程。

**Skills：**

| Skill | 说明 |
|-------|------|
| `story-design` | 需求设计 — 理解拆解需求并生成设计文档 |
| `story-implement` | 需求实现 — 根据设计文档编码实现 |
| `story-review` | 需求/代码 Review |
| `library-update` | Library 文档更新 |
| `library-doc-index` | 目录文件索引生成 |
| `story-wiki` | 从需求文档和代码生成 Wiki |
| `story-learn` | 从设计文档提炼方法论写入 library |

**Agents：**

| Agent | 说明 |
|-------|------|
| `ue5-expert` | UE5 FPS C++ 代码阅读专家 |
| `ue5-reviewer` | UE5 FPS C++ 代码审查专家 |

### git-plugin (v1.0.0)

Git 工具插件，提供自动化提交和文档生成功能。

**Skills：**

| Skill | 说明 |
|-------|------|
| `git-commit` | 根据代码差异自动生成提交信息并完成提交 |
| `readme-update` | 根据项目内容生成或更新 README |

## 项目结构

```
.claude-plugin/
  marketplace.json          # 插件市场配置
plugins/
  story-plugin/             # 需求生命周期管理插件
    agents/                 # UE5 专家 Agent
    skills/                 # 设计、实现、Review 等 Skill
  git-plugin/               # Git 工具插件
    skills/                 # 提交、README 更新等 Skill
```

## 使用方式

本仓库作为 Claude Code 插件市场源使用，插件通过 `marketplace.json` 注册并分发。
