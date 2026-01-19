---
name: discover
description: 从文章中发现新的理论框架。当用户想要分析文章中的理论、发现新框架、扩充知识库时使用。
allowed-tools: Bash, Read
user-invocable: true
---

# Framework Discovery

分析文章，自动发现并学习新的理论框架，扩充知识库。

## 快速使用

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/discover $ARGUMENTS"
```

## 参数
- 第一个参数：文章文件路径（必需）
- `--no-save`：只发现不保存

## 输出
发现的框架自动保存到 `frameworks/` 目录。

详细说明见 [INSTRUCTIONS.md](./INSTRUCTIONS.md)
