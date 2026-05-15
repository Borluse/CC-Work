---
name: story-review
description: "Review 需求或者代码。TRIGGER: 当用户说'开始 Review'、'审查代码'、'检查实现'时使用。"
---


- **必须** 加载 skills/common/basic.md 获取必要信息
**强制要求** ：使用 `ue5-reviewer` agent 进行Review

- 找用户了解是review代码还是review需求

# Step 1. Review
- 读取需求文档，理解功能需求和实现方案
- 所有的条目按统一的标号。例如 R1, R2, R3

- 如果是review设计，参考 `./references/design-review.md`
- 如果是review代码，参考 `./references/code-review.md`

- 等待用户逐项确认。**严禁**自行决定修改内容。

# Step 2 生成报告

报告输出格式为 HTML，统一存放在 `.agent/story/<Slug>/Review/`。

## 代码 Review

按本 skill 的固定模板生成视觉一致的报告：

1. 按 `./report-html/example.yaml` 的字段骨架，生成一份 YAML 数据文件，命名为 `需求<N>_代码Review.yaml`，临时保存在 Review/ 目录。
2. 字段映射规则见 `./references/code-review.md` 末尾的「输出 YAML 字段映射」章节。
3. 调用渲染脚本（同目录的相对路径）：
   ```
   python "<skill-dir>/report-html/generate.py" <Review 目录>/需求<N>_代码Review.yaml <Review 目录>/需求<N>_代码Review.html
   ```
4. 渲染成功后**删除中间 YAML**，仅保留 `需求<N>_代码Review.html`。
5. 向用户简要总结，并附 HTML 文件路径。

## 设计 Review

仍按自由 HTML 模式产出 `需求<N>_设计Review.html`：
- 含 `<!DOCTYPE html>` 与内联样式，无外部依赖
- 不使用任何固定模板，根据本次 Review 的实际内容自由组织页面结构与视觉样式
- 必须包含的信息（结构与命名自定）：
  - 关联需求、Review 类型、日期、涉及文件
  - 总体评价
  - 问题清单：每条与 Step 1 的统一编号（R1/R2/...）对应，并标注严重程度（必须 / 建议 / 可选）
  - 结论（是否通过 / 是否需重新 Review）
- 生成后向用户简要总结，并附上 HTML 文件路径。

# Step 3 提醒用户
- 提示用户Review文档，并询问哪些问题需要修复。

# Step 4 修复问题
- 修复问题后，更新文档。并重新输出文档报告。回到Step 3
- 如果所有问题都修复了，结束Review。