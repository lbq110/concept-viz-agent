"""
Skill: /design - 可视化设计
为每个概念设计具体的可视化方案和图像提示词
"""

import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from lib.api import client
from lib.registry import registry
from config import DEFAULT_VISUAL_STYLE


DESIGN_PROMPT = '''你是一位专业的技术文档设计师，擅长创建 Intuition Machine 风格的技术简报图。

**⚠️⚠️⚠️ 核心风格：技术简报演示文稿 ⚠️⚠️⚠️**
这是学术/技术简报风格，不是艺术3D渲染！

关键特征：
1. **扁平2D图形** - 干净的线条画，不是3D渲染
2. **解释性文本框** - 每张图必须有2-4个文本框解释概念
3. **分栏布局** - 图在左/中，文字在右/下
4. **底部总结** - "KEY QUOTE:" 框包含核心洞察

**统一样式规范：**
{style_prefix}

**可用图表类型：**
{chart_types}

**输入的映射结果：**
```json
{mappings}
```

**任务：**
为每个概念设计 Intuition Machine 风格的图像提示词（英文）。

**输出格式（必须是有效JSON）：**
```json
{{
  "designs": [
    {{
      "concept_id": "概念ID",
      "title": "中文标题",
      "chart_type": "图表类型",
      "layout": "split|center|comparison",
      "visual_elements": ["元素1", "元素2"],
      "text_boxes": [
        {{"label": "Definition:", "content": "概念定义"}},
        {{"label": "KEY QUOTE:", "content": "核心引文"}}
      ],
      "key_quote": "关键引文（中文）",
      "image_prompt": "完整的图像生成提示词（200-400词）"
    }}
  ]
}}
```

**⚠️ 提示词生成规则（必须严格遵守）：**

**禁止使用的词汇（会导致过度渲染）：**
- ❌ glowing, luminous, radiant, shimmering, ethereal
- ❌ breathtaking, stunning, majestic
- ❌ 3D render, photorealistic

**必须使用的风格描述：**
- ✅ clean line art, flat 2D graphics
- ✅ technical diagram, infographic style
- ✅ simple shapes, clean curves
- ✅ professional, educational

**布局必须包含（选择一种）：**
A) "Split layout: diagram on LEFT, text boxes on RIGHT side"
B) "Center layout: diagram in center, summary boxes BELOW"
C) "Comparison layout: two panels side by side"

**文本框必须包含：**
- "Text box with header 'Definition:' explaining the concept"
- "Text box with header 'KEY QUOTE:' containing main insight in italics"
- "Text box with header 'The Logic:' or 'Insight:' with explanation"

**结构要求：**
1. 以 "Technical infographic in Intuition Machine style." 开头
2. 包含 "Title: '[中文标题]' in dark maroon ALL CAPS at top"
3. 描述扁平2D图形（不是3D）
4. 描述文本框的位置和内容
5. 包含 "Light cream graph paper background (#F5F0E1) with subtle grid"
6. 包含 "Small logo in bottom right corner"
7. **必须包含中文质量要求：**
   - "All text in Simplified Chinese (简体中文)"
   - "Chinese characters must be crystal clear, perfectly formed, and correctly rendered"
   - "Use clean Chinese fonts like Noto Sans SC"
8. **必须以以下内容结尾：**
   "4K ultra-high resolution, sharp details. Clean technical style, educational infographic."

**示例 prompt（注意：扁平风格 + 文本框 + 分栏布局 + 4K + 中文要求）：**
"Technical infographic in Intuition Machine style. Title: 'THE AGAPISTIC ALTERNATIVE' in dark maroon ALL CAPS at top, with subtitle 'Alignment via Attraction' below. Split layout: LEFT side shows a flat 2D diagram with a brown triangle on the left connected by clean teal parallel curves (like magnetic field lines) flowing toward a teal circle labeled 'THE IDEAL (MAGNETIC CENTER)' on the right. The curves represent 'Internal Desire / Sympathy'. RIGHT side contains three text boxes with light cream backgrounds: Box 1 header 'Definition:' explains Agapism concept; Box 2 header 'Mechanism:' shows the formula; Box 3 header 'The Goal:' describes the objective. Light cream graph paper background (#F5F0E1) with subtle grid. Colors: teal #2F337, brown #8B7355, maroon titles. Small logo in bottom right corner. All text in Simplified Chinese (简体中文). Chinese characters must be crystal clear, perfectly formed, and correctly rendered. Use clean Chinese fonts like Noto Sans SC. 4K ultra-high resolution, sharp details. Clean technical style, educational infographic."

请直接输出JSON，不要有任何其他文字。
'''


