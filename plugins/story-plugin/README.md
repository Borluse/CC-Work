# story-plugin

需求生命周期管理插件：通过 `/story` 路由入口，将需求从设计到实现再到 Review 的完整流程拆分为独立的 skill。

- 版本：3.8.0
- 作者：borlusezhao
- 关键词：需求分析、工作流、设计、实现、review

## 功能特性

- **统一入口**：`/story` 根据用户描述自动路由到对应子流程
- **大需求拆分**：`/story-tdd` 拆分大需求并产出 TDD 文档
- **原始需求清理**：`/story-story` 整理粘贴的原始需求文本
- **方案设计**：`/story-design` 单个需求点的设计与文档产出
- **编码实现**：`/story-implement` 根据设计文档落地代码
- **审查 Review**：`/story-review` Review 设计文档或代码实现
- **文档整合**：`/story-consolidate` 多份需求文档合并为以代码为准的总览
- **Wiki 输出**：`/story-wiki` 从总览生成面向团队的精简 Wiki
- **方法论沉淀**：`/story-learn` 从对话或设计文档提炼可复用模式写入 library

## 路由表

| 路由目标 | 适用场景 |
|---|---|
| `/story-tdd` | 拿到一个大需求（如新 Boss、新系统），需要整体理解、拆分子需求、产出 TDD 文档 |
| `/story-story` | 用户粘贴一段原始需求文本，需要清理格式、生成 slug、存入需求目录 |
| `/story-design` | 对单个需求点进行需求理解、方案设计、产出设计文档 |
| `/story-implement` | 设计文档已就绪，开始写代码（含临时需求） |
| `/story-review` | Review 设计文档或代码实现 |
| `/story-consolidate` | 多份需求文档合并为一份总览，以实际代码为准去重校对 |
| `/story-wiki` | 从设计/总览文档生成面向团队的精简 Wiki |
| `/story-learn` | 从对话上下文或 story 文档中提炼可复用模式写入 library |

## 项目结构

```
story-plugin/
├── .claude-plugin/
│   └── plugin.json              # 插件元信息与 skill 列表
├── agents/
│   ├── ue5-expert.md            # UE5 专家 subagent
│   └── ue5-reviewer.md          # UE5 Review subagent（强制用于 /story-review）
└── skills/
    ├── common/
    │   ├── basic.md             # 各 skill 通用基础信息
    │   └── gamedesign.md        # 游戏设计相关参考
    ├── story/                   # /story 路由入口
    ├── story-tdd/               # 大需求拆分 + TDD
    ├── story-story/             # 原始需求清理
    ├── story-design/            # 单点设计
    ├── story-implement/         # 编码实现
    ├── story-review/            # 审查
    ├── story-consolidate/       # 文档整合
    ├── story-wiki/              # Wiki 生成
    └── story-learn/             # 方法论沉淀
```

## 使用方式

在 Claude Code 中通过插件市场启用本插件后，直接对话触发：

- 输入 `/story <描述>`：由路由自动选择子 skill
- 或直接调用具体 skill：`/story-design`、`/story-implement` 等

各 skill 会按需加载 `skills/common/basic.md` 与项目内的 `.agent/library/`、`.agent/references/` 等上下文。

## 约定

- 所有产出文档默认中文
- `/story-implement` 强制加载 `.agent/library/common/ue5-cpp-rule.md` 作为代码规范
- `/story-review` 强制使用 `ue5-reviewer` agent
- `/story-wiki` 强制使用 `story:ue5-expert` subagent
