---
name: pipeline
description: 将文章转化为概念可视化图。当用户要求生成概念图、可视化文章、或一键处理文章时使用。
allowed-tools: Bash, Read, Write
user-invocable: true
---

# Concept Visualization Pipeline

一键将文章转化为 4K 科学风格概念图。

## 快速使用

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/pipeline $ARGUMENTS --style=blueprint"
```

## 参数
- 第一个参数：文章文件路径（必需）
- `--style=xxx`：视觉风格（blueprint/modern/academic/creative）
- `--no-learn`：跳过框架学习

## 输出
`output/run_时间戳/` 目录，包含 JSON 结果、概念图、报告。

详细说明见 [INSTRUCTIONS.md](./INSTRUCTIONS.md)
