#!/usr/bin/env python3
"""
Concept Visualizer Agent - 开放式概念可视化Agent
将文章转化为科学风格概念图，支持自定义框架、图表类型和多模型

Usage:
    python agent.py                     # 交互模式
    python agent.py /pipeline <file>    # 执行完整流水线
    python agent.py /analyze <file>     # 仅分析文章
    python agent.py /help               # 显示帮助
"""

import sys
import json
import readline
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from skills import (
    AnalyzeSkill,
    MapFrameworkSkill,
    DesignSkill,
    GenerateSkill,
    PipelineSkill,
    DiscoverSkill,
    LearnExampleSkill
)
from lib.registry import registry
from lib.api import ProviderFactory


class ConceptVisualizerAgent:
    """开放式概念可视化Agent"""

    def __init__(self):
        self.skills = {
            "analyze": AnalyzeSkill(),
            "map": MapFrameworkSkill(),
            "design": DesignSkill(),
            "generate": GenerateSkill(),
            "pipeline": PipelineSkill(),
            "discover": DiscoverSkill(),
            "learn": LearnExampleSkill(),
        }

        self.registry = registry
        self.context = {}

        self.banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎨 CONCEPT VISUALIZER AGENT (Polymathic Edition)           ║
║                                                              ║
║   海纳百川的博学家Agent                                        ║
║   - 自动学习：从文章中发现新理论框架                             ║
║   - 可扩展框架库 (frameworks/)                                 ║
║   - 可扩展图表类型 (chart_types/)                              ║
║   - 多模型支持 (Google/OpenAI/Anthropic/Ollama)               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

    def show_help(self):
        """显示帮助信息"""
        # 获取可用框架和图表类型数量
        n_frameworks = len(self.registry.list_frameworks())
        n_charts = len(self.registry.list_chart_types())
        n_styles = len(self.registry.list_visual_styles())

        help_text = f"""
📚 可用技能 (Skills)
═══════════════════════════════════════════════════════════════

/pipeline <文章路径> [输出目录] [--no-learn] [--style=样式ID]
    一键执行完整workflow，自动学习新框架并生成概念图
    示例: /pipeline article.md ./output
    示例: /pipeline article.md --style=modern
    添加 --no-learn 可跳过框架学习
    添加 --style=<ID> 可跳过交互式样式选择
    可用样式: blueprint(默认), modern, academic, creative

/discover <文章路径>
    🎓 从文章中发现新理论框架并自动扩充框架库
    这是Agent的"博学家"能力核心

/learn <示例文件夹> [--no-verify] [--threshold=70]
    📚 从示例学习：分析文件夹中的文章+图片
    自动提取并添加新的 frameworks、charts、styles
    包含闭环验证：正向生成 → 比较 → 确认后保存
    示例: /learn ./examples/soul_document
    跳过验证: /learn ./examples --no-verify
    自定义阈值: /learn ./examples --threshold=80

/analyze <文章路径或文本>
    分析文章，提取核心概念和关键引文

/map
    将分析结果映射到理论框架（需要先执行 /analyze）

/design [--style=<风格>]
    设计可视化方案和图像提示词（需要先执行 /map）

/generate [prompt_index]
    生成图像（需要先执行 /design）

═══════════════════════════════════════════════════════════════

🎓 知识管理 (海纳百川)
═══════════════════════════════════════════════════════════════

/frameworks              列出所有理论框架 ({n_frameworks}个)
/frameworks show <id>    显示框架详情
/frameworks add <id>     手动添加新框架（交互式）

/charts                  列出所有图表类型 ({n_charts}个)
/styles                  列出所有视觉风格 ({n_styles}个)
/providers               列出所有模型提供商

/reload                  重新加载所有配置（从YAML文件）

═══════════════════════════════════════════════════════════════

📊 状态与导出
═══════════════════════════════════════════════════════════════

/status                  查看当前上下文和知识库状态
/export <文件名>         导出当前结果为JSON
/clear                   清除上下文缓存

/help                    显示此帮助信息
/quit 或 /exit           退出Agent

═══════════════════════════════════════════════════════════════

💡 博学家进化之路:
1. 每次 /pipeline 自动从文章中学习新框架
2. 单独使用 /discover 专注于框架发现
3. 使用 /learn 从示例作品反向学习 (frameworks + charts + styles)
4. 框架自动保存到 frameworks/、chart_types/、visual_styles/ 目录
5. 知识库随着阅读不断扩充
"""
        print(help_text)

    def show_status(self):
        """显示当前状态"""
        print("\n📊 当前上下文状态")
        print("─" * 40)

        if not self.context:
            print("(空)")
        else:
            if "analyze" in self.context:
                concepts = self.context["analyze"].get("key_concepts", [])
                print(f"✓ 分析完成: {len(concepts)} 个概念")

            if "map" in self.context:
                mappings = self.context["map"].get("mappings", [])
                print(f"✓ 框架映射: {len(mappings)} 个映射")

            if "design" in self.context:
                designs = self.context["design"].get("designs", [])
                print(f"✓ 可视化设计: {len(designs)} 个设计")

            if "generate" in self.context:
                results = self.context["generate"]
                success = sum(1 for r in results if r.get("success"))
                print(f"✓ 图像生成: {success}/{len(results)} 成功")

        print("─" * 40)

        # 显示配置状态
        print("\n⚙️ 当前配置")
        print("─" * 40)
        print(f"理论框架: {len(self.registry.list_frameworks())} 个")
        print(f"图表类型: {len(self.registry.list_chart_types())} 个")
        print(f"视觉风格: {len(self.registry.list_visual_styles())} 个")

        providers = ProviderFactory.list_available()
        enabled = [p for p, info in providers.items() if info.get("is_available")]
        print(f"可用模型: {', '.join(enabled) if enabled else '无'}")
        print("─" * 40)

    def list_frameworks(self):
        """列出所有框架"""
        frameworks = self.registry.list_frameworks()
        print(f"\n📚 理论框架库 ({len(frameworks)}个)")
        print("─" * 50)

        for fid, f in frameworks.items():
            print(f"  [{fid}] {f.get('name', fid)}")
            print(f"      {f.get('description', '')[:50]}...")
            print()

        print("─" * 50)
        print("使用 /frameworks show <id> 查看详情")
        print("在 frameworks/ 目录添加 YAML 文件来扩展")

    def show_framework(self, framework_id: str):
        """显示框架详情"""
        f = self.registry.get_framework(framework_id)
        if not f:
            print(f"未找到框架: {framework_id}")
            return

        print(f"\n📖 {f.get('name', framework_id)}")
        print("─" * 50)
        print(f"ID: {framework_id}")
        print(f"英文名: {f.get('name_en', 'N/A')}")
        print(f"来源: {f.get('origin', 'N/A')}")
        print(f"\n描述: {f.get('description', 'N/A')}")
        print(f"英文描述: {f.get('description_en', 'N/A')}")
        print(f"\n关键词: {', '.join(f.get('keywords', []))}")
        print(f"视觉元素: {', '.join(f.get('visual_elements', []))}")
        print(f"适用场景: {f.get('use_when', 'N/A')}")
        if f.get('anti_pattern'):
            print(f"对立模式: {f.get('anti_pattern')}")
        print("─" * 50)

    def add_framework_interactive(self, framework_id: str):
        """交互式添加框架"""
        print(f"\n📝 添加新框架: {framework_id}")
        print("─" * 40)

        framework = {"id": framework_id}

        framework["name"] = input("名称 (中英文): ").strip()
        framework["name_en"] = input("英文名: ").strip()
        framework["origin"] = input("来源/出处: ").strip()
        framework["description"] = input("描述 (中文): ").strip()
        framework["description_en"] = input("描述 (英文): ").strip()

        keywords = input("关键词 (逗号分隔): ").strip()
        framework["keywords"] = [k.strip() for k in keywords.split(",") if k.strip()]

        visuals = input("视觉元素 (逗号分隔): ").strip()
        framework["visual_elements"] = [v.strip() for v in visuals.split(",") if v.strip()]

        framework["use_when"] = input("适用场景: ").strip()
        framework["anti_pattern"] = input("对立模式 (可选): ").strip() or None

        # 保存
        self.registry.add_framework(framework_id, framework, persist=True)
        print(f"\n✓ 框架已添加并保存到 frameworks/{framework_id}.yaml")

    def list_charts(self):
        """列出所有图表类型"""
        charts = self.registry.list_chart_types()
        print(f"\n📊 图表类型库 ({len(charts)}个)")
        print("─" * 50)

        for cid, c in charts.items():
            print(f"  [{cid}] {c.get('name', cid)} ({c.get('name_en', '')})")
            print(f"      适用: {', '.join(c.get('best_for', [])[:3])}...")
            print()

        print("─" * 50)
        print("在 chart_types/ 目录添加 YAML 文件来扩展")

    def list_styles(self):
        """列出所有视觉风格"""
        styles = self.registry.list_visual_styles()
        print(f"\n🎨 视觉风格 ({len(styles)}个)")
        print("─" * 50)

        for sid, s in styles.items():
            print(f"  [{sid}] {s.get('name', sid)}")
            print(f"      {s.get('description', '')}")
            print()

        print("─" * 50)

    def list_providers(self):
        """列出所有提供商"""
        providers = ProviderFactory.list_available()
        print(f"\n🔌 模型提供商")
        print("─" * 50)

        for pid, info in providers.items():
            status = "✓" if info.get("is_available") else "✗"
            features = []
            if info.get("has_text"):
                features.append("文本")
            if info.get("has_image"):
                features.append("图像")

            print(f"  {status} [{pid}] {info.get('name')}")
            print(f"      功能: {', '.join(features)}")
            print(f"      状态: {'可用' if info.get('is_available') else '未配置'}")
            print()

        print("─" * 50)
        print("设置环境变量来启用更多提供商:")
        print("  OPENAI_API_KEY, ANTHROPIC_API_KEY, STABILITY_API_KEY")

    def export_results(self, filename: str):
        """导出结果"""
        if not self.context:
            print("没有可导出的结果")
            return

        output_path = Path(filename)
        if not output_path.suffix:
            output_path = output_path.with_suffix(".json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.context, f, ensure_ascii=False, indent=2, default=str)

        print(f"✓ 结果已导出: {output_path}")

    def handle_command(self, command: str) -> bool:
        """处理命令"""
        parts = command.strip().split(maxsplit=1)
        if not parts:
            return True

        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd.startswith("/"):
            cmd = cmd[1:]

        # 退出
        if cmd in ["quit", "exit", "q"]:
            print("👋 再见!")
            return False

        # 帮助
        if cmd == "help":
            self.show_help()
            return True

        # 状态
        if cmd == "status":
            self.show_status()
            return True

        # 清除
        if cmd == "clear":
            self.context = {}
            print("✓ 上下文已清除")
            return True

        # 导出
        if cmd == "export":
            self.export_results(args or "results.json")
            return True

        # 重新加载
        if cmd == "reload":
            self.registry.reload()
            print("✓ 配置已重新加载")
            return True

        # 框架管理
        if cmd == "frameworks":
            if not args:
                self.list_frameworks()
            elif args.startswith("show "):
                self.show_framework(args[5:].strip())
            elif args.startswith("add "):
                self.add_framework_interactive(args[4:].strip())
            else:
                self.list_frameworks()
            return True

        # 图表类型
        if cmd == "charts":
            self.list_charts()
            return True

        # 视觉风格
        if cmd == "styles":
            self.list_styles()
            return True

        # 提供商
        if cmd == "providers":
            self.list_providers()
            return True

        # Discover (框架发现)
        if cmd == "discover":
            if not args:
                print("请提供文章路径: /discover <文章路径>")
                return True

            result = self.skills["discover"].run(args)
            self.context["discover"] = result

            if "error" not in result:
                print(self.skills["discover"].format_output(result))
            return True

        # Learn (从示例学习)
        if cmd == "learn":
            if not args:
                print("请提供示例文件夹路径: /learn <文件夹路径> [--no-verify] [--threshold=70]")
                print("文件夹应包含: 1个文章文件(.md/.txt) + 多张生成的图片(.jpg/.png)")
                print("\n选项:")
                print("  --no-verify      跳过闭环验证，直接保存学习结果")
                print("  --threshold=N    设置验证通过阈值 (默认70)")
                return True

            # 解析参数
            parts = args.split()
            folder_path = parts[0]
            verify = True
            threshold = 70

            for part in parts[1:]:
                if part == "--no-verify":
                    verify = False
                elif part.startswith("--threshold="):
                    try:
                        threshold = int(part.split("=")[1])
                    except:
                        pass

            # 创建带参数的技能实例
            learn_skill = LearnExampleSkill(verify=verify, pass_threshold=threshold)
            result = learn_skill.run(folder_path)
            self.context["learn"] = result

            if "error" in result:
                print(f"❌ 错误: {result['error']}")
            else:
                # 显示分析备注
                notes = result.get("analysis", {}).get("analysis_notes", "")
                if notes:
                    print(f"\n📝 分析备注: {notes}")

                # 显示验证结果
                verification = result.get("verification", {})
                if not verification.get("skipped"):
                    if verification.get("passed"):
                        print(f"\n✓ 验证通过")
                        analysis = verification.get("analysis", {})
                        if analysis.get("strengths"):
                            print(f"  优点: {', '.join(analysis['strengths'])}")
                    else:
                        print(f"\n✗ 验证未通过")
                        analysis = verification.get("analysis", {})
                        if analysis.get("weaknesses"):
                            print(f"  问题: {', '.join(analysis['weaknesses'])}")
                        if analysis.get("suggestions"):
                            print(f"  建议: {', '.join(analysis['suggestions'])}")

            return True

        # Pipeline
        if cmd == "pipeline":
            if not args:
                print("请提供文章路径: /pipeline <文章路径>")
                return True

            parts = args.split()
            article_path = parts[0]
            output_dir = None
            auto_learn = True
            style = None

            for part in parts[1:]:
                if part == "--no-learn":
                    auto_learn = False
                elif part.startswith("--style="):
                    style = part.split("=", 1)[1]
                elif not part.startswith("--"):
                    output_dir = part

            # 如果指定了 style，则跳过交互选择
            interactive_style = (style is None)
            skill = PipelineSkill(output_dir, auto_learn=auto_learn, style=style, interactive_style=interactive_style)
            result = skill.run(article_path)
            self.context = result.get("steps", {})
            self.context["learning"] = result.get("learning", {})
            return True

        # 分析
        if cmd == "analyze":
            if not args:
                print("请提供文章路径或文本: /analyze <文章路径>")
                return True

            result = self.skills["analyze"].run(args)
            self.context["analyze"] = result

            if "error" not in result:
                print(self.skills["analyze"].format_output(result))
            return True

        # 映射
        if cmd == "map":
            if "analyze" not in self.context:
                print("请先执行 /analyze")
                return True

            result = self.skills["map"].run(self.context["analyze"])
            self.context["map"] = result

            if "error" not in result:
                print(self.skills["map"].format_output(result))
            return True

        # 设计
        if cmd == "design":
            if "map" not in self.context:
                print("请先执行 /map")
                return True

            style = None
            if args.startswith("--style="):
                style = args.split("=")[1]

            skill = DesignSkill(style)
            result = skill.run(self.context["map"])
            self.context["design"] = result

            if "error" not in result:
                print(skill.format_output(result))
            return True

        # 生成
        if cmd == "generate":
            if "design" not in self.context:
                print("请先执行 /design")
                return True

            designs = self.context["design"].get("designs", [])

            if args:
                try:
                    idx = int(args) - 1
                    if 0 <= idx < len(designs):
                        result = self.skills["generate"].run(
                            designs[idx].get("image_prompt"),
                            designs[idx].get("title")
                        )
                        self.context.setdefault("generate", []).append(result)
                    else:
                        print(f"索引超出范围 (1-{len(designs)})")
                except ValueError:
                    print("请提供有效的索引数字")
            else:
                results = self.skills["generate"].run_batch(designs)
                self.context["generate"] = results
                print(self.skills["generate"].format_output(results))

            return True

        # 未知命令
        print(f"未知命令: {cmd}")
        print("输入 /help 查看可用命令")
        return True

    def run_interactive(self):
        """运行交互模式"""
        print(self.banner)
        self.show_help()

        while True:
            try:
                command = input("\n🤖 > ").strip()

                if not command:
                    continue

                if not self.handle_command(command):
                    break

            except KeyboardInterrupt:
                print("\n\n👋 再见!")
                break
            except EOFError:
                print("\n\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

    def run_command(self, command: str):
        """运行单个命令"""
        self.handle_command(command)


def main():
    agent = ConceptVisualizerAgent()

    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        agent.run_command(command)
    else:
        agent.run_interactive()


if __name__ == "__main__":
    main()
