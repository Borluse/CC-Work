---
name: p4-hook-install
description: "Install or remove a project-scoped p4 edit hook (runs p4 edit before editing to unlock read-only Perforce files) into a target project directory for Codex apply_patch and Claude Code Edit/Write/MultiEdit, optionally Cursor. Use when the user asks to install/configure/uninstall the p4 edit hook for a directory, e.g. 给某目录装 p4 hook、配置 p4 编辑解锁、安装/卸载 p4 hook。"
---

# p4-hook-install

把「编辑前 p4 edit」hook 安装/卸载到指定项目目录。hook 只在目标项目内生效（项目级配置），不写用户级配置。

## 用法

```bash
python3 <本技能目录>/scripts/install.py install <目标目录> [--cursor]
python3 <本技能目录>/scripts/install.py uninstall <目标目录> [--cursor]
```

`<本技能目录>` 即 SKILL.md 所在目录（插件内为 `skills/p4-hook-install`）。install 默认安装 Codex + Claude Code 双端；`--cursor` 额外安装 Cursor。

## 流程

1. 确认目标目录存在，必要时向用户复述一次目录。
2. 运行 `install.py install <目标目录> [--cursor]`。
3. 展示脚本输出的安装清单与信任说明：
   - Codex：目标项目需处于 trusted；hook 首次需在 `/hooks` 审查并信任。
   - Claude Code：项目级 hook 首次运行可能弹审批（配置已预置 `permission: "allow"`）。
4. 卸载运行 `install.py uninstall <目标目录> [--cursor]`，只移除本技能写入的条目与脚本。

## 行为约定

- 幂等：重复 install 不产生重复条目；内容有变化时先打印 diff 再覆盖。
- 合并：`.claude/settings.json` 等已存在时保留其他键；`.codex/hooks.json` 保留其他事件与条目。
- 可逆：uninstall 只删除由本技能管理（命令包含目标项目 hook 脚本路径）的条目与脚本文件，其余配置保留。
- 绝对路径：目标项目可能不是 git 仓库，配置写入项目内脚本的绝对路径；项目移动后重跑 install。

## 验证

模拟 stdin 喂给安装后的 hook 脚本（对只读文件会尝试 `p4 edit`，失败仅告警、退出码 0）：

```bash
echo '{"cwd":"<目标目录>","tool_name":"apply_patch","tool_input":{"command":"*** Update File: test.txt"}}' | python3 <目标目录>/.codex/hooks/p4-edit-hook.py
```

注意：目标机器需安装 p4（在 PATH 中）或设置 `CODEX_P4_HOOK_P4` 指向 p4 可执行文件；未装 p4 时 hook 告警放行，不阻断编辑。
