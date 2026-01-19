# Discover 详细指令

## 功能说明

从文章中自动发现并学习新的理论框架，扩充框架知识库。

### 识别范围

- **哲学概念**：实用主义、涌现论、现象学等
- **科学方法论**：演绎、归纳、溯因推理
- **系统论**：反馈、吸引子、自组织、涌现
- **物理学概念**：全息原理、量子纠错码、热力学
- **认知科学**：具身认知、分布式认知
- **工程模式**：断路器、负载均衡、微服务
- **博弈论**：纳什均衡、协调博弈、囚徒困境

## 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| 第一个参数 | ✓ | 文章文件路径 |
| `--no-save` | | 只发现不保存 |

## 发现流程

1. **文本分析** - LLM 分析文章内容
2. **框架识别** - 识别文章中隐含的理论框架
3. **库匹配** - 与已有框架库比对
4. **新增保存** - 将新发现的框架保存为 YAML

## 输出格式

```json
{
  "discovered_frameworks": [
    {
      "id": "framework_id",
      "name": "框架名称",
      "name_en": "Framework Name",
      "description": "框架描述",
      "confidence": 0.85,
      "is_new": true
    }
  ],
  "summary": {
    "total_discovered": 3,
    "new_added": 2,
    "already_exists": 1
  }
}
```

## 框架存储

新发现的框架自动保存到 `frameworks/` 目录：

```yaml
# frameworks/framework_id.yaml
id: framework_id
name: "框架名称"
name_en: "Framework Name"
origin: "来源文章"
description: "框架描述"
keywords:
  - keyword1
  - keyword2
visual_elements:
  - element1
  - element2
use_when: "适用场景"
```

## 使用示例

```bash
# 发现并保存
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/discover article.md"

# 只发现不保存
cd ${CLAUDE_PLUGIN_ROOT} && python agent.py "/discover article.md --no-save"
```
