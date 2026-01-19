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
2. **解释性文本框** - 每张图必须有3-5个文本框解释概念，包含文章原文的关键观点
3. **分栏布局** - 图在左/中，文字在右/下
4. **底部总结** - "KEY QUOTE:" 框包含核心洞察
5. **丰富的文章内容** - 图片中要包含足够多与原文相关的信息（关键词、观点、例子等）

**统一样式规范：**
{style_prefix}

**可用图表类型：**
{chart_types}

**⚠️ 图表选择优先级（重要）：**
为每个概念选择 chart_type 时，请按以下优先级：
1. **首选**：使用映射结果中的 `recommended_chart` 字段（如果有）
2. **备选**：如果 recommended_chart 不适合内容，从 `alternative_charts` 中选择
3. **自由选择**：只有在没有推荐或推荐不适合时，才从完整图表库自由选择

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
        {{"label": "DEFINITION 定义:", "content": "概念定义（来自原文）"}},
        {{"label": "KEY INSIGHT 核心洞察:", "content": "来自映射框架的insight"}},
        {{"label": "EXAMPLE 案例:", "content": "原文提到的具体例子"}},
        {{"label": "KEY QUOTE 关键引文:", "content": "核心引文（来自原文）"}}
      ],
      "key_quote": "关键引文（中文）",
      "image_prompt": "完整的图像生成提示词（300-500词，必须包含3-5个文本框内容）"
    }}
  ]
}}
```

**⚠️ 提示词生成规则（必须严格遵守）：**

**图表风格（可选2D或等轴测3D）：**
- ✅ 可以使用 isometric 3D technical illustration（等轴测技术插图）
- ✅ 也可以使用 flat 2D technical diagram
- ✅ 根据概念选择最合适的表现方式

**必须包含的视觉丰富元素：**
1. **纸张材质**："aged blueprint paper with subtle texture and light creases"
2. **背景图案**："faded thematic background pattern related to [概念]"（如电路图、齿轮、流程图等，要与主题呼应）
3. **双语标签**："bilingual labels (English term + Chinese translation)"
4. **文章内容标注**：必须包含3-5个与原文直接相关的文本框，内容来自：
   - 原文的核心观点或定义
   - 原文提到的例子或案例
   - 原文的关键引文
   - 映射框架的insight解释

**⚠️ 不要包含以下元素：**
- 右下角的 title block / 标题栏
- 右上角的 stamps / watermarks / 技术标签
- 任何尺寸标注或测量线

**结构要求：**
1. 以 "Technical blueprint infographic." 开头
2. 标题格式："Title: '[中文标题]' in dark maroon ALL CAPS in brackets, with English subtitle below"
3. 描述主图（2D或等轴测3D技术插图）
4. 描述背景图案（与主题相关的淡化图案）
5. 包含 "Aged cream blueprint paper (#F5F0E1) with subtle texture and grid"
6. **必须包含3-5个文本框**，内容直接来自原文的观点、例子或引文
7. **必须包含中文质量要求：**
   - "All text in Simplified Chinese (简体中文)"
   - "Chinese characters must be crystal clear, perfectly formed"
8. **必须以以下内容结尾：**
   "Clean corners with no title blocks or stamps. 4K ultra-high resolution. Technical blueprint aesthetic."

**示例 prompt（注意丰富的文章内容和视觉元素）：**
"Technical blueprint infographic. Title: '[必然性需求格栅]' in dark maroon ALL CAPS in brackets at top, with English subtitle 'THE ANANCIC LATTICE OF SPECIFICATION' below. Main diagram: isometric 3D technical illustration of an interlocking lattice structure made of teal steel beams and brown wooden connectors, representing structured requirements. Multiple text boxes with article content: Box 1 - 'DEFINITION 定义: 通过规则和约束实现控制', Box 2 - 'KEY INSIGHT 核心洞察: 硬性规则确保一致性但牺牲灵活性', Box 3 - 'EXAMPLE 案例: 代码规范如同建筑蓝图', Box 4 - 'KEY QUOTE 关键引文: 约束是自由的基础'. Bilingual callout labels point to key parts: 'STRUCTURAL CONSTRAINTS 结构约束', 'LOGIC FLOW 逻辑导向', 'CORE DOMAIN 核心领域'. Background: aged cream blueprint paper (#F5F0E1) with subtle texture and light creases. Faded flowchart patterns in background related to process logic. Colors: teal #2F337, warm brown #8B7355, maroon titles. All text in Simplified Chinese (简体中文). Chinese characters must be crystal clear, perfectly formed. Clean corners with no title blocks or stamps. 4K ultra-high resolution. Technical blueprint aesthetic."

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
