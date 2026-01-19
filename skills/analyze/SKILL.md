---
name: analyze
description: 分析文章提取核心概念。当用户只想分析文章、不需要生成图像时使用。
allowed-tools: Bash, Read
user-invocable: true
---

# Article Analysis

单独分析文章，提取核心概念、关键引文和主题。

## 快速使用

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/analyze $ARGUMENTS"
```

## 参数
- 第一个参数：文章文件路径（必需）

## 输出
JSON 格式分析结果，包含：
- `main_theme`: 主题
- `key_concepts`: 核心概念列表
- `key_quotes`: 关键引文

适合调试或只需要分析结果的场景。
