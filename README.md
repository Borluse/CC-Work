# CC-Work

Claude Code 插件市场仓库，收录面向游戏开发与工作流的插件与 Agent。

通过 `.claude-plugin/marketplace.json` 注册并分发。

## 插件一览

| 插件 | 版本 | 类别 | 说明 |
|------|------|------|------|
| [story-lite](#story-lite-v028) | 0.2.8 | 工作流 | 轻量需求文档同步维护与 HTML 工具生成 |
| [git-plugin](#git-plugin-v114) | 1.1.4 | 开发工具 | Git 提交、README、版本号 |
| [p4-plugin](#p4-plugin-v113) | 1.1.3 | 开发工具 | P4 pending CL 代码审查 |
| [obsidian-plugin](#obsidian-plugin-v100) | 1.0.0 | 开发工具 | Obsidian vault 管理与文档生成 |

---

### story-lite (v0.2.8)

轻量需求文档维护。Agent 干活时同步更新需求 / 设计 / Review 文档，设计前检索 library，完成后可沉淀可复用知识；附带需求转单文件 HTML 工具能力。需显式点名使用（如 `@story-lite`）。

**Skills**

| Skill | 说明 |
|-------|------|
| `story-lite` | 轻量工作流：总览规划 → 逐点设计 → 实现（文档同步）→ Review → 总结 |
| `story-lite-learn` | 提炼可复用方法论指引（厚度受限），经确认后写入 library |
| `story-lite-wiki` | 从需求文档生成或迭代团队 Wiki（export 导出 / tdd 按需求点讨论方案） |
| `story-show` | 将需求转换为静态说明页或可修改参数的交互式 HTML 测试工具 |

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