class DesignSkill:
    """可视化设计技能"""

    name = "design"
    description = "设计图像提示词和视觉方案"
    usage = "/design <map结果JSON>"

    def __init__(self, style: str = None):
        self.client = client
        self.registry = registry
        self.style_id = style or DEFAULT_VISUAL_STYLE

    def _get_chart_types_desc(self) -> str:
        """生成图表类型描述（从registry动态获取）"""
        return self.registry.get_chart_types_for_prompt()

    def _get_style(self) -> dict:
        """获取当前视觉风格"""
        return self.registry.get_visual_style(self.style_id)

    def _get_style_prefix(self) -> str:
        """获取统一样式前缀"""
        style = self._get_style()
        # 优先使用 style_prefix，否则使用 template
        return style.get("style_prefix", style.get("template", ""))

    def run(self, mappings: list | dict) -> dict:
        """
        设计可视化方案

        Args:
            mappings: map skill的输出

        Returns:
            设计结果字典
        """
        if isinstance(mappings, dict):
            if "mappings" in mappings:
                mappings = mappings["mappings"]

        if isinstance(mappings, str):
            mappings = json.loads(mappings)

        style = self._get_style()
        style_prefix = self._get_style_prefix()

        prompt = DESIGN_PROMPT.format(
            style_prefix=style_prefix,
            chart_types=self._get_chart_types_desc(),
            mappings=json.dumps(mappings, ensure_ascii=False, indent=2)
        )

        print("🎨 正在设计可视化方案...")

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
            print(f"✓ 完成 {len(result.get('designs', []))} 个可视化设计")
            return result

        except json.JSONDecodeError as e:
            print(f"⚠ JSON解析失败: {e}")
            return {"raw_response": response, "error": str(e)}

    def format_output(self, result: dict) -> str:
        """格式化输出结果"""
        if "error" in result:
            return f"设计失败: {result['error']}"

        lines = [
            "# 可视化设计方案",
            ""
        ]

        for i, d in enumerate(result.get('designs', []), 1):
            lines.extend([
                f"## {i}. {d.get('title', 'UNTITLED')}",
                "",
                f"**图表类型**: {d.get('chart_type')}",
                f"**布局**: {d.get('layout')}",
                "",
                "**视觉元素**:",
                *[f"- {e}" for e in d.get('visual_elements', [])],
                "",
                "**文字框**:",
                *[f"- [{t.get('label')}]: {t.get('content')[:50]}..." for t in d.get('text_boxes', [])],
                "",
                "**图像提示词**:",
                "```",
                d.get('image_prompt', 'N/A'),
                "```",
                "",
                "---",
                ""
            ])

        return "\n".join(lines)

    def get_prompts_only(self, result: dict) -> list:
        """仅提取图像提示词列表"""
        prompts = []
        for d in result.get('designs', []):
            prompts.append({
                "title": d.get('title'),
                "prompt": d.get('image_prompt')
            })
        return prompts


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python design.py <mappings_json>")
        sys.exit(1)

    skill = DesignSkill()

    input_arg = sys.argv[1]
    if input_arg.endswith('.json'):
        with open(input_arg) as f:
            mappings = json.load(f)
    else:
        mappings = json.loads(input_arg)

    result = skill.run(mappings)
    print(skill.format_output(result))
