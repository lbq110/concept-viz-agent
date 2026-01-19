---
name: frameworks
description: 查看和管理理论框架库。当用户想要查看已有框架、添加新框架、或了解框架详情时使用。
allowed-tools: Bash, Read
user-invocable: true
---

# Framework Management

管理理论框架知识库。

## 快速使用

```bash
# 列出所有框架
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks"

# 查看框架详情
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks show <framework_id>"

# 添加新框架
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks add"
```

## 框架存储
`frameworks/` 目录下的 YAML 文件。

详细说明见 [INSTRUCTIONS.md](./INSTRUCTIONS.md)
