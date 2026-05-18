---
name: story-story
description: 整理清理需求文档
---

- **必须** 加载 `${CLAUDE_SKILL_DIR}/../common/basic.md`

根据用户提供的需求内容，作如下事情
1. 清理格式
2. 去除无用的内容，如无效的贴图链接等。
3. 生成一个slug，并询问用户
4. 将整理后的内容写入到slug下的原始需求文件中。
