# Pipeline 详细指令

## 完整工作流

1. **框架发现** - 自动识别文章中的理论框架，扩充知识库
2. **文章分析** - 提取核心概念、关键引文和主题
3. **框架映射** - 将概念映射到理论框架，生成洞察
4. **可视化设计** - 设计图表类型，生成图像提示词
5. **图像生成** - 调用 AI 生成 4K 概念图

## 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| 第一个参数 | ✓ | 文章文件路径 |
| `--style=xxx` | | 视觉风格：blueprint（默认）、modern、academic、creative |
| `--no-learn` | | 跳过框架学习，只生成图像 |
| `--output=dir` | | 指定输出目录 |

## 视觉风格

| ID | 名称 | 描述 |
|----|------|------|
| `blueprint` | 技术蓝图风格 | Intuition Machine 风格（默认）|
| `modern` | 现代简约风格 | 商业演示 |
| `academic` | 学术论文风格 | 研究内容 |
| `creative` | 创意艺术风格 | 艺术感强 |

## 输出结构

```
output/run_时间戳/
├── 00_discover.json    # 框架发现结果
├── 01_analyze.json     # 文章分析结果
├── 02_map.json         # 框架映射结果
├── 03_design.json      # 可视化设计
├── 04_generate.json    # 生成结果
├── prompts.md          # 图像提示词
├── report.md           # 运行报告
├── run_stats.json      # 执行统计
└── images/             # 生成的图像
```

## 错误处理

- 每步失败会记录到 `run_stats.json`
- 查看 `report.md` 了解执行详情
- 如需重试，可手动运行单步 Skills

## 使用示例

```bash
# 基本使用
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/pipeline article.md"

# 指定样式
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/pipeline article.md --style=modern"

# 跳过学习
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/pipeline article.md --no-learn"
```
