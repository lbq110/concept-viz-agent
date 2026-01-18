"""
Registry - 开放式注册系统
管理理论框架、图表类型和模型提供商的动态加载
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import (
    FRAMEWORKS_DIR, CHART_TYPES_DIR, PROVIDERS_DIR, VISUAL_STYLES_DIR,
    DEFAULT_FRAMEWORKS, DEFAULT_CHART_TYPES, PROVIDERS,
    VISUAL_STYLES, DEFAULT_VISUAL_STYLE
)


class Registry:
    """统一的注册管理器"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.frameworks: Dict[str, Any] = {}
        self.chart_types: Dict[str, Any] = {}
        self.providers: Dict[str, Any] = {}
        self.visual_styles: Dict[str, Any] = {}

        self._load_all()
        self._initialized = True

    def _load_yaml_files(self, directory: Path) -> Dict[str, Any]:
        """从目录加载所有YAML文件"""
        items = {}
        if not directory.exists():
            return items

        for file in directory.glob("*.yaml"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        # 使用文件名（无扩展名）作为ID，或使用文件中的id字段
                        item_id = data.get("id", file.stem)
                        items[item_id] = data
            except Exception as e:
                print(f"Warning: Failed to load {file}: {e}")

        for file in directory.glob("*.yml"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        item_id = data.get("id", file.stem)
                        items[item_id] = data
            except Exception as e:
                print(f"Warning: Failed to load {file}: {e}")

        return items

    def _load_all(self):
        """加载所有配置"""
        # 加载框架：先加载默认，再加载自定义（自定义覆盖默认）
        self.frameworks = DEFAULT_FRAMEWORKS.copy()
        custom_frameworks = self._load_yaml_files(FRAMEWORKS_DIR)
        self.frameworks.update(custom_frameworks)

        # 加载图表类型
        self.chart_types = DEFAULT_CHART_TYPES.copy()
        custom_charts = self._load_yaml_files(CHART_TYPES_DIR)
        self.chart_types.update(custom_charts)

        # 加载提供商配置
        self.providers = PROVIDERS.copy()
        custom_providers = self._load_yaml_files(PROVIDERS_DIR)
        self.providers.update(custom_providers)

        # 加载视觉风格
        self.visual_styles = VISUAL_STYLES.copy()
        custom_styles = self._load_yaml_files(VISUAL_STYLES_DIR)
        self.visual_styles.update(custom_styles)

    def reload(self):
        """重新加载所有配置"""
        self._load_all()

    # =========================================================================
    # 框架相关方法
    # =========================================================================

    def get_framework(self, framework_id: str) -> Optional[Dict]:
        """获取单个框架"""
        return self.frameworks.get(framework_id)

    def list_frameworks(self) -> Dict[str, Any]:
        """列出所有框架"""
        return self.frameworks

    def add_framework(self, framework_id: str, framework_data: Dict, persist: bool = False):
        """
        添加新框架

        Args:
            framework_id: 框架ID
            framework_data: 框架数据
            persist: 是否持久化到文件
        """
        self.frameworks[framework_id] = framework_data

        if persist:
            file_path = FRAMEWORKS_DIR / f"{framework_id}.yaml"
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(framework_data, f, allow_unicode=True, default_flow_style=False)

    def remove_framework(self, framework_id: str):
        """移除框架"""
        if framework_id in self.frameworks:
            del self.frameworks[framework_id]
            # 也删除文件
            file_path = FRAMEWORKS_DIR / f"{framework_id}.yaml"
            if file_path.exists():
                file_path.unlink()

    def get_frameworks_for_prompt(self) -> str:
        """生成供LLM使用的框架描述"""
        lines = []
        for fid, f in self.frameworks.items():
            lines.append(f"### {f.get('name', fid)} (ID: {fid})")
            lines.append(f"- 描述: {f.get('description', 'N/A')}")
            lines.append(f"- 关键词: {', '.join(f.get('keywords', []))}")
            lines.append(f"- 视觉元素: {', '.join(f.get('visual_elements', []))}")
            lines.append(f"- 适用场景: {f.get('use_when', 'N/A')}")
            if f.get('canonical_chart'):
                suggested = f.get('suggested_charts', [])
                suggested_str = f", 备选: {', '.join(suggested)}" if suggested else ""
                lines.append(f"- 推荐图表: {f.get('canonical_chart')}{suggested_str}")
            lines.append("")
        return "\n".join(lines)

    def get_framework_chart_recommendation(self, framework_id: str) -> dict:
        """
        获取框架的图表推荐

        Args:
            framework_id: 框架ID

        Returns:
            包含图表推荐的字典:
            - canonical_chart: 首选图表类型
            - suggested_charts: 备选图表列表
            - all_recommendations: 所有推荐（首选+备选）
        """
        framework = self.get_framework(framework_id)
        if not framework:
            return {
                "canonical_chart": None,
                "suggested_charts": [],
                "all_recommendations": []
            }

        canonical = framework.get("canonical_chart")
        suggested = framework.get("suggested_charts", [])

        all_recommendations = []
        if canonical:
            all_recommendations.append(canonical)
        all_recommendations.extend([c for c in suggested if c not in all_recommendations])

        return {
            "canonical_chart": canonical,
            "suggested_charts": suggested,
            "all_recommendations": all_recommendations
        }

    # =========================================================================
    # 图表类型相关方法
    # =========================================================================

    def get_chart_type(self, chart_id: str) -> Optional[Dict]:
        """获取单个图表类型"""
        return self.chart_types.get(chart_id)

    def list_chart_types(self) -> Dict[str, Any]:
        """列出所有图表类型"""
        return self.chart_types

    def add_chart_type(self, chart_id: str, chart_data: Dict, persist: bool = False):
        """添加新图表类型"""
        self.chart_types[chart_id] = chart_data

        if persist:
            file_path = CHART_TYPES_DIR / f"{chart_id}.yaml"
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(chart_data, f, allow_unicode=True, default_flow_style=False)

    def get_chart_types_for_prompt(self) -> str:
        """生成供LLM使用的图表类型描述"""
        lines = []
        for cid, c in self.chart_types.items():
            lines.append(f"- **{cid}** ({c.get('name', cid)}): {c.get('description', 'N/A')}")
            lines.append(f"  适用于: {', '.join(c.get('best_for', []))}")
        return "\n".join(lines)

    # =========================================================================
    # 提供商相关方法
    # =========================================================================

    def get_provider(self, provider_id: str) -> Optional[Dict]:
        """获取单个提供商配置"""
        return self.providers.get(provider_id)

    def list_providers(self) -> Dict[str, Any]:
        """列出所有提供商"""
        return self.providers

    def list_enabled_providers(self) -> Dict[str, Any]:
        """列出已启用的提供商"""
        return {k: v for k, v in self.providers.items() if v.get("enabled")}

    def enable_provider(self, provider_id: str, api_key: str = None):
        """启用提供商"""
        if provider_id in self.providers:
            self.providers[provider_id]["enabled"] = True
            if api_key:
                self.providers[provider_id]["api_key"] = api_key

    def disable_provider(self, provider_id: str):
        """禁用提供商"""
        if provider_id in self.providers:
            self.providers[provider_id]["enabled"] = False

    # =========================================================================
    # 视觉风格相关方法
    # =========================================================================

    def get_visual_style(self, style_id: str = None) -> Dict:
        """获取视觉风格"""
        style_id = style_id or DEFAULT_VISUAL_STYLE
        return self.visual_styles.get(style_id, self.visual_styles.get("blueprint"))

    def list_visual_styles(self) -> Dict[str, Any]:
        """列出所有视觉风格"""
        return self.visual_styles

    def add_visual_style(self, style_id: str, style_data: Dict, persist: bool = False):
        """添加新视觉风格"""
        self.visual_styles[style_id] = style_data

        if persist:
            file_path = VISUAL_STYLES_DIR / f"{style_id}.yaml"
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(style_data, f, allow_unicode=True, default_flow_style=False)

    # =========================================================================
    # 导出/导入
    # =========================================================================

    def export_all(self, output_path: str):
        """导出所有配置"""
        data = {
            "frameworks": self.frameworks,
            "chart_types": self.chart_types,
            "visual_styles": self.visual_styles
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_frameworks(self, file_path: str):
        """从文件导入框架"""
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        if isinstance(data, dict):
            if "frameworks" in data:
                self.frameworks.update(data["frameworks"])
            else:
                self.frameworks.update(data)


# 单例实例
registry = Registry()
