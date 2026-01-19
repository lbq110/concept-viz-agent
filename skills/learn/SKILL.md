---
name: learn
description: 从已有示例作品中学习。当用户有现成的文章+图像示例，想要提取风格和框架时使用。
allowed-tools: Bash, Read
user-invocable: true
---

# Learn from Examples

从示例作品中反向学习框架、图表类型和视觉风格。

## 快速使用

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/learn $ARGUMENTS"
```

## 参数
- 第一个参数：示例文件夹路径（必需）
- `--no-verify`：跳过验证直接保存
- `--threshold=70`：验证阈值

## 示例文件夹结构
```
example_folder/
├── article.md
└── images/
    └── *.jpg / *.png
```

详细说明见 [INSTRUCTIONS.md](./INSTRUCTIONS.md)
