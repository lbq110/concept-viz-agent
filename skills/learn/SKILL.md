---
name: learn
description: 从已有示例作品中学习。当用户有现成的文章+图像示例，想要提取风格和框架时使用。
allowed-tools: Bash, Read
user-invocable: true
---

# Learn from Examples

## 功能
从已有的示例作品中反向学习：
1. 用 AI Vision 分析图像
2. 提取候选框架、图表类型、风格
3. 闭环验证（可选）
4. 保存到知识库

## 使用方法

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/learn $ARGUMENTS"
```

## 参数
- 示例文件夹路径（必需）
- `--no-verify`：跳过验证直接保存
- `--threshold=70`：验证通过分数阈值

## 示例文件夹结构
```
example_folder/
├── article.md
└── images/
    ├── image_1.jpg
    └── image_2.jpg
```
