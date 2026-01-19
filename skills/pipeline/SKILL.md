---
name: pipeline
description: 将文章转化为概念可视化图。当用户要求生成概念图、可视化文章、或一键处理文章时使用。
allowed-tools: Bash, Read, Write
user-invocable: true
---

# Concept Visualization Pipeline

## 功能
将文章转化为科学风格的概念可视化图，包含：
1. 框架发现 - 自动识别文章中的理论框架
2. 文章分析 - 提取核心概念和关系
3. 框架映射 - 将概念映射到理论框架
4. 可视化设计 - 生成图像提示词
5. 图像生成 - 调用 AI 生成 4K 概念图

## 使用方法

运行以下命令：

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/pipeline $ARGUMENTS --style=blueprint"
```

## 参数说明
- 第一个参数：文章文件路径（必需）
- `--style=xxx`：视觉风格（可选，默认 blueprint）
- `--no-learn`：跳过框架学习（可选）

## 输出
- `output/run_时间戳/` 目录，包含：
  - JSON 中间结果
  - 生成的概念图（4K）
  - prompts.md 和 report.md
