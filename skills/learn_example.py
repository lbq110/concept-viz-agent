"""
Skill: /learn - 从示例学习
输入包含文章和生成图片的文件夹，反向分析并扩充 frameworks、charts、styles
"""

import json
import base64
import sys
from pathlib import Path
from typing import List, Dict, Tuple
sys.path.append(str(Path(__file__).parent.parent))

from lib.api import GeminiClient
from lib.registry import Registry
from .analyze import AnalyzeSkill
from .map_framework import MapFrameworkSkill
from .design import DesignSkill
from .generate import GenerateSkill

# 支持的图片格式
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
# 支持的文章格式
ARTICLE_EXTENSIONS = {'.md', '.txt', '.markdown'}


VERIFY_PROMPT = """你是一位专业的图像比较分析师。

## 任务
比较两组图片的相似度，判断「生成图片」是否成功复现了「原始示例」的风格和内容。

## 评估维度

1. **视觉风格匹配** (0-100)
   - 背景风格是否一致
   - 配色方案是否相似
   - 整体美学是否接近

2. **图表类型匹配** (0-100)
   - 使用的图表形式是否相同
   - 布局结构是否类似

3. **概念表达匹配** (0-100)
   - 核心概念是否被正确可视化
   - 理论框架的表达是否准确

4. **整体质量** (0-100)
   - 生成图片的专业度
   - 是否达到原始示例的水准

## 输出格式
返回JSON（不要markdown代码块）：
{{
    "scores": {{
        "visual_style": 85,
        "chart_type": 90,
        "concept_expression": 80,
        "overall_quality": 82
    }},
    "average_score": 84,
    "passed": true,
    "analysis": {{
        "strengths": ["风格还原度高", "配色准确"],
        "weaknesses": ["部分细节缺失"],
        "suggestions": ["可以增加更多标注"]
    }},
    "verdict": "验证通过/验证失败的简短说明"
}}

注意：average_score >= 70 时 passed 为 true
"""


ANALYZE_EXAMPLE_PROMPT = """你是一位博学的视觉设计分析专家，精通理论框架、图表类型和视觉风格。

## 任务
分析这组示例作品（文章 + 生成的概念图），提取其中使用的：
1. 理论框架 (Frameworks) - 用于解释概念的学术/科学理论
2. 图表类型 (Chart Types) - 可视化的图表形式
3. 视觉风格 (Visual Styles) - 整体美学风格

## 输入

### 文章内容
{article}

### 图片数量
共 {image_count} 张概念图

## 分析要求

### 1. 理论框架分析
观察图片中如何解释概念，识别使用的理论框架：
- 框架名称（中英文）
- 框架来源（哲学/科学/工程等领域）
- 核心描述
- 关键词
- 视觉表现元素
- 适用场景

### 2. 图表类型分析
识别图片中使用的图表形式：
- 图表名称（中英文）
- 描述
- 最适合表达什么
- 布局方式
- 核心元素

### 3. 视觉风格分析
分析整体视觉风格：
- 风格名称（中英文）
- 背景特征
- 配色方案
- 排版特点
- 标题风格
- 整体氛围

## 输出格式
返回JSON（不要markdown代码块）：
{{
    "frameworks": [
        {{
            "id": "snake_case_id",
            "name": "中文名称 (English Name)",
            "name_en": "English Name",
            "origin": "来源领域",
            "description": "详细描述",
            "description_en": "English description",
            "keywords": ["关键词1", "关键词2"],
            "visual_elements": ["视觉元素1", "视觉元素2"],
            "use_when": "适用场景描述"
        }}
    ],
    "chart_types": [
        {{
            "id": "snake_case_id",
            "name": "中文名称",
            "name_en": "English Name",
            "description": "描述",
            "description_en": "English description",
            "best_for": ["适用场景1", "适用场景2"],
            "layout": "布局描述",
            "elements": ["元素1", "元素2"],
            "template": "视觉模板描述"
        }}
    ],
    "visual_styles": [
        {{
            "id": "snake_case_id",
            "name": "中文名称",
            "name_en": "English Name",
            "description": "风格描述",
            "background": "背景描述",
            "colors": {{
                "primary": "主色",
                "secondary": "次色",
                "accent": "强调色",
                "text": "文字色"
            }},
            "typography": {{
                "title": "标题风格",
                "body": "正文风格"
            }},
            "characteristics": ["特征1", "特征2"]
        }}
    ],
    "analysis_notes": "分析备注，说明这组作品的整体特点"
}}
"""


