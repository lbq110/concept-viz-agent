---
name: discover
description: 从文章中发现新的理论框架。当用户想要分析文章中的理论、发现新框架、扩充知识库时使用。
allowed-tools: Bash, Read
user-invocable: true
---

# Framework Discovery

## 功能
分析文章，自动发现并学习新的理论框架，扩充框架知识库。

识别范围：
- 哲学概念（实用主义、涌现论等）
- 科学方法论（演绎、归纳、溯因推理）
- 系统论（反馈、吸引子、自组织）
- 物理学概念（全息原理、量子纠错码）
- 等等

## 使用方法

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/discover $ARGUMENTS"
```

## 输出
- 发现的新框架列表
- 自动保存到 `frameworks/` 目录
