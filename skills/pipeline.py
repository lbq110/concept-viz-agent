"""
Skill: /pipeline - 完整流水线
一键执行完整的文章→图像workflow
包含自动学习功能：发现并扩充理论框架库
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).parent.parent))

from .analyze import AnalyzeSkill
from .map_framework import MapFrameworkSkill
from .design import DesignSkill
from .generate import GenerateSkill
from .discover import DiscoverSkill


class PipelineSkill:
    """完整流水线技能 - 带自动学习"""

    name = "pipeline"
    description = "一键执行完整的文章→图像workflow，同时自动学习新框架"
    usage = "/pipeline <文章文件路径> [输出目录] [--no-learn]"

    def __init__(self, output_dir: str = None, auto_learn: bool = True):
        self.analyze = AnalyzeSkill()
        self.map_framework = MapFrameworkSkill()
        self.design = DesignSkill()
        self.discover = DiscoverSkill(auto_save=True)
        self.auto_learn = auto_learn

        # 设置输出目录
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = Path(f"output/run_{timestamp}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generate = GenerateSkill(str(self.output_dir / "images"))

    def run(self, article_path: str, generate_images: bool = True) -> dict:
        """
        执行完整流水线

        Args:
            article_path: 文章文件路径
            generate_images: 是否生成图像

        Returns:
            完整结果字典
        """
        results = {
            "article_path": article_path,
            "output_dir": str(self.output_dir),
            "steps": {},
            "learning": {},
            "success": False
        }

        total_steps = 5 if self.auto_learn else 4

        print("=" * 60)
        print("🚀 CONCEPT VISUALIZER PIPELINE (Learning Edition)")
        print("=" * 60)
        print(f"输入: {article_path}")
        print(f"输出: {self.output_dir}")
        print(f"自动学习: {'✓ 开启' if self.auto_learn else '✗ 关闭'}")
        print("=" * 60)

        # 读取文章
        article_file = Path(article_path)
        if not article_file.exists():
            print(f"✗ 文件不存在: {article_path}")
            return results

        article = article_file.read_text(encoding='utf-8')
        print(f"✓ 读取文章: {len(article)} 字符")

        # Step 0: 框架发现与学习（可选但推荐）
        if self.auto_learn:
            print("\n" + "-" * 40)
            print(f"STEP 0/{total_steps}: 🎓 框架发现与学习")
            print("-" * 40)

            discover_result = self.discover.run(article)
            results["learning"] = discover_result

            if "error" not in discover_result:
                # 保存学习结果
                with open(self.output_dir / "00_discover.json", "w", encoding="utf-8") as f:
                    json.dump(discover_result, f, ensure_ascii=False, indent=2)

                summary = discover_result.get("summary", {})
                if summary.get("new_added", 0) > 0:
                    print(f"🎉 框架库已扩充！新增 {summary['new_added']} 个框架")

        # Step 1: 分析
        print("\n" + "-" * 40)
        print(f"STEP 1/{total_steps}: 分析文章")
        print("-" * 40)

        analyze_result = self.analyze.run(article)
        results["steps"]["analyze"] = analyze_result

        if "error" in analyze_result:
            print(f"✗ 分析失败: {analyze_result['error']}")
            return results

        # 保存分析结果
        with open(self.output_dir / "01_analyze.json", "w", encoding="utf-8") as f:
            json.dump(analyze_result, f, ensure_ascii=False, indent=2)

        # Step 2: 理论框架映射
        print("\n" + "-" * 40)
        print(f"STEP 2/{total_steps}: 理论框架映射")
        print("-" * 40)

        map_result = self.map_framework.run(analyze_result)
        results["steps"]["map"] = map_result

        if "error" in map_result:
            print(f"✗ 映射失败: {map_result['error']}")
            return results

        # 保存映射结果
        with open(self.output_dir / "02_map.json", "w", encoding="utf-8") as f:
            json.dump(map_result, f, ensure_ascii=False, indent=2)

        # Step 3: 可视化设计
        print("\n" + "-" * 40)
        print(f"STEP 3/{total_steps}: 可视化设计")
        print("-" * 40)

        design_result = self.design.run(map_result)
        results["steps"]["design"] = design_result

        if "error" in design_result:
            print(f"✗ 设计失败: {design_result['error']}")
            return results

        # 保存设计结果
        with open(self.output_dir / "03_design.json", "w", encoding="utf-8") as f:
            json.dump(design_result, f, ensure_ascii=False, indent=2)

        # 保存提示词到markdown
        prompts_md = self._format_prompts_markdown(design_result)
        with open(self.output_dir / "prompts.md", "w", encoding="utf-8") as f:
            f.write(prompts_md)

        # Step 4: 生成图像
        if generate_images:
            print("\n" + "-" * 40)
            print(f"STEP 4/{total_steps}: 生成图像")
            print("-" * 40)

            generate_result = self.generate.run_batch(design_result)
            results["steps"]["generate"] = generate_result

            # 保存生成结果
            with open(self.output_dir / "04_generate.json", "w", encoding="utf-8") as f:
                json.dump(generate_result, f, ensure_ascii=False, indent=2, default=str)

        else:
            print("\n" + "-" * 40)
            print(f"STEP 4/{total_steps}: 跳过图像生成")
            print("-" * 40)
            print("提示词已保存到 prompts.md")

        # 生成报告
        report = self._generate_report(results)
        with open(self.output_dir / "report.md", "w", encoding="utf-8") as f:
            f.write(report)

        results["success"] = True

        print("\n" + "=" * 60)
        print("✓ 流水线完成!")
        print(f"输出目录: {self.output_dir}")

        # 显示学习成果
        if self.auto_learn and "summary" in results.get("learning", {}):
            summary = results["learning"]["summary"]
            print(f"\n📚 学习成果:")
            print(f"   新增框架: {summary.get('new_added', 0)}")
            print(f"   框架库总数: {summary.get('total_frameworks', 'N/A')}")

        print("=" * 60)

        return results

    def _format_prompts_markdown(self, design_result: dict) -> str:
        """格式化提示词为markdown"""
        lines = [
            "# Generated Image Prompts",
            "",
            f"Generated at: {datetime.now().isoformat()}",
            "",
        ]

        for i, d in enumerate(design_result.get("designs", []), 1):
            lines.extend([
                f"## {i}. {d.get('title', 'UNTITLED')}",
                "",
                f"**Chart Type**: {d.get('chart_type')}",
                "",
                "**Prompt**:",
                "```",
                d.get("image_prompt", "N/A"),
                "```",
                "",
                "---",
                ""
            ])

        return "\n".join(lines)

    def _generate_report(self, results: dict) -> str:
        """生成最终报告"""
        lines = [
            "# Concept Visualizer Pipeline Report",
            "",
            f"**Date**: {datetime.now().isoformat()}",
            f"**Input**: {results.get('article_path')}",
            f"**Output**: {results.get('output_dir')}",
            "",
        ]

        # 学习成果
        learning = results.get("learning", {})
        if learning and "summary" in learning:
            summary = learning["summary"]
            lines.extend([
                "## 🎓 Learning Results",
                "",
                f"- New frameworks added: {summary.get('new_added', 0)}",
                f"- Frameworks enriched: {summary.get('enriched', 0)}",
                f"- Total frameworks in library: {summary.get('total_frameworks', 'N/A')}",
                ""
            ])

            # 新增的框架
            new_added = learning.get("learning", {}).get("new_frameworks_added", [])
            if new_added:
                lines.append("### New Frameworks Added")
                lines.append("")
                for f in new_added:
                    lines.append(f"- **{f.get('name')}** (`{f.get('id')}`) - confidence: {f.get('confidence', 0):.0%}")
                lines.append("")

        lines.append("## Pipeline Steps")
        lines.append("")

        steps = results.get("steps", {})

        # 分析结果
        if "analyze" in steps:
            analyze = steps["analyze"]
            concepts = analyze.get("key_concepts", [])
            lines.extend([
                "### Step 1: Analyze",
                f"- Theme: {analyze.get('main_theme', 'N/A')}",
                f"- Concepts extracted: {len(concepts)}",
                ""
            ])

        # 映射结果
        if "map" in steps:
            mappings = steps["map"].get("mappings", [])
            lines.extend([
                "### Step 2: Framework Mapping",
                f"- Mappings created: {len(mappings)}",
                ""
            ])

        # 设计结果
        if "design" in steps:
            designs = steps["design"].get("designs", [])
            lines.extend([
                "### Step 3: Visual Design",
                f"- Designs created: {len(designs)}",
                ""
            ])

        # 生成结果
        if "generate" in steps:
            gen_results = steps["generate"]
            success = sum(1 for r in gen_results if r.get("success"))
            lines.extend([
                "### Step 4: Image Generation",
                f"- Images generated: {success}/{len(gen_results)}",
                ""
            ])

        # 概念列表
        if "analyze" in steps:
            lines.extend([
                "## Concepts",
                ""
            ])
            for i, c in enumerate(steps["analyze"].get("key_concepts", []), 1):
                lines.append(f"{i}. **{c.get('name_cn', c.get('name'))}**: {c.get('description', '')[:60]}...")

        lines.extend([
            "",
            "## Output Files",
            "",
            "- `00_discover.json` - 框架发现结果（如启用）",
            "- `01_analyze.json` - 文章分析结果",
            "- `02_map.json` - 理论框架映射",
            "- `03_design.json` - 可视化设计",
            "- `04_generate.json` - 图像生成结果",
            "- `prompts.md` - 图像提示词",
            "- `images/` - 生成的图像",
        ])

        return "\n".join(lines)


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <article_path> [output_dir] [--no-learn]")
        sys.exit(1)

    article_path = sys.argv[1]
    output_dir = None
    auto_learn = True

    for arg in sys.argv[2:]:
        if arg == "--no-learn":
            auto_learn = False
        else:
            output_dir = arg

    skill = PipelineSkill(output_dir, auto_learn=auto_learn)
    skill.run(article_path)
