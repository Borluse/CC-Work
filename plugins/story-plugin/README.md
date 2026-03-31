# Story Plugin

需求生命周期管理插件：通过 `/story` 路由入口，将需求从设计→实现→Review→经验沉淀的完整流程拆分为独立的 skill。

**版本**: 2.11.0

## 功能特性

- `/story` 路由入口，根据用户意图自动分发到子流程
- `/story-design` 需求分析与设计文档生成
- `/story-implement` 根据设计文档实现代码
- `/story-review` 代码审查（通过 ue5-reviewer subagent）
- `/story-learn` 从设计或实现中提炼可复用方法论

## 项目结构

```
story-plugin/
├── .claude-plugin/
│   └── plugin.json          # 插件元信息
├── agents/
│   ├── ue5-expert.md         # UE5 专家 agent
│   └── ue5-reviewer.md       # UE5 审查 agent
└── skills/
    ├── story/                # 路由入口
    ├── story-design/         # 需求设计
    ├── story-implement/      # 代码实现
    ├── story-learn/          # 经验提炼
    └── story-review/         # 代码审查
```
