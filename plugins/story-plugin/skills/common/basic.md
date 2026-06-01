# 使用约定（所有 story-* skill 共享）

任意 `story-*` skill 在执行第一步动作前，**必须**加载本文件（同会话已读则跳过）。子 skill 在 SKILL.md 顶部统一使用：

> **前置**：加载 `${CLAUDE_SKILL_DIR}/../common/basic.md`（同会话已读则跳过）。

涉及代码规范或设计原则的 skill 可附加加载 `${CLAUDE_SKILL_DIR}/../common/gamedesign.md`。

## 路径铁律（贯穿全文）

1. cwd 必须通过 `pwd`（PowerShell 下 `Get-Location`）显式取得，禁止凭印象、凭历史会话、凭 plugin 安装路径猜测。
2. 所有 `.agent/...` 路径以**相对路径**形式基于 cwd 解析；工具签名要求绝对路径时，由 Step 0 取到的 cwd 现场拼接并逐字校对。
3. 路径中**禁止出现 `..`**；出现即视为路径错误，停止动作并重新基于 cwd 计算。
4. **嵌套 `.agent` 警示**：若 cwd 父目录也存在 `.agent`，**绝不**以父目录为项目根；项目根永远等于 Step 0 取到的 cwd。

## 运行时条件加载（加载本文件后判断执行）

当本文件被加载后，**严格按以下顺序**判断并执行，**禁止跳步或乱序**：

### Step 0（阻断性前置，必须最先执行）
1. 执行 `pwd`，结果作为后续所有 `.agent/...` 路径的解析基准。
2. 使用 Read 工具读取**相对路径** `.agent/milestones.yaml`；若文件不存在，**报错停止**，提示用户执行 `/story-milestone` 创建。
3. 读取成功后，向用户输出：`📍 当前 milestone: <current>`。
4. **只有完成上述三步后**，才可执行任何 slug 检索或文件操作。

### Step 0.5（写入前强制校验，覆盖 Write / Edit / mkdir / Bash 等所有落盘动作）
1. 写入路径必须以 `.agent/` 开头的相对路径传入；遵循「路径铁律」。
2. mkdir 与 Write 必须使用同一基准——前者用相对，后者也必须用相对，**严禁**中途切换为绝对路径。

### Step 1（条件加载）
| 条件 | 动作 |
|------|------|
| 任务涉及 C++ 代码（设计、实现、Review） | **必须**加载工程目录下 `.agent/library/common/ue5-cpp-rule.md` |
| 工程目录下存在 `.agent/library/overall.md` | **必须**加载该文件作为项目全局上下文 |

以上加载遵循「同会话已读则跳过」原则。

# 目录与 Milestone

核心流转：原始需求 → TDD → 需求N → 总览；忽略 wiki 与 archive 目录。

```
D:\Work\.agent
├── milestones.yaml
├── library/
└── story/
    ├── 切片1/                       ← milestone 目录
    │   ├── 2026-5-20_怪物推挤/      ← slug 目录
    │   │   ├── wiki/
    │   │   ├── archive/
    │   │   ├── Review/
    │   │   │   └── 需求1_代码Review.md
    │   │   ├── TDD_怪物推挤.md
    │   │   ├── 需求1_需求描述.md
    │   │   ├── 总览.md
    │   │   └── 原始需求.md
    │   └── 临时快速需求/
    └── MS10/                        ← 另一个 milestone
        └── 2026-4-15_基础战斗/
```

## Milestone 配置（`.agent/milestones.yaml`）

```yaml
current: 切片1
milestones:
  切片1:
    created: 2026-05-20
  MS10:
    created: 2026-04-15
```

- `current` 指向当前活跃的 milestone，所有 slug 操作默认在该 milestone 目录下执行。

## Slug 检索流程（所有 story-* skill 共享）

定位、验证、匹配 Slug 或 Story 目录时，**必须**按以下流程执行，严禁绕过：

1. **确定目标 milestone**：
   - 若用户输入中提及了已知的 milestone 名称（匹配 YAML 中的条目），则在该 milestone 目录下操作。
   - 若用户提及的 milestone 名称不存在于 YAML，**直接报错停止**。
   - 若用户未指定 milestone，使用 YAML 的 `current` 值。
2. **检索命令模板**（强制，禁止修改；遵循「路径铁律」）：在当前工作目录执行
   ```bash
   fd . .agent/story/<milestone>/ -t d --max-depth 1
   ```
   再用 `rg -i "<关键词>"` 在结果中过滤。
3. **兜底**：若 `.agent/story/<milestone>/` 不存在，直接告知用户并停止，不要扩大搜索范围。
4. **Slug 命中后**：进入子流程前，**至少**读取该 slug 目录下的 `原始需求.md` 与 `总览.md`（若存在），并列出已有需求点 / Review 文件，作为后续操作的上下文基线。

## 文档规则
- 需求标号总是为自增，例如，`需求1`, `需求2`
- 一个slug下总是只有一个`总览.md`

## Slug命名规则
- 提炼 ≤5 词中文短语作为目录名（如 `怪物推挤`），向用户确认。
- 目录格式为 `日期_需求slug`，日期为生成该slug的时间，例如 `2026-4-30_怪物推挤`
- 在开启新任务或缺失 slug 上下文时，必须向用户确认当前的 slug 名称。

# 文档先行规则
任何实质性的变更（包括但不限于逻辑分支、数据结构、接口签名、UE元数据等），必须先更新对应的需求文档及总览，再修改源代码。
修改后在文档末尾追加：<YYYY-MM-DD>：[类型] 变更简述（严禁大段记录）。
