"""
Skill: /analyze - 分析文章提取要点
从文章中提取核心概念、关键引文和层级关系
"""

import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from lib.api import client


ANALYZE_PROMPT = '''你是一个概念分析专家。请分析以下文章，提取核心要点。

**任务：**
1. 识别文章的核心主题和论点
2. 提取5-8个关键概念
3. 为每个概念找出文章中最有力的原文引文
4. 识别概念之间的层级关系或逻辑关系
5. 为每个概念推荐适合的可视化类型

**可视化类型选项：**
- hierarchy: 层级/优先级概念 → 金字塔图
- comparison: 二元对比概念 → 对比图
- network: 系统/关系概念 → 网络图
- flowchart: 过程/决策概念 → 流程图
- terrain: 优化/权衡概念 → 地形图
- attractor: 吸引/趋向概念 → 吸引子图

**输出格式（必须是有效JSON）：**
```json
{{
  "main_theme": "文章主题的一句话总结",
  "key_concepts": [
    {{
      "id": "concept_1",
      "name": "概念名称（简短英文）",
      "name_cn": "概念中文名称",
      "description": "概念描述（1-2句话）",
      "key_quote": "原文引文（英文）",
      "visualization_type": "hierarchy|comparison|network|flowchart|terrain|attractor",
      "importance": 1-10
    }}
  ],
  "relationships": [
    {{
      "from": "concept_id",
      "to": "concept_id",
      "type": "contains|constrains|enables|contrasts"
    }}
  ]
}}
```

**文章内容：**
---
{article}
---

请直接输出JSON，不要有任何其他文字。
'''


class AnalyzeSkill:
    """分析文章提取要点的技能"""

    name = "analyze"
    description = "分析文章，提取核心概念和关键引文"
    usage = "/analyze <文章内容或文件路径>"

    def __init__(self):
        self.client = client

    def run(self, article: str) -> dict:
        """
        分析文章

        Args:
            article: 文章内容或文件路径

        Returns:
            分析结果字典
        """
        # 如果是文件路径，读取文件
        if article.endswith('.md') or article.endswith('.txt'):
            path = Path(article)
            if path.exists():
                article = path.read_text(encoding='utf-8')

        prompt = ANALYZE_PROMPT.format(article=article[:15000])  # 限制长度

        print("🔍 正在分析文章...")

        response = self.client.generate_text(prompt)

        # 提取JSON
        try:
            # 尝试找到JSON块
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response

            result = json.loads(json_str.strip())
            print(f"✓ 提取了 {len(result.get('key_concepts', []))} 个核心概念")
            return result

        except json.JSONDecodeError as e:
            print(f"⚠ JSON解析失败: {e}")
            return {"raw_response": response, "error": str(e)}

    def format_output(self, result: dict) -> str:
        """格式化输出结果"""
        if "error" in result:
            return f"分析失败: {result['error']}"

        lines = [
            f"# 文章分析结果",
            f"",
            f"## 主题",
            f"{result.get('main_theme', 'N/A')}",
            f"",
            f"## 核心概念 ({len(result.get('key_concepts', []))}个)",
            ""
        ]

        for i, concept in enumerate(result.get('key_concepts', []), 1):
            lines.extend([
                f"### {i}. {concept.get('name_cn', concept.get('name'))}",
                f"- **英文名**: {concept.get('name')}",
                f"- **描述**: {concept.get('description')}",
                f"- **可视化**: {concept.get('visualization_type')}",
                f"- **引文**: \"{concept.get('key_quote', 'N/A')[:100]}...\"",
                ""
            ])

        return "\n".join(lines)


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyze.py <article_file_or_text>")
        sys.exit(1)

    skill = AnalyzeSkill()
    result = skill.run(sys.argv[1])
    print(skill.format_output(result))
