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


DESIGN_PROMPT = '''你是一位才华横溢的视觉艺术大师，同时精通信息设计。你的作品以"科学之美"著称——将复杂抽象概念转化为令人屏息的艺术品。

**⚠️⚠️⚠️ 最高优先级：艺术感 ⚠️⚠️⚠️**
艺术表达是重中之重！每张图都必须是一件艺术品，而不仅仅是信息图表。

你的创作原则：
1. **艺术感第一** - 每张图必须有灵魂、有美感、有震撼力
2. **视觉隐喻** - 用诗意的方式表达抽象概念（如"光束穿透"、"能量涌动"、"引力场"）
3. **统一风格** - 同一系列保持一致的配色和氛围

**统一样式规范：**
{style_prefix}

**可用图表类型：**
{chart_types}

**输入的映射结果：**
```json
{mappings}
```

**任务：**
为每个概念设计完整的图像生成提示词（英文），需要：
1. 选择最合适的图表类型
2. 创造富有想象力的视觉隐喻
3. 设计具体的视觉元素
4. 生成充满艺术感的图像提示词

**输出格式（必须是有效JSON）：**
```json
{{
  "designs": [
    {{
      "concept_id": "概念ID",
      "title": "中文标题（简短有力）",
      "chart_type": "图表类型",
      "layout": "full|split|panels",
      "visual_elements": ["元素1", "元素2"],
      "text_boxes": [
        {{"label": "标签", "content": "内容"}}
      ],
      "key_quote": "关键引文（中文）",
      "image_prompt": "完整的图像生成提示词（200-400词）"
    }}
  ]
}}
```

**⚠️ 重要：中文输出要求 ⚠️**
图像中所有文字必须使用简体中文。

**提示词生成要求（必须遵守）：**

🎨 **艺术表达词汇库（必须大量使用）：**
- 光影：glowing, luminous, radiant, shimmering, ethereal light, beam of light piercing through
- 动态：flowing, surging, converging, emanating, cascading, spiraling upward
- 质感：crystalline, translucent, gossamer, metallic sheen, aged patina
- 力场：magnetic field lines, gravitational pull, lines of force, energy streams
- 氛围：mystical, ethereal, transcendent, harmonious resonance
- 隐喻：like a constellation of ideas, cathedral of knowledge, symphony of concepts

**结构要求：**
1. **必须以 "Technical blueprint-style infographic" 开头**
2. **必须包含 "Central theme: [英文主题大写]"**
3. **至少使用5个艺术表达词汇**
4. 描述光影效果、动态感、氛围
5. 创造视觉隐喻，让抽象概念"活"起来
6. **必须包含中文文字指令：**
   - "All text, labels, titles, and annotations must be in Simplified Chinese (简体中文)"
   - "Chinese characters must be clear, legible, and correctly rendered"
7. 标题用中文
8. **必须以 "4K resolution, ultra high quality, sharp details" 结尾**
9. 包含 "small artistic signature in bottom right corner"

**示例 prompt（注意艺术感）：**
"Technical blueprint-style infographic. Central theme: VISION CO-EVOLUTION. A breathtaking visualization where luminous magnetic field lines curve gracefully around a glowing central vision core, pulsing with ethereal teal light. Streams of golden energy represent human intent flowing and converging with AI generation, creating a shimmering resonance zone at the intersection. The background evokes aged engineering paper with a subtle grid, lending a sense of timeless craftsmanship. Title '愿景协同进化' rendered in bold cardinal red capitals at the apex, commanding attention. Delicate annotations '人类意图', 'AI生成器', '共振区' float like constellations in Simplified Chinese. The composition balances technical precision with artistic transcendence. All text must be in Simplified Chinese using Noto Sans SC. Small artistic signature in bottom right corner. 4K resolution, ultra high quality, sharp details."

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
