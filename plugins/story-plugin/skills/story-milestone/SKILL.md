---
name: story-milestone
description: "管理 milestone（迭代切片）。TRIGGER: 当用户说'创建milestone'、'切换milestone'、'设置milestone'、'列出milestone'、'重命名milestone'时使用。"
---

- @../common/basic.md

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

### 操作 1: 创建新 milestone

1. 询问 milestone 名称（自由命名）。
2. 检查名称是否已存在，已存在报错。
3. YAML `milestones` 下添加新条目，`created` 为当天。
4. 创建目录 `.agent/story/<name>/`。
5. 询问是否将 `current` 切换到新 milestone。
6. 根据回答更新 YAML `current`。

### 操作 2: 切换 current

1. 列出所有 milestone（名称 + 创建日期）。
2. 用户选择后更新 YAML `current`。

### 操作 3: 列出所有 milestone

1. 读取 YAML，表格展示：名称、创建日期、是否 current（标记 `←`）。

### 操作 4: 重命名 milestone

1. 列出所有 milestone，用户选择目标。
2. 用户提供新名称，检查不冲突。
3. 重命名目录：`.agent/story/<旧名>` → `.agent/story/<新名>`。
4. 更新 YAML 条目 key。
5. 若重命名的是 `current` 指向的 → 自动更新 `current`。
