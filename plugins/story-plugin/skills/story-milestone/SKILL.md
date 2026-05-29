---
name: story-milestone
description: "管理 milestone（迭代切片）。TRIGGER: 当用户说'创建milestone'、'切换milestone'、'设置milestone'、'列出milestone'、'重命名milestone'时使用。"
---

- **前置**：加载 `${CLAUDE_SKILL_DIR}/../common/basic.md`（同会话已读则跳过）。

# Milestone 管理

管理 `.agent/milestones.yaml` 和 `.agent/story/<milestone>/` 目录结构。

## YAML 结构

```yaml
current: <当前活跃的 milestone 名>
milestones:
  <name>:
    created: <YYYY-MM-DD>
```

文件位置：`.agent/milestones.yaml`（强制存在，不存在则报错停止）。

## 操作路由

根据用户意图分流到以下操作：

### 操作 1: 创建新 milestone

1. 询问用户 milestone 名称（自由命名，无格式约束）。
2. 检查名称是否已存在于 YAML，已存在则报错。
3. 在 YAML 的 `milestones` 下添加新条目，`created` 为当天日期。
4. 创建目录 `.agent/story/<name>/`。
5. **询问用户**：是否将 `current` 切换到新创建的 milestone？
6. 根据用户回答更新（或不更新）YAML 的 `current` 字段。

### 操作 2: 切换 current

1. 列出 YAML 中所有已有 milestone（名称 + 创建日期）。
2. 用户选择后，更新 YAML 的 `current` 字段。

### 操作 3: 列出所有 milestone

1. 读取 YAML，以表格形式展示所有 milestone：
   - 名称
   - 创建日期
   - 是否为 current（标记 `←`）

### 操作 4: 重命名 milestone

1. 列出所有 milestone，用户选择要重命名的目标。
2. 用户提供新名称，检查不与已有名称冲突。
3. 重命名目录：`.agent/story/<旧名>` → `.agent/story/<新名>`。
4. 更新 YAML 中该条目的 key。
5. 若重命名的是 `current` 指向的 milestone，**自动更新** `current` 为新名称。
