# CC-Work

Claude Code 插件市场仓库，包含多个面向开发工作流的插件和 Agent。

## 插件列表

### story-plugin (v3.7.3)

需求生命周期管理插件，覆盖需求从设计到实现到 Review 的完整流程。

**Skills：**

| Skill | 说明 |
|-------|------|
| `story` | 需求工作流入口 — 根据描述自动路由到子流程 |
| `story-tdd` | 大需求拆分与规划，生成 TDD 文档 |
| `story-story` | 整理清理原始需求文档 |
| `story-design` | 单个需求点设计 — 理解拆解需求并生成设计文档 |
| `story-implement` | 编码实现 — 根据设计文档或临时需求实现代码 |
| `story-review` | 需求/代码 Review |
| `story-consolidate` | 根据实际代码合并整理需求文档 |
| `story-wiki` | 从设计文档生成精简的 Wiki 文档 |
| `story-learn` | 从上下文提炼可复用方法论写入 library |

**Agents：**

| Agent | 说明 |
|-------|------|
| `ue5-expert` | UE5 FPS C++ 代码阅读专家 |
| `ue5-reviewer` | UE5 FPS C++ 代码审查专家 |

### git-plugin (v1.1.4)

Git 工具插件，提供自动化提交和文档生成功能。

**Skills：**

| Skill | 说明 |
|-------|------|
| `git-commit` | 根据代码差异自动生成提交信息并完成提交 |
| `readme-update` | 根据项目内容生成或更新 README |
| `update-version` | 根据上下文更新插件版本号、同步 README，可选提交推送 |

### p4-plugin (v1.1.3)

Perforce 工具插件，提供 P4 changelist 代码审查功能。

**Skills：**

| Skill | 说明 |
|-------|------|
| `p4-review-cl` | 对 P4 pending changelist 执行代码审查 |

### obsidian-plugin (v1.0.0)

Obsidian vault 管理插件，通过 obsidian-cli 对 Markdown 笔记进行自动化操作。

**Skills：**

| Skill | 说明 |
|-------|------|
| `obsidian` | 通过 obsidian-cli 对 vault 进行搜索、创建、移动、删除等操作 |
| `docgen` | 从代码生成符合 Obsidian 规范的技术文档 |

## 项目结构

```
.claude-plugin/
  marketplace.json          # 插件市场配置
plugins/
  story-plugin/             # 需求生命周期管理插件
    agents/                 # UE5 专家 Agent
    skills/                 # 设计、实现、Review、Epic 拆分等 Skill
  git-plugin/               # Git 工具插件
    skills/                 # 提交、README 更新等 Skill
  p4-plugin/                # Perforce 工具插件
    skills/                 # CL 审查等 Skill
  obsidian-plugin/          # Obsidian vault 管理插件
    skills/                 # obsidian 操作、文档生成等 Skill
opencode.css                # VSCode Markdown Preview 暗色主题
```

## 使用方式

本仓库作为 Claude Code 插件市场源使用，插件通过 `marketplace.json` 注册并分发。
