# Concept Visualizer Agent

**海纳百川的博学家Agent** - 将文章转化为科学风格概念图，同时自动学习并扩充理论框架知识库。

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 核心特性

- **自动学习** - 从每篇文章中发现新理论框架，知识库越用越丰富
- **开放式框架库** - 内置8+理论框架，支持YAML扩展
- **多图表类型** - 金字塔、网络图、流程图、地形图等10+种
- **多模型支持** - Google/OpenAI/Anthropic/Stability/Ollama
- **统一视觉风格** - 技术蓝图风格的专业概念图

## 快速开始

### 安装

```bash
git clone https://github.com/yourusername/concept-viz-agent.git
cd concept-viz-agent
pip install -r requirements.txt
```

### 配置API Key

```bash
# Google AI Studio (默认已配置)
export GOOGLE_API_KEY="your-key"

# 可选：其他提供商
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

### 使用

```bash
# 一键生成概念图（自动学习新框架）
python agent.py /pipeline your_article.md

# 交互模式
python agent.py
```

## Workflow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  /discover   │ →  │  /analyze    │ →  │    /map      │ →  │   /design    │ →  │  /generate   │
│  框架发现    │    │   分析文章   │    │  框架映射    │    │  可视化设计  │    │   生成图像   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       ↓                   ↓                   ↓                   ↓                   ↓
   学习新框架          提取概念            映射理论            设计图表            AI生图
   扩充知识库          关键引文            生成洞察            生成提示词           保存文件
```

## 命令参考

### 核心技能

| 命令 | 功能 |
|------|------|
| `/pipeline <文章> [输出目录]` | 一键执行完整workflow，自动学习新框架 |
| `/pipeline <文章> --no-learn` | 跳过框架学习，仅生成图片 |
| `/discover <文章>` | 专注于框架发现，扩充知识库 |
| `/analyze <文章>` | 分析文章，提取核心概念 |
| `/map` | 将概念映射到理论框架 |
| `/design` | 生成可视化设计方案 |
| `/generate` | 生成图像 |

### 知识管理

| 命令 | 功能 |
|------|------|
| `/frameworks` | 列出所有理论框架 |
| `/frameworks show <id>` | 显示框架详情 |
| `/frameworks add <id>` | 交互式添加新框架 |
| `/charts` | 列出所有图表类型 |
| `/styles` | 列出所有视觉风格 |
| `/providers` | 列出所有模型提供商 |
| `/reload` | 重新加载配置 |

### 状态与导出

| 命令 | 功能 |
|------|------|
| `/status` | 查看当前状态 |
| `/export <文件名>` | 导出结果为JSON |
| `/clear` | 清除上下文 |
| `/help` | 显示帮助 |

## 内置理论框架

| 框架 | 描述 | 适用场景 |
|------|------|---------|
| **Agapism** | 通过吸引/内在驱动实现发展 | 内在动机、价值认同 |
| **Anancism** | 通过规则/约束实现控制 | 硬性规则、机械约束 |
| **Goodhart's Law** | 度量与目标的差距问题 | 优化陷阱、指标失效 |
| **Moloch Trap** | 协调失败导致集体非理性 | 竞争困境、博弈问题 |
| **Participatory Knowing** | 通过身份认同理解 | 身份构建、内化价值 |
| **Multi-Scale Alignment** | 多层级目标协调 | 层级结构、优先级 |
| **Circuit Breaker** | 检测异常并中断的机制 | 安全机制、自检系统 |
| **Attractor Dynamics** | 系统趋向某状态的倾向 | 吸引子、稳定状态 |

*框架库会随着使用自动扩充*

## 图表类型

| 类型 | 名称 | 适用场景 |
|------|------|---------|
| `pyramid` | 金字塔图 | 层级、优先级 |
| `comparison` | 对比图 | 二元对比 |
| `network` | 网络图 | 系统关系 |
| `flowchart` | 流程图 | 过程、决策 |
| `terrain` | 地形图 | 优化、权衡 |
| `attractor` | 吸引子图 | 收敛、吸引 |
| `timeline` | 时间线 | 时序、演进 |
| `venn` | 韦恩图 | 集合、重叠 |
| `matrix` | 矩阵图 | 分类、象限 |
| `cycle` | 循环图 | 循环、反馈 |

## 扩展指南

### 添加理论框架

