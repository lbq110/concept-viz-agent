"""
Skill: /generate - 图像生成
使用Google AI Studio API生成图像
"""

import json
import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from lib.api import client
from lib.registry import registry
from config import DEFAULT_VISUAL_STYLE, VISUAL_STYLES


class GenerateSkill:
    """图像生成技能"""

    name = "generate"
    description = "使用AI生成概念图"
    usage = "/generate <prompt> [output_path]"

    def __init__(self, output_dir: str = "output", style: str = None):
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.style_id = style or DEFAULT_VISUAL_STYLE
        self.style_prefix = self._get_style_prefix()

    def _get_style_prefix(self) -> str:
        """获取统一样式前缀"""
        # 先尝试从 config 中的 VISUAL_STYLES 获取
        if self.style_id in VISUAL_STYLES:
            style = VISUAL_STYLES[self.style_id]
            return style.get("style_prefix", "")
        # 否则从 registry 获取
        style = registry.get_visual_style(self.style_id)
        return style.get("style_prefix", style.get("template", ""))

    def run(self, prompt: str, output_name: str = None, use_style_prefix: bool = True) -> dict:
        """
        生成单张图像

        Args:
            prompt: 图像生成提示词
            output_name: 输出文件名（不含扩展名）
            use_style_prefix: 是否添加统一样式前缀

        Returns:
            生成结果字典
        """
        if output_name is None:
            output_name = f"image_{int(time.time())}"

        output_path = str(self.output_dir / output_name)

        # 添加统一样式前缀
        if use_style_prefix and self.style_prefix:
            full_prompt = f"{self.style_prefix}\n\n=== IMAGE CONTENT ===\n{prompt}"
        else:
            full_prompt = prompt

        print(f"🖼️ 正在生成图像: {output_name}")

        try:
            result = self.client.generate_image(full_prompt, output_path)

            if result.get("success"):
                print(f"✓ 图像已保存: {result.get('output_path')}")
            else:
                print(f"✗ 生成失败: {result.get('error')}")

            return result

        except Exception as e:
            print(f"✗ 错误: {e}")
            return {"success": False, "error": str(e)}

    def run_batch(self, designs: list | dict, delay: float = 2.0) -> list:
        """
        批量生成图像

        Args:
            designs: design skill的输出，或包含prompt的列表
            delay: 请求间隔（秒）

        Returns:
            生成结果列表
        """
        if isinstance(designs, dict):
            if "designs" in designs:
                designs = designs["designs"]

        if isinstance(designs, str):
            designs = json.loads(designs)

        results = []
        total = len(designs)

        print(f"📦 批量生成 {total} 张图像...")
        print("=" * 50)

        for i, design in enumerate(designs, 1):
            # 提取提示词和标题
            if isinstance(design, dict):
                prompt = design.get("image_prompt") or design.get("prompt")
                title = design.get("title", f"image_{i:02d}")
            else:
                prompt = design
                title = f"image_{i:02d}"

            # 清理文件名
            safe_title = "".join(c if c.isalnum() or c in "._-" else "_" for c in title)
            output_name = f"{i:02d}_{safe_title}"

            print(f"\n[{i}/{total}] {title}")

            result = self.run(prompt, output_name)
            result["title"] = title
            result["index"] = i
            results.append(result)

            # 间隔
            if i < total:
                time.sleep(delay)

        # 统计
        success_count = sum(1 for r in results if r.get("success"))
        print("\n" + "=" * 50)
        print(f"完成: {success_count}/{total} 成功")

        return results

    def format_output(self, results: list) -> str:
        """格式化批量生成结果"""
        lines = [
            "# 图像生成结果",
            "",
            f"成功: {sum(1 for r in results if r.get('success'))}/{len(results)}",
            ""
        ]

        for r in results:
            status = "✓" if r.get("success") else "✗"
            path = r.get("output_path", "N/A")
            lines.append(f"{status} [{r.get('index')}] {r.get('title')}: {path}")

        return "\n".join(lines)


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate.py <prompt> [output_name]")
        print("  python generate.py --batch <designs_json>")
        sys.exit(1)

    skill = GenerateSkill()

    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Please provide designs JSON file")
            sys.exit(1)

        with open(sys.argv[2]) as f:
            designs = json.load(f)

        results = skill.run_batch(designs)
        print(skill.format_output(results))

    else:
        prompt = sys.argv[1]
        output_name = sys.argv[2] if len(sys.argv) > 2 else None
        skill.run(prompt, output_name)
