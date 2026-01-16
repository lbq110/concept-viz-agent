"""
Skill: Framework Discovery - 理论框架发现与学习
自动从文章中发现新的理论框架并扩充框架库
让Agent成为海纳百川的博学家
"""

import json
import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).parent.parent))

from lib.api import client
from lib.registry import registry


DISCOVER_PROMPT = '''你是一位博学的跨学科学者，精通哲学、科学方法论、系统论、认知科学、社会学等领域。

**任务：**
分析以下文章，识别其中涉及或暗含的理论框架、方法论、思维模型。

**什么算作"理论框架"：**
1. 哲学概念（如Agapism、Anancism、实用主义、现象学）
2. 科学方法论（如演绎法、归纳法、溯因推理）
3. 系统论概念（如涌现、反馈循环、吸引子）
4. 心理学/认知科学模型（如双系统理论、元认知）
5. 社会学/经济学理论（如博弈论、制度经济学）
6. 工程/设计模式（如断路器、最小权限原则）
7. 任何有名称、有解释力、可复用的思维工具

**已知框架库（用于对比）：**
{known_frameworks}

**文章内容：**
---
{article}
---

**请识别文章中的理论框架，输出JSON格式：**

```json
{{
  "discovered_frameworks": [
    {{
      "id": "framework_id_snake_case",
      "name": "框架名称 (英文名)",
      "name_en": "English Name",
      "origin": "来源（人名/领域/书籍）",
      "description": "框架描述（中文，1-2句话）",
      "description_en": "English description",
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "visual_elements": ["suggested visual element 1", "suggested visual element 2"],
      "use_when": "适用场景（中文）",
      "is_new": true,
      "confidence": 0.9,
      "source_quote": "文章中提到该框架的原文片段"
    }}
  ],
  "existing_matches": [
    {{
      "framework_id": "已存在的框架ID",
      "relevance": "high/medium/low",
      "enrichment": "可以补充到现有框架的新信息（如果有）"
    }}
  ]
}}
```

**注意：**
1. is_new=true 表示这是一个不在已知框架库中的新框架
2. is_new=false 表示它与已知框架相似或相同
3. confidence 表示你对这个框架识别的确信度 (0-1)
4. 不要发明框架，只识别文章中明确提到或强烈暗示的
5. 优先识别有学术/实践价值、可复用的框架
6. 如果框架已存在但文章提供了新视角，放入 existing_matches 的 enrichment

请直接输出JSON，不要有任何其他文字。
'''


ENRICH_PROMPT = '''你是一位博学的学者，负责完善理论框架的定义。

**现有框架：**
```json
{existing_framework}
```

**新发现的补充信息：**
{enrichment}

**来源文章片段：**
{source_quote}

**任务：**
判断是否需要更新现有框架，如果需要，输出更新后的完整框架。

```json
{{
  "should_update": true/false,
  "reason": "更新原因或不更新的理由",
  "updated_framework": {{
    // 如果should_update=true，输出完整的更新后框架
    // 保留原有字段，添加或修改需要更新的部分
  }}
}}
```

请直接输出JSON。
'''


