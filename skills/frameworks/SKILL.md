---
name: frameworks
description: 查看和管理理论框架库。当用户想要查看已有框架、添加新框架、或了解框架详情时使用。
allowed-tools: Bash, Read
user-invocable: true
---

# Framework Management

## 功能
管理理论框架知识库，支持：
- 列出所有框架
- 查看框架详情
- 交互式添加新框架

## 使用方法

### 列出所有框架
```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks"
```

### 查看框架详情
```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks show <framework_id>"
```

### 添加新框架
```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks add"
```

## 框架存储位置
- `frameworks/` 目录下的 YAML 文件
