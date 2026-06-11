### 全局Step 0 - 获取全局目录 (当前会话已有信息，则跳过)
**严格按以下顺序**判断并执行，**禁止跳步或乱序**：
1. **显式获取**：必须通过 `pwd`（PowerShell 下 `Get-Location`）获取当前工作目录绝对路径，标记为 `<cwd>`。
   - **禁止**凭印象/历史会话/plugin安装路径猜测。
   - **嵌套防范**：若 `<cwd>` 父目录也存在 `.agent`，不以父目录为项目根；项目根永远等于 `<cwd>`。
2. **统一拼接**：后续所有路径操作**必须**用 `<cwd>/<目标路径>` 拼接。
3. **禁止回退**：路径中**严禁 `..`**；出现则停止动作，重新基于 `<cwd>` 计算。

4. **版本库确认**：查看 `<cwd>/vcs.md`（若存在），确认并输出版本库信息。
5. **Milestone 获取**：Read `<cwd>/.agent/milestones.yaml`；不存在则**报错停止**，提示用户执行 `/story-milestone`。
6. **输出状态**：`📍 当前 milestone: <current>`。
7. **守门员原则**：完成上述步骤后才可执行后续操作。
8. 输出 `.agent` 全局路径

### Step 1（条件加载）
- 涉及 C++ 代码 → **必须**加载 `<cwd>/.agent/library/common/ue5-cpp-rule.md`
- `<cwd>/.agent/library/overall.md` **必须**加载
同会话已读则跳过。

# 目录与 Milestone
核心流转：原始需求 → TDD → 需求N → 总览；忽略 wiki 与 archive 目录。

## Milestone 配置（`.agent/milestones.yaml`）

```yaml
current: 切片1
milestones:
  切片1:
    created: 2026-05-20
  MS10:
    created: 2026-04-15
```

- `current` 指向当前活跃 milestone，所有 slug 操作默认在该 milestone 目录下执行。

## Slug 检索流程（所有 story-* skill 共享）

定位/验证/匹配 Slug 或 Story 目录时，**必须**按以下流程执行：

1. **确定目标 milestone**：
   - 用户提及已知 milestone 名称 → 在该 milestone 目录下操作。
   - 用户提及不存在的 milestone → **报错停止**。
   - 未指定 → 用 YAML `current` 值。
2. **检索命令**（强制，禁止修改；遵循路径铁律）：
   ```bash
   fd . .agent/story/<milestone>/ -t d --max-depth 1
   ```
   再用 `rg -i "<关键词>"` 过滤。
3. **兜底**：`.agent/story/<milestone>/` 不存在 → 告知用户并停止，不扩大搜索。
4. **Slug 命中后**：至少读取 `原始需求.md` 与 `总览.md`（若存在），列出已有需求点/Review 文件作为上下文基线。

## 文档规则
- 需求标号自增：`需求1_具体描述`, `需求2_具体描述`
- 一个 slug 下只有一个 `总览.md`

## Slug命名规则
- 提炼 ≤5 词中文短语作目录名（如 `怪物推挤`），向用户确认。
- 目录格式：`日期_需求slug`，日期为生成时间，如 `2026-4-30_怪物推挤`
- 开启新任务或缺失 slug 上下文时，必须向用户确认 slug 名称。

# 文档先行规则
任何实质性变更（逻辑分支、数据结构、接口签名、UE元数据等），先更新需求文档及总览，再改源代码。
修改后文档末尾追加：<YYYY-MM-DD>：[类型] 变更简述（禁止大段记录）。