class DiscoverSkill:
    """理论框架发现与学习技能"""

    name = "discover"
    description = "从文章中发现新的理论框架并扩充知识库"
    usage = "/discover <文章路径或文本>"

    def __init__(self, auto_save: bool = True, min_confidence: float = 0.7):
        self.client = client
        self.registry = registry
        self.auto_save = auto_save
        self.min_confidence = min_confidence

    def _get_known_frameworks_summary(self) -> str:
        """获取已知框架的摘要"""
        frameworks = self.registry.list_frameworks()
        lines = []
        for fid, f in frameworks.items():
            keywords = ", ".join(f.get("keywords", [])[:5])
            lines.append(f"- {fid}: {f.get('name', fid)} [{keywords}]")
        return "\n".join(lines)

    def discover(self, article: str) -> dict:
        """
        从文章中发现理论框架

        Args:
            article: 文章内容

        Returns:
            发现结果
        """
        # 如果是文件路径，读取文件
        if isinstance(article, str) and (article.endswith('.md') or article.endswith('.txt')):
            path = Path(article)
            if path.exists():
                article = path.read_text(encoding='utf-8')

        prompt = DISCOVER_PROMPT.format(
            known_frameworks=self._get_known_frameworks_summary(),
            article=article[:20000]  # 限制长度
        )

        print("🔬 正在分析文章中的理论框架...")

        response = self.client.generate_text(prompt)

        # 解析JSON
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response

            result = json.loads(json_str.strip())

            # 统计
            new_frameworks = [f for f in result.get("discovered_frameworks", [])
                           if f.get("is_new") and f.get("confidence", 0) >= self.min_confidence]
            existing = result.get("existing_matches", [])

            print(f"✓ 发现 {len(new_frameworks)} 个新框架")
            print(f"✓ 匹配 {len(existing)} 个已有框架")

            return result

        except json.JSONDecodeError as e:
            print(f"⚠ JSON解析失败: {e}")
            return {"raw_response": response, "error": str(e)}

    def learn(self, discovery_result: dict) -> dict:
        """
        从发现结果中学习，更新框架库

        Args:
            discovery_result: discover() 的返回结果

        Returns:
            学习报告
        """
        if "error" in discovery_result:
            return {"success": False, "error": discovery_result["error"]}

        report = {
            "new_frameworks_added": [],
            "frameworks_enriched": [],
            "skipped": []
        }

        # 处理新框架
        for framework in discovery_result.get("discovered_frameworks", []):
            if not framework.get("is_new"):
                continue

            confidence = framework.get("confidence", 0)
            if confidence < self.min_confidence:
                report["skipped"].append({
                    "id": framework.get("id"),
                    "reason": f"置信度不足 ({confidence:.2f} < {self.min_confidence})"
                })
                continue

            framework_id = framework.get("id")
            if not framework_id:
                continue

            # 检查是否真的是新的
            if self.registry.get_framework(framework_id):
                report["skipped"].append({
                    "id": framework_id,
                    "reason": "框架已存在"
                })
                continue

            # 准备框架数据
            framework_data = {
                "name": framework.get("name"),
                "name_en": framework.get("name_en"),
                "origin": framework.get("origin"),
                "description": framework.get("description"),
                "description_en": framework.get("description_en"),
                "keywords": framework.get("keywords", []),
                "visual_elements": framework.get("visual_elements", []),
                "use_when": framework.get("use_when"),
                "discovered_at": datetime.now().isoformat(),
                "source_quote": framework.get("source_quote"),
                "confidence": confidence
            }

            # 添加到注册表
            if self.auto_save:
                self.registry.add_framework(framework_id, framework_data, persist=True)
                print(f"  📚 新增框架: {framework.get('name')} ({framework_id})")

            report["new_frameworks_added"].append({
                "id": framework_id,
                "name": framework.get("name"),
                "confidence": confidence
            })

        # 处理已有框架的补充
        for match in discovery_result.get("existing_matches", []):
            if match.get("enrichment") and match.get("relevance") == "high":
                framework_id = match.get("framework_id")
                existing = self.registry.get_framework(framework_id)

                if existing and match.get("enrichment"):
                    # 可以选择是否自动更新，这里先记录
                    report["frameworks_enriched"].append({
                        "id": framework_id,
                        "enrichment": match.get("enrichment")
                    })
                    print(f"  💡 可补充框架: {framework_id}")

        return report

    def run(self, article: str) -> dict:
        """
        完整的发现-学习流程

        Args:
            article: 文章内容或路径

        Returns:
            完整结果
        """
        print("=" * 50)
        print("🎓 FRAMEWORK DISCOVERY & LEARNING")
        print("=" * 50)

        # 发现
        discovery = self.discover(article)

        if "error" in discovery:
            return discovery

        # 学习
        learning = self.learn(discovery)

        # 汇总
        result = {
            "discovery": discovery,
            "learning": learning,
            "summary": {
                "new_added": len(learning.get("new_frameworks_added", [])),
                "enriched": len(learning.get("frameworks_enriched", [])),
                "skipped": len(learning.get("skipped", [])),
                "total_frameworks": len(self.registry.list_frameworks())
            }
        }

        print("=" * 50)
        print(f"📊 学习完成:")
        print(f"   新增框架: {result['summary']['new_added']}")
        print(f"   可补充: {result['summary']['enriched']}")
        print(f"   框架库总数: {result['summary']['total_frameworks']}")
        print("=" * 50)

        return result

    def format_output(self, result: dict) -> str:
        """格式化输出"""
        if "error" in result:
            return f"发现失败: {result['error']}"

        lines = [
            "# 理论框架发现报告",
            "",
            f"**框架库总数**: {result['summary']['total_frameworks']}",
            ""
        ]

        # 新增框架
        new_added = result["learning"].get("new_frameworks_added", [])
        if new_added:
            lines.append("## 新增框架")
            lines.append("")
            for f in new_added:
                lines.append(f"- **{f['name']}** (`{f['id']}`) - 置信度: {f['confidence']:.0%}")
            lines.append("")

        # 可补充
        enriched = result["learning"].get("frameworks_enriched", [])
        if enriched:
            lines.append("## 可补充框架")
            lines.append("")
            for f in enriched:
                lines.append(f"- `{f['id']}`: {f['enrichment'][:100]}...")
            lines.append("")

        # 发现的已知框架匹配
        existing = result["discovery"].get("existing_matches", [])
        if existing:
            lines.append("## 匹配的已有框架")
            lines.append("")
            for m in existing:
                lines.append(f"- `{m['framework_id']}` (相关度: {m['relevance']})")
            lines.append("")

        return "\n".join(lines)


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python discover.py <article_file>")
        sys.exit(1)

    skill = DiscoverSkill()
    result = skill.run(sys.argv[1])
    print(skill.format_output(result))
