# Git Plugin

Git 工作流辅助插件，提供提交、README 更新和版本号管理功能。

**版本**: 1.1.3

## 功能特性

- `/git-commit` Git 提交
- `/readme-update` 根据项目结构自动生成或更新 README.md
- `/update-version` 根据改动上下文更新 plugin.json 版本号，同步 README，可选提交推送

## 项目结构

```
git-plugin/
├── .claude-plugin/
│   └── plugin.json           # 插件元信息
└── skills/
    ├── git-commit/           # Git 提交
    ├── readme-update/        # README 生成/更新
    └── update-version/       # 版本号管理
```
