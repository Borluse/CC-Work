# CC-Work

Claude Code 插件市场仓库，收录面向游戏开发与工作流的插件与 Agent。

通过 `.claude-plugin/marketplace.json` 注册并分发。

## 插件一览

| 插件 | 版本 | 类别 | 说明 |
|------|------|------|------|
| [story-plugin](#story-plugin-v443) | 4.4.3 | 工作流 | 需求生命周期：设计 → 实现 → Review → 经验提炼 |
| [story-lite](#story-lite-v0122) | 0.1.22 | 工作流 | 轻量需求文档同步维护 |
| [git-plugin](#git-plugin-v114) | 1.1.4 | 开发工具 | Git 提交、README、版本号 |
| [p4-plugin](#p4-plugin-v113) | 1.1.3 | 开发工具 | P4 pending CL 代码审查 |
| [obsidian-plugin](#obsidian-plugin-v100) | 1.0.0 | 开发工具 | Obsidian vault 管理与文档生成 |

---

### story-plugin (v4.4.3)

需求生命周期管理。入口 `/story` 按意图路由到子 skill；附带 UE5 FPS 代码阅读与审查 Agent。

**Skills**

| Skill | 说明 |
|-------|------|
| `story` | 工作流入口，按描述自动路由 |
| `story-milestone` | Milestone 创建 / 切换 / 列出 / 重命名 |
| `story-tdd` | 大需求拆分，产出 TDD 文档 |
| `story-story` | 整理原始需求，生成 slug 与目录 |
| `story-design` | 单需求点方案设计与设计文档 |
| `story-ask` | 探索答疑（查文档与代码，不产文档） |
| `story-implement` | 按设计文档实现代码 |
| `story-review` | 设计 / 代码 Review |
| `story-consolidate` | 多文档合并为总览，以代码为准校对 |
| `story-wiki` | 从设计 / 总览生成团队 Wiki |
| `story-learn` | 提炼可复用模式写入 library |

**Agents**

| Agent | 说明 |
|-------|------|
| `ue5-expert` | UE5 FPS C++ 代码阅读与分析 |
| `ue5-reviewer` | UE5 FPS C++ 代码审查 |

---

### story-lite (v0.1.22)

轻量需求文档维护。Agent 干活时同步更新需求 / 设计 / Review 文档，设计前检索 library，完成后可沉淀可复用知识。需显式点名使用（如 `@story-lite`）。

**Skills**

| Skill | 说明 |
|-------|------|
| `story-lite` | 轻量工作流：设计前检索 → 实现（文档同步）→ Review → 总结 |
| `story-lite-learn` | 提炼可复用方法论指引（厚度受限），经确认后写入 library |
| `story-lite-wiki` | 从需求/设计/总览生成面向团队的精简 Wiki |

---

### git-plugin (v1.1.4)

Git 与仓库元信息工具。

**Skills**

| Skill | 说明 |
|-------|------|
| `git-commit` | 根据差异生成提交信息并提交 |
| `readme-update` | 按项目结构生成 / 更新 README |
| `update-version` | 更新插件版本号，同步 README，可选提交推送 |

---

### p4-plugin (v1.1.3)

Perforce 工具。

**Skills**

| Skill | 说明 |
|-------|------|
| `p4-review-cl` | 审查 P4 pending changelist |

---

### obsidian-plugin (v1.0.0)

Obsidian vault 管理与技术文档生成。

**Skills**

| Skill | 说明 |
|-------|------|
| `obsidian` | 通过 obsidian-cli 搜索 / 创建 / 移动 / 删除笔记 |
| `docgen` | 从代码生成符合 Obsidian 规范的技术文档 |

---

## 目录结构

```
.claude-plugin/
  marketplace.json          # 市场注册
plugins/
  story-plugin/             # 需求全流程
    agents/                 # UE5 专家 Agent
    skills/                 # 设计、实现、Review、Wiki 等
  story-lite/               # 轻量文档同步
    skills/
  git-plugin/
    skills/
  p4-plugin/
    skills/
  obsidian-plugin/
    skills/
```

## 使用方式

本仓库作为 Claude Code 插件市场源，通过 `marketplace.json` 注册后安装对应插件即可。
