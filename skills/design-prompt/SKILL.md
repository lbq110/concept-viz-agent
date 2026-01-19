---
name: design-prompt
description: 生成图像提示词。当用户有分析结果、只需要生成提示词时使用。
allowed-tools: Bash, Read
user-invocable: true
---

# Design Prompt

基于分析/映射结果生成图像提示词。

## 快速使用

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/design $ARGUMENTS"
```

## 参数
- 第一个参数：映射结果 JSON 文件路径（必需）
- `--style=xxx`：视觉风格（可选）

## 输出
JSON 格式设计结果，包含：
- `designs`: 设计方案列表
  - `title`: 标题
  - `chart_type`: 图表类型
  - `image_prompt`: 图像提示词

适合只需要提示词、手动生成图像的场景。
