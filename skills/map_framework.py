"""
Skill: /map - 理论框架映射
将提取的概念映射到科学/哲学方法论框架
"""

import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from lib.api import client
from lib.registry import registry


MAP_PROMPT = '''你是一个跨学科理论家，擅长将概念映射到科学和哲学框架。

**可用的理论框架库：**

{frameworks_desc}

**任务：**
对于每个输入的概念，选择1-2个最合适的理论框架进行映射，并：
1. 解释映射关系
2. 生成一个基于框架的新标题（全大写英文）
3. 提供理论框架带来的新洞察

**输入概念：**
```json
{concepts}
```

**输出格式（必须是有效JSON）：**
```json
{{
  "mappings": [
    {{
      "concept_id": "原概念ID",
      "original_name": "原概念名称",
      "framework": "映射的理论框架ID",
      "framework_name": "理论框架名称",
      "mapping_explanation": "映射解释（中文）",
      "new_title": "THE NEW TITLE IN CAPS",
      "subtitle": "可选的副标题",
      "insight": "理论框架带来的新洞察（中文）",
      "visual_metaphor": "建议的视觉隐喻"
    }}
  ]
}}
```

请直接输出JSON，不要有任何其他文字。
'''


class MapFrameworkSkill:
    """理论框架映射技能"""

    name = "map"
    description = "将概念映射到科学/哲学理论框架"
    usage = "/map <analyze结果JSON>"

    def __init__(self):
        self.client = client
        self.registry = registry

    def _get_frameworks_description(self) -> str:
        """生成框架描述文本（从registry动态获取）"""
        return self.registry.get_frameworks_for_prompt()

    def run(self, concepts: list | dict) -> dict:
        """
        映射概念到理论框架

        Args:
            concepts: analyze skill的输出，或概念列表

        Returns:
            映射结果字典
        """
        # 处理输入
        if isinstance(concepts, dict):
            if "key_concepts" in concepts:
                concepts = concepts["key_concepts"]

        if isinstance(concepts, str):
            concepts = json.loads(concepts)

        prompt = MAP_PROMPT.format(
            frameworks_desc=self._get_frameworks_description(),
            concepts=json.dumps(concepts, ensure_ascii=False, indent=2)
        )

        print("🗺️ 正在映射理论框架...")

        response = self.client.generate_text(prompt)

        # 提取JSON
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response

            result = json.loads(json_str.strip())
            print(f"✓ 完成 {len(result.get('mappings', []))} 个概念的框架映射")
            return result

        except json.JSONDecodeError as e:
            print(f"⚠ JSON解析失败: {e}")
            return {"raw_response": response, "error": str(e)}

    def format_output(self, result: dict) -> str:
        """格式化输出结果"""
        if "error" in result:
            return f"映射失败: {result['error']}"

        lines = [
            "# 理论框架映射结果",
            ""
        ]

        for i, m in enumerate(result.get('mappings', []), 1):
            lines.extend([
                f"## {i}. {m.get('new_title', 'UNTITLED')}",
                f"**副标题**: {m.get('subtitle', 'N/A')}",
                "",
                f"**原概念**: {m.get('original_name')}",
                f"**理论框架**: {m.get('framework_name')} ({m.get('framework')})",
                "",
                f"**映射解释**: {m.get('mapping_explanation')}",
                "",
                f"**洞察**: {m.get('insight')}",
                "",
                f"**视觉隐喻**: {m.get('visual_metaphor')}",
                "",
                "---",
                ""
            ])

        return "\n".join(lines)


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python map_framework.py <concepts_json>")
        sys.exit(1)

    skill = MapFrameworkSkill()

    # 读取输入
    input_arg = sys.argv[1]
    if input_arg.endswith('.json'):
        with open(input_arg) as f:
            concepts = json.load(f)
    else:
        concepts = json.loads(input_arg)

    result = skill.run(concepts)
    print(skill.format_output(result))
