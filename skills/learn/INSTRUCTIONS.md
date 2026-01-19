# Learn 详细指令

## 功能说明

从已有的示例作品（文章 + 图像）中反向学习，提取框架、图表类型和视觉风格。

### 学习流程

1. **图像分析** - 使用 AI Vision 分析示例图像
2. **知识提取** - 提取候选框架、图表类型、风格
3. **闭环验证**（可选）- 用提取的知识重新生成，验证质量
4. **持久化** - 验证通过后保存到知识库

## 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| 第一个参数 | ✓ | 示例文件夹路径 |
| `--no-verify` | | 跳过闭环验证，直接保存 |
| `--threshold=N` | | 验证通过阈值（默认 70）|

## 示例文件夹结构

```
example_folder/
├── article.md          # 原始文章（必需）
└── images/             # 示例图像（必需）
    ├── image_1.jpg
    ├── image_2.png
    └── ...
```

支持的图像格式：`.jpg`, `.jpeg`, `.png`, `.webp`

## 闭环验证

验证维度（每项 0-100 分）：
- **视觉风格匹配** - 颜色、布局、图形风格
- **图表类型匹配** - 图表结构和元素
- **概念表达匹配** - 核心概念的表达准确度
- **整体质量** - 综合质量评估

平均分 ≥ 阈值才会保存学习结果。

## 输出格式

```json
{
  "learned": {
    "frameworks": [
      {"id": "xxx", "name": "框架名", "saved": true}
    ],
    "styles": [
      {"id": "xxx", "name": "风格名", "saved": true}
    ]
  },
  "verification": {
    "score": 82,
    "threshold": 70,
    "passed": true,
    "details": {
      "visual_style": 85,
      "chart_type": 80,
      "concept_expression": 78,
      "overall_quality": 85
    }
  }
}
```

## 存储位置

- 框架：`frameworks/` 目录
- 风格：`visual_styles/` 目录
- 图表类型：`chart_types/` 目录

## 使用示例

```bash
# 默认（开启验证）
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/learn ./examples/my_folder"

# 跳过验证
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/learn ./examples/my_folder --no-verify"

# 设置验证阈值
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/learn ./examples/my_folder --threshold=80"
```

## 注意事项

- 默认样式（blueprint 等）已锁定，不会被覆盖
- 学习结果以新 ID 保存，不影响现有知识库
- 建议提供 3+ 张示例图像以提高学习质量