class LearnExampleSkill:
    """从示例学习技能 - 带闭环验证"""

    name = "learn"
    description = "从示例文件夹学习新的frameworks、charts、styles（含验证）"
    usage = "/learn <文件夹路径> [--no-verify] [--threshold=70]"

    def __init__(self, verify: bool = True, pass_threshold: int = 70):
        """
        Args:
            verify: 是否进行闭环验证（正向生成并比较）
            pass_threshold: 验证通过的分数阈值 (0-100)
        """
        self.client = GeminiClient()
        self.registry = Registry()
        self.verify = verify
        self.pass_threshold = pass_threshold

        # 用于验证的技能
        self.analyze_skill = AnalyzeSkill()
        self.map_skill = MapFrameworkSkill()
        self.design_skill = DesignSkill()
        self.generate_skill = None  # 延迟初始化

    def run(self, folder_path: str) -> dict:
        """
        从示例文件夹学习

        Args:
            folder_path: 包含文章和图片的文件夹路径

        Returns:
            学习结果
        """
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return {"error": f"文件夹不存在: {folder_path}"}

        print("=" * 60)
        print("📚 LEARN FROM EXAMPLE" + (" (with verification)" if self.verify else ""))
        print("=" * 60)
        print(f"文件夹: {folder_path}")
        if self.verify:
            print(f"验证阈值: {self.pass_threshold}")

        # 1. 查找文章和图片
        article_path, article_content = self._find_article(folder)
        image_paths = self._find_images(folder)

        if not article_content:
            return {"error": "未找到文章文件 (.md, .txt)"}

        if not image_paths:
            return {"error": "未找到图片文件 (.jpg, .png, .gif, .webp)"}

        print(f"✓ 找到文章: {article_path.name} ({len(article_content)} 字符)")
        print(f"✓ 找到图片: {len(image_paths)} 张")
        for img in image_paths:
            print(f"  - {img.name}")

        # 2. 分析示例（反向提取）
        print("\n" + "-" * 40)
        print("🔬 STEP 1: 反向分析示例作品...")
        print("-" * 40)

        analysis = self._analyze_example(article_content, image_paths)

        if "error" in analysis:
            return analysis

        # 3. 提取候选内容（暂不持久化）
        print("\n" + "-" * 40)
        print("📋 STEP 2: 提取候选知识...")
        print("-" * 40)

        candidates = self._extract_candidates(analysis)

        if not candidates["has_new"]:
            print("  ℹ 未发现新内容，现有库已包含这些知识")
            return {
                "folder": folder_path,
                "article": str(article_path),
                "analysis": analysis,
                "verification": {"skipped": True, "reason": "no_new_content"},
                "learning": {"frameworks_added": 0, "charts_added": 0, "styles_added": 0},
                "summary": self._get_summary(0, 0, 0)
            }

        # 4. 闭环验证
        verification_result = {"skipped": True, "reason": "disabled"}

        if self.verify:
            print("\n" + "-" * 40)
            print("🔄 STEP 3: 闭环验证（正向生成 → 比较）...")
            print("-" * 40)

            verification_result = self._verify_by_regeneration(
                article_content,
                image_paths,
                candidates,
                folder
            )

            if "error" in verification_result:
                print(f"  ⚠ 验证过程出错: {verification_result['error']}")
                print("  → 跳过验证，不保存学习结果")
                return {
                    "folder": folder_path,
                    "article": str(article_path),
                    "analysis": analysis,
                    "candidates": candidates,
                    "verification": verification_result,
                    "learning": {"frameworks_added": 0, "charts_added": 0, "styles_added": 0},
                    "summary": self._get_summary(0, 0, 0)
                }

            # 检查是否通过验证
            if not verification_result.get("passed", False):
                print(f"\n  ✗ 验证未通过 (分数: {verification_result.get('average_score', 0)}/{self.pass_threshold})")
                print(f"  → 原因: {verification_result.get('verdict', 'N/A')}")
                print("  → 学习结果未保存")

                return {
                    "folder": folder_path,
                    "article": str(article_path),
                    "analysis": analysis,
                    "candidates": candidates,
                    "verification": verification_result,
                    "learning": {"frameworks_added": 0, "charts_added": 0, "styles_added": 0},
                    "summary": self._get_summary(0, 0, 0)
                }

            print(f"\n  ✓ 验证通过! (分数: {verification_result.get('average_score', 0)}/{self.pass_threshold})")

        # 5. 持久化学习结果
        print("\n" + "-" * 40)
        print("💾 STEP 4: 保存学习结果...")
        print("-" * 40)

        learning_result = self._persist_candidates(candidates)

        # 6. 汇总结果
        result = {
            "folder": folder_path,
            "article": str(article_path),
            "images": [str(p) for p in image_paths],
            "analysis": analysis,
            "verification": verification_result,
            "learning": learning_result,
            "summary": self._get_summary(
                learning_result.get("frameworks_added", 0),
                learning_result.get("charts_added", 0),
                learning_result.get("styles_added", 0)
            )
        }

        # 打印结果
        print("\n" + "=" * 60)
        print("📊 学习完成!")
        print("=" * 60)
        print(f"新增 Frameworks: {result['summary']['frameworks_added']}")
        print(f"新增 Chart Types: {result['summary']['charts_added']}")
        print(f"新增 Visual Styles: {result['summary']['styles_added']}")
        if self.verify and verification_result.get("passed"):
            print(f"验证分数: {verification_result.get('average_score', 0)}")
        print("-" * 40)
        print(f"框架库总数: {result['summary']['total_frameworks']}")
        print(f"图表库总数: {result['summary']['total_charts']}")
        print(f"风格库总数: {result['summary']['total_styles']}")
        print("=" * 60)

        return result

    def _get_summary(self, fw_added: int, charts_added: int, styles_added: int) -> dict:
        """生成摘要"""
        return {
            "frameworks_added": fw_added,
            "charts_added": charts_added,
            "styles_added": styles_added,
            "total_frameworks": len(self.registry.frameworks),
            "total_charts": len(self.registry.chart_types),
            "total_styles": len(self.registry.visual_styles)
        }

    def _extract_candidates(self, analysis: dict) -> dict:
        """提取候选内容（不持久化）"""
        candidates = {
            "frameworks": [],
            "charts": [],
            "styles": [],
            "has_new": False
        }

        # 检查新框架
        for fw in analysis.get("frameworks", []):
            fw_id = fw.get("id")
            if fw_id and fw_id not in self.registry.frameworks:
                candidates["frameworks"].append(fw)
                candidates["has_new"] = True
                print(f"  📚 候选框架: {fw.get('name')} ({fw_id})")

        # 检查新图表类型
        for chart in analysis.get("chart_types", []):
            chart_id = chart.get("id")
            if chart_id and chart_id not in self.registry.chart_types:
                candidates["charts"].append(chart)
                candidates["has_new"] = True
                print(f"  📊 候选图表: {chart.get('name')} ({chart_id})")

        # 检查新视觉风格
        for style in analysis.get("visual_styles", []):
            style_id = style.get("id")
            if style_id and style_id not in self.registry.visual_styles:
                candidates["styles"].append(style)
                candidates["has_new"] = True
                print(f"  🎨 候选风格: {style.get('name')} ({style_id})")

        return candidates

    def _verify_by_regeneration(self, article: str, original_images: List[Path],
                                 candidates: dict, output_folder: Path) -> dict:
        """通过重新生成来验证学习结果"""

        # 临时添加候选内容到注册表（不持久化）
        print("  → 临时加载候选知识...")
        for fw in candidates["frameworks"]:
            self.registry.add_framework(fw["id"], fw, persist=False)
        for chart in candidates["charts"]:
            self.registry.add_chart_type(chart["id"], chart, persist=False)
        for style in candidates["styles"]:
            self.registry.add_visual_style(style["id"], style, persist=False)

        try:
            # 正向生成流程
            print("  → 分析文章...")
            analyze_result = self.analyze_skill.run(article)
            if "error" in analyze_result:
                return {"error": f"分析失败: {analyze_result['error']}"}

            print("  → 映射框架...")
            map_result = self.map_skill.run(analyze_result)
            if "error" in map_result:
                return {"error": f"映射失败: {map_result['error']}"}

            print("  → 设计可视化...")
            # 使用候选风格（如果有）
            style_id = candidates["styles"][0]["id"] if candidates["styles"] else None
            design_skill = DesignSkill(style_id)
            design_result = design_skill.run(map_result)
            if "error" in design_result:
                return {"error": f"设计失败: {design_result['error']}"}

            # 生成图片
            print("  → 生成验证图片...")
            verify_output_dir = output_folder / "_verify_temp"
            verify_output_dir.mkdir(exist_ok=True)

            self.generate_skill = GenerateSkill(str(verify_output_dir))

            # 只生成前3张用于验证
            designs = design_result.get("designs", [])[:3]
            generated_images = []

            for i, design in enumerate(designs):
                result = self.generate_skill.run(
                    design.get("image_prompt"),
                    f"verify_{i+1}"
                )
                if result.get("success") and result.get("output_path"):
                    generated_images.append(Path(result["output_path"]))
                    print(f"    ✓ 生成: verify_{i+1}")

            if not generated_images:
                return {"error": "未能生成任何验证图片"}

            # 比较图片
            print("  → 比较原始图片与生成图片...")
            comparison_result = self._compare_images(
                original_images[:5],  # 原始图片取前5张
                generated_images
            )

            # 清理临时文件
            import shutil
            if verify_output_dir.exists():
                shutil.rmtree(verify_output_dir)

            return comparison_result

        except Exception as e:
            return {"error": str(e)}
        finally:
            # 移除临时添加的候选内容
            for fw in candidates["frameworks"]:
                if fw["id"] in self.registry.frameworks:
                    del self.registry.frameworks[fw["id"]]
            for chart in candidates["charts"]:
                if chart["id"] in self.registry.chart_types:
                    del self.registry.chart_types[chart["id"]]
            for style in candidates["styles"]:
                if style["id"] in self.registry.visual_styles:
                    del self.registry.visual_styles[style["id"]]

    def _compare_images(self, original_paths: List[Path], generated_paths: List[Path]) -> dict:
        """使用多模态AI比较两组图片"""

        # 加载原始图片
        original_images = []
        for img_path in original_paths:
            try:
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    ext = img_path.suffix.lower()
                    mime_type = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                               '.png': 'image/png', '.gif': 'image/gif',
                               '.webp': 'image/webp'}.get(ext, 'image/jpeg')
                    original_images.append({"mime_type": mime_type, "data": img_base64})
            except:
                continue

        # 加载生成图片
        generated_images = []
        for img_path in generated_paths:
            try:
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    ext = img_path.suffix.lower()
                    mime_type = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                               '.png': 'image/png', '.gif': 'image/gif',
                               '.webp': 'image/webp'}.get(ext, 'image/jpeg')
                    generated_images.append({"mime_type": mime_type, "data": img_base64})
            except:
                continue

        if not original_images or not generated_images:
            return {"error": "无法加载比较图片"}

        # 构建比较prompt
        prompt = f"""## 图片比较任务

我会给你两组图片：
- 前 {len(original_images)} 张是【原始示例图片】
- 后 {len(generated_images)} 张是【新生成的图片】

请比较这两组图片，评估新生成的图片是否成功复现了原始示例的风格和内容。

{VERIFY_PROMPT}
"""

        # 合并所有图片
        all_images = original_images + generated_images

        try:
            response = self.client.generate_with_images(prompt, all_images)

            # 解析JSON
            text = response.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()

            result = json.loads(text)

            # 根据阈值判断是否通过
            avg_score = result.get("average_score", 0)
            result["passed"] = avg_score >= self.pass_threshold

            return result

        except json.JSONDecodeError as e:
            return {"error": f"JSON解析失败: {str(e)}", "passed": False}
        except Exception as e:
            return {"error": str(e), "passed": False}

    def _persist_candidates(self, candidates: dict) -> dict:
        """持久化候选内容"""
        result = {
            "frameworks_added": 0,
            "charts_added": 0,
            "styles_added": 0,
            "new_frameworks": [],
            "new_charts": [],
            "new_styles": []
        }

        for fw in candidates["frameworks"]:
            self.registry.add_framework(fw["id"], fw, persist=True)
            result["frameworks_added"] += 1
            result["new_frameworks"].append(fw)
            print(f"  ✓ 保存框架: {fw.get('name')} ({fw['id']})")

        for chart in candidates["charts"]:
            self.registry.add_chart_type(chart["id"], chart, persist=True)
            result["charts_added"] += 1
            result["new_charts"].append(chart)
            print(f"  ✓ 保存图表: {chart.get('name')} ({chart['id']})")

        for style in candidates["styles"]:
            self.registry.add_visual_style(style["id"], style, persist=True)
            result["styles_added"] += 1
            result["new_styles"].append(style)
            print(f"  ✓ 保存风格: {style.get('name')} ({style['id']})")

        return result

    def _find_article(self, folder: Path) -> Tuple[Path, str]:
        """查找文章文件"""
        for ext in ARTICLE_EXTENSIONS:
            for file in folder.glob(f"*{ext}"):
                try:
                    content = file.read_text(encoding='utf-8')
                    if len(content) > 100:  # 至少100字符
                        return file, content
                except:
                    continue
        return None, None

    def _find_images(self, folder: Path) -> List[Path]:
        """查找图片文件"""
        images = []
        for ext in IMAGE_EXTENSIONS:
            images.extend(folder.glob(f"*{ext}"))
            images.extend(folder.glob(f"*{ext.upper()}"))
        # 按文件名排序
        return sorted(images, key=lambda p: p.name)

    def _analyze_example(self, article: str, image_paths: List[Path]) -> dict:
        """使用多模态AI分析示例"""
        # 构建prompt
        prompt = ANALYZE_EXAMPLE_PROMPT.format(
            article=article[:8000],  # 限制文章长度
            image_count=len(image_paths)
        )

        # 读取图片并转为base64
        images_data = []
        for img_path in image_paths[:10]:  # 最多10张图
            try:
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

                    # 确定MIME类型
                    ext = img_path.suffix.lower()
                    mime_map = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp'
                    }
                    mime_type = mime_map.get(ext, 'image/jpeg')

                    images_data.append({
                        "mime_type": mime_type,
                        "data": img_base64
                    })
                    print(f"  ✓ 加载图片: {img_path.name}")
            except Exception as e:
                print(f"  ✗ 加载失败: {img_path.name} - {e}")

        if not images_data:
            return {"error": "无法加载任何图片"}

        # 调用多模态API
        try:
            response = self.client.generate_with_images(prompt, images_data)

            # 解析JSON
            text = response.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()

            return json.loads(text)

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return {"error": f"JSON解析失败: {str(e)}", "raw_response": response}
        except Exception as e:
            return {"error": str(e)}

    def _learn_from_analysis(self, analysis: dict) -> dict:
        """从分析结果中学习新内容"""
        result = {
            "frameworks_added": 0,
            "charts_added": 0,
            "styles_added": 0,
            "new_frameworks": [],
            "new_charts": [],
            "new_styles": []
        }

        # 学习新框架
        for fw in analysis.get("frameworks", []):
            fw_id = fw.get("id")
            if fw_id and fw_id not in self.registry.frameworks:
                self.registry.add_framework(fw_id, fw, persist=True)
                result["frameworks_added"] += 1
                result["new_frameworks"].append(fw)
                print(f"  📚 新增框架: {fw.get('name')} ({fw_id})")

        # 学习新图表类型
        for chart in analysis.get("chart_types", []):
            chart_id = chart.get("id")
            if chart_id and chart_id not in self.registry.chart_types:
                self.registry.add_chart_type(chart_id, chart, persist=True)
                result["charts_added"] += 1
                result["new_charts"].append(chart)
                print(f"  📊 新增图表: {chart.get('name')} ({chart_id})")

        # 学习新视觉风格
        for style in analysis.get("visual_styles", []):
            style_id = style.get("id")
            if style_id and style_id not in self.registry.visual_styles:
                self.registry.add_visual_style(style_id, style, persist=True)
                result["styles_added"] += 1
                result["new_styles"].append(style)
                print(f"  🎨 新增风格: {style.get('name')} ({style_id})")

        if result["frameworks_added"] == 0 and result["charts_added"] == 0 and result["styles_added"] == 0:
            print("  ℹ 未发现新内容，现有库已包含这些知识")

        return result


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python learn_example.py <folder_path>")
        sys.exit(1)

    skill = LearnExampleSkill()
    result = skill.run(sys.argv[1])

    if "error" in result:
        print(f"错误: {result['error']}")
    else:
        print(f"\n分析备注: {result['analysis'].get('analysis_notes', 'N/A')}")
