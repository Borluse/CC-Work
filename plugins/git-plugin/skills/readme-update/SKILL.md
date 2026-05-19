---
name: readme-update
description: "根据当前工作目录的代码结构和内容，自动生成或更新 README.md 文件。Use when the user says '更新 README' / '生成 README' / '写 README' / 'update readme'，或要求根据项目内容刷新 README 时触发。"
---

扫描当前工作目录的项目结构、代码文件、配置文件等，自动生成或更新该目录下的 `README.md`。

## 工作流程

### 1. 收集项目信息

通过 Bash 执行以下命令收集信息：

```bash
# 项目文件结构（仅展示前两层）
fd --max-depth 2 --type f

# 查找包管理/构建配置文件
fd -d 1 "(package\.json|Cargo\.toml|go\.mod|pyproject\.toml|setup\.py|CMakeLists\.txt|Makefile|\.csproj|pom\.xml|build\.gradle|\.uproject|tsconfig\.json|vite\.config|webpack\.config|docker-compose|Dockerfile)" --type f

# 查找已有 README
fd "README" --max-depth 1 --type f

# 如果是 git 仓库，获取远程地址
git remote -v 2>/dev/null | head -1
```

### 2. 读取关键文件

根据第 1 步的结果，读取以下文件（如存在）：

- **包管理文件**（`package.json`、`Cargo.toml`、`go.mod`、`pyproject.toml` 等）：提取项目名、描述、依赖、脚本命令
- **已有 README.md**：了解现有内容，保留用户手写的自定义内容
- **入口文件**（`src/main.*`、`src/index.*`、`app.*` 等）：了解项目核心功能
- **配置文件**（`docker-compose.yml`、`.env.example`、`tsconfig.json` 等）：了解运行环境和配置

**重要**：如果已有 README.md，必须先 Read 再决定更新策略。

### 3. 分析项目并启动子任务（如项目较大）

如果项目文件较多（>20 个源文件），**必须**启动一个 `general-purpose` 子任务来分析代码。

子任务 prompt 示例：

```
请分析以下项目目录的代码结构：<当前目录>

文件列表：
<第1步获取的文件列表>

要求：
- 读取入口文件和关键模块，理解项目的核心功能
- 识别项目的技术栈和框架
- 总结项目的主要功能模块
- 以结构化文本返回分析结果，不要写入任何文件
```

如果项目较小，可以直接在主对话中读取分析。

### 4. 生成 / 更新 README.md

根据收集到的信息生成 README。
只更新或生成工程根目录下的README文件

**如果是全新生成**，使用以下结构：

```markdown
# 项目名称

简要描述（1-2 句话说明项目是什么、解决什么问题）。

## 功能特性

- 特性 1
- 特性 2
- ...

## 技术栈

- 框架/语言
- 关键依赖

## 快速开始

### 环境要求

- Node.js >= xx / Python >= xx / ...

### 安装

```bash
安装命令
```

### 运行

```bash
启动命令
```

## 项目结构

```
目录结构概览（关键目录，不超过 2 层）
```

## 配置说明

（如有 .env.example 或配置文件，说明关键配置项）

## License

（如果 LICENSE 文件存在，注明类型）
```

**如果是更新已有 README**：

- 保留用户手写的自定义章节（如 Contributing、Acknowledgments 等）
- 仅更新可自动推导的章节（项目结构、技术栈、安装命令等）
- 不要删除现有内容，只补充缺失的部分
- 对于用户编写的描述性文字，保持原样，不要替换

## 注意事项

- README 语言默认跟随项目中已有 README 的语言；如无已有 README，使用中文
- 不要添加不存在的功能或虚构的信息，所有内容必须来自实际代码
- 保持简洁，避免废话
- 不要添加 badge/shield 图标，除非已有 README 中存在
- 如果项目有 `scripts` 字段（package.json）或 Makefile targets，列出常用命令