在 `frameworks/` 目录创建YAML文件：

```yaml
# frameworks/my_framework.yaml
id: my_framework
name: "我的框架 (My Framework)"
name_en: "My Framework"
origin: "来源"
description: "框架描述"
description_en: "English description"
keywords:
  - keyword1
  - keyword2
visual_elements:
  - element1
  - element2
use_when: "适用场景"
```

### 添加图表类型

在 `chart_types/` 目录创建YAML文件：

```yaml
# chart_types/my_chart.yaml
id: my_chart
name: "我的图表"
name_en: "My Chart"
description: "图表描述"
best_for:
  - scenario1
  - scenario2
template: "视觉模板描述"
layout: "布局方式"
elements:
  - element1
  - element2
```

### 配置模型提供商

支持的提供商：

| 提供商 | 文本生成 | 图像生成 | 配置方式 |
|--------|---------|---------|---------|
| Google AI Studio | ✅ Gemini | ✅ Imagen | 默认启用 |
| OpenAI | ✅ GPT-4o | ✅ DALL-E 3 | OPENAI_API_KEY |
| Anthropic | ✅ Claude | ❌ | ANTHROPIC_API_KEY |
| Stability AI | ❌ | ✅ SDXL | STABILITY_API_KEY |
| Ollama | ✅ 本地模型 | ❌ | 本地运行 |

## 项目结构

```
concept-viz-agent/
├── agent.py                 # 主入口
├── config.py                # 配置文件
├── requirements.txt
├── README.md
│
├── frameworks/              # 📂 可扩展理论框架
│   ├── example_custom_framework.yaml
│   └── ... (自动学习的框架)
│
├── chart_types/             # 📂 可扩展图表类型
│   └── example_custom_chart.yaml
│
├── lib/
│   ├── api.py               # 多模型API客户端
│   └── registry.py          # 开放式注册系统
│
├── skills/
│   ├── analyze.py           # /analyze 分析文章
│   ├── map_framework.py     # /map 框架映射
│   ├── design.py            # /design 可视化设计
│   ├── generate.py          # /generate 图像生成
│   ├── discover.py          # /discover 框架发现
│   └── pipeline.py          # /pipeline 完整流水线
│
└── output/                  # 输出目录
    └── run_YYYYMMDD_HHMMSS/
        ├── 00_discover.json
        ├── 01_analyze.json
        ├── 02_map.json
        ├── 03_design.json
        ├── 04_generate.json
        ├── prompts.md
        ├── report.md
        └── images/
```

## 示例输出

### 生成的概念图示例

使用 `/pipeline` 处理文章后，会生成类似以下风格的概念图：

- 米色网格纸背景（工程图纸风格）
- 红色大写标题
- 蓝色/棕色配色方案
- 专业学术图表风格

### 框架学习示例

```
==================================================
🎓 FRAMEWORK DISCOVERY & LEARNING
==================================================
🔬 正在分析文章中的理论框架...
✓ 发现 2 个新框架
✓ 匹配 1 个已有框架
  📚 新增框架: Principal Hierarchy (principal_hierarchy)
  📚 新增框架: Contextual Interpretation (contextual_interpretation)
==================================================
📊 学习完成:
   新增框架: 2
   框架库总数: 11
==================================================
```

## 设计理念

### 海纳百川

Agent的设计理念是成为一个**博学的哲学家、科学家、方法论家**：

1. **开放式知识库** - 框架和图表类型都可以通过YAML文件扩展
2. **自动学习** - 每次处理文章都会尝试发现新的理论框架
3. **知识积累** - 学到的框架自动持久化，知识库随使用不断丰富
4. **跨学科** - 涵盖哲学、系统论、认知科学、工程模式等多个领域

### 理论框架映射

Agent的独特价值在于将抽象概念映射到科学/哲学方法论：

- 不只是提取要点，而是**用理论框架重新诠释**
- 生成的图表具有**学术深度和方法论洞察**
- 让概念可视化不只是美观，更是**思维工具**

## License

MIT License

## Contributing

欢迎贡献新的理论框架和图表类型！

1. Fork 本仓库
2. 在 `frameworks/` 或 `chart_types/` 添加YAML文件
3. 提交 Pull Request

## Acknowledgments

- Google AI Studio for Gemini API
- Anthropic for Claude
- OpenAI for GPT-4 and DALL-E
