# Frameworks 详细指令

## 功能说明

管理理论框架知识库，支持查看、搜索和添加框架。

## 子命令

### 列出所有框架

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks"
```

输出示例：
```
📚 理论框架库 (12 个)
──────────────────────────────
1. agapism          - 爱智主义 (Agapism)
2. anancism         - 必然主义 (Anancism)
3. attractor        - 吸引子动力学 (Attractor Dynamics)
4. circuit_breaker  - 断路器模式 (Circuit Breaker)
...
```

### 查看框架详情

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks show <framework_id>"
```

输出示例：
```yaml
id: agapism
name: "爱智主义 (Agapism)"
name_en: "Agapism"
origin: "Charles Sanders Peirce"
description: "通过吸引/爱/内在驱动实现发展的进化理论"
keywords:
  - 内在动机
  - 价值认同
  - 自发秩序
visual_elements:
  - 向心吸引
  - 内在光源
  - 有机生长
use_when: "描述内在动机、价值认同、自然涌现的场景"
```

### 添加新框架

```bash
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks add"
```

进入交互式添加模式，依次输入：
- 框架 ID（英文下划线）
- 中文名称
- 英文名称
- 来源
- 描述
- 关键词（逗号分隔）
- 视觉元素（逗号分隔）
- 适用场景

## 框架文件格式

框架存储在 `frameworks/` 目录下的 YAML 文件：

```yaml
id: framework_id
name: "中文名称 (English Name)"
name_en: "English Name"
origin: "来源/创始人"
description: "详细描述"
description_en: "English description"
keywords:
  - 关键词1
  - 关键词2
visual_elements:
  - 视觉元素1
  - 视觉元素2
use_when: "适用场景描述"
```

## 内置框架

| ID | 名称 | 适用场景 |
|----|------|---------|
| `agapism` | 爱智主义 | 内在动机、价值认同 |
| `anancism` | 必然主义 | 硬性规则、机械约束 |
| `goodharts_law` | 古德哈特定律 | 优化陷阱、指标失效 |
| `moloch_trap` | 莫洛克陷阱 | 协调失败、博弈困境 |
| `participatory_knowing` | 参与式认知 | 身份构建、内化价值 |
| `multi_scale_alignment` | 多尺度对齐 | 层级结构、优先级 |
| `circuit_breaker` | 断路器模式 | 安全机制、自检系统 |
| `attractor_dynamics` | 吸引子动力学 | 吸引子、稳定状态 |

*框架库会随着使用自动扩充*

## 搜索框架

```bash
# 按关键词搜索
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/frameworks search <keyword>"
```
