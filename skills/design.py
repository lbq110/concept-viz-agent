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


DESIGN_PROMPT = '''你是一个专业的信息设计师，擅长将抽象概念转化为技术风格的可视化图表。

**统一视觉风格要求：**
- 背景: {background}
- 标题: {title_color}, {title_font}
- 主色调: {primary_color}
- 辅色调: {secondary_color}
- 强调色: {accent_color}
- 整体风格: {style}
- 水印: {watermark}

**可用图表类型：**
{chart_types}

**输入的映射结果：**
```json
{mappings}
```

**任务：**
为每个概念设计完整的图像生成提示词（英文），需要：
1. 选择最合适的图表类型
2. 设计具体的视觉元素
3. 规划布局和文字框
4. 生成完整的图像生成提示词

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
图像中所有文字必须使用简体中文，包括：
- 标题必须是中文
- 所有标签、说明文字必须是中文
- 引文必须是中文
- 图表中的文字必须是中文

**提示词生成要求：**
1. 以"Technical blueprint-style infographic"开头
2. 明确描述背景、标题、主要视觉元素
3. 包含颜色规范
4. 描述文字框位置和内容
5. **必须包含以下中文文字指令：**
   - "All text, labels, titles, and annotations must be in Simplified Chinese (简体中文)"
   - "Chinese characters must be clear, legible, and correctly rendered"
   - "Use a clean Chinese font like Noto Sans SC, Source Han Sans, or Microsoft YaHei"
6. 标题格式：用中文，如 "模块化规范：避免指令诅咒"
7. 以风格描述结尾
8. 添加 "4K resolution, ultra high quality, sharp details"

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
        prompt = DESIGN_PROMPT.format(
            background=style.get("description", "technical blueprint style"),
            title_color="dark red capital letters",
            title_font="Crimson Pro or similar bold serif font",
            primary_color="teal blue (#2F337)",
            secondary_color="warm brown/gold tones",
            accent_color="deep red for emphasis",
            style=style.get("name", "blueprint"),
            watermark="small watermark in bottom right corner",
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
