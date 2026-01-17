"""
Concept Visualizer Agent - Configuration
开放式配置，支持扩展理论框架、图表类型和模型接口
"""

import os
from pathlib import Path

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有安装 python-dotenv，尝试手动加载
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

# =============================================================================
# 路径配置
# =============================================================================

BASE_DIR = Path(__file__).parent
FRAMEWORKS_DIR = BASE_DIR / "frameworks"      # 理论框架目录
CHART_TYPES_DIR = BASE_DIR / "chart_types"    # 图表类型目录
VISUAL_STYLES_DIR = BASE_DIR / "visual_styles"  # 视觉风格目录
PROVIDERS_DIR = BASE_DIR / "providers"        # 模型提供商目录
OUTPUT_DIR = BASE_DIR / "output"              # 输出目录

# 确保目录存在
for d in [FRAMEWORKS_DIR, CHART_TYPES_DIR, VISUAL_STYLES_DIR, PROVIDERS_DIR, OUTPUT_DIR]:
    d.mkdir(exist_ok=True)

# =============================================================================
# 模型提供商配置 (多模型支持)
# =============================================================================

PROVIDERS = {
    "google": {
        "name": "Google AI Studio",
        "api_key_env": "GOOGLE_API_KEY",
        "api_key": os.environ.get("GOOGLE_API_KEY", ""),  # 从环境变量读取
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "text_model": "gemini-3-flash-preview",
        "image_model": "gemini-3-pro-image-preview",
        "enabled": True
    },
    "openai": {
        "name": "OpenAI",
        "api_key_env": "OPENAI_API_KEY",
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "text_model": "gpt-4o",
        "image_model": "dall-e-3",
        "enabled": False  # 需要配置API key后启用
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "api_key_env": "ANTHROPIC_API_KEY",
        "api_key": "",
        "base_url": "https://api.anthropic.com/v1",
        "text_model": "claude-sonnet-4-20250514",
        "image_model": None,  # Claude不生成图像，需配合其他图像模型
        "enabled": False
    },
    "stability": {
        "name": "Stability AI",
        "api_key_env": "STABILITY_API_KEY",
        "api_key": "",
        "base_url": "https://api.stability.ai/v1",
        "text_model": None,
        "image_model": "stable-diffusion-xl-1024-v1-0",
        "enabled": False
    },
    "ollama": {
        "name": "Ollama (Local)",
        "api_key_env": None,
        "api_key": None,
        "base_url": "http://localhost:11434/api",
        "text_model": "llama3",
        "image_model": None,
        "enabled": False
    }
}

# 当前使用的提供商
DEFAULT_TEXT_PROVIDER = "google"
DEFAULT_IMAGE_PROVIDER = "google"

# =============================================================================
# 视觉风格配置 (可自定义)
# =============================================================================

VISUAL_STYLES = {
    "blueprint": {
        "name": "技术蓝图风格",
        "description": "工程图纸风格，适合技术/学术内容",
        "template": """Technical blueprint-style infographic on light beige/cream graph paper background with subtle grid lines.
Title: "{title}" in dark red capital letters at the top, using Crimson Pro or similar bold serif font.
{visual_description}
Color palette:
- Background: Light beige/cream (#F5F0E1) with subtle grid
- Primary accent: Teal blue (#2F337)
- Secondary: Warm brown/gold tones
- Highlights: Deep red for titles and emphasis
Style: Clean technical illustration, professional academic diagram aesthetic.
{additional_elements}"""
    },
    "modern": {
        "name": "现代简约风格",
        "description": "简洁现代，适合商业演示",
        "template": """Modern minimalist infographic with clean white background.
Title: "{title}" in bold sans-serif font (like Helvetica or Inter).
{visual_description}
Color palette:
- Background: Pure white or light gray (#F8F9FA)
- Primary: Deep blue (#1A365D)
- Accent: Coral (#FF6B6B) or teal (#38B2AC)
Style: Flat design, sharp edges, minimal shadows, professional corporate feel.
{additional_elements}"""
    },
    "academic": {
        "name": "学术论文风格",
        "description": "严谨学术，适合研究内容",
        "template": """Academic paper figure style with minimal decoration.
Title: "{title}" in Times New Roman or similar serif font.
{visual_description}
Color palette:
- Background: White
- Primary: Black and dark gray
- Accent: Single accent color (blue or red)
Style: High contrast, clear labels, suitable for print publication.
{additional_elements}"""
    },
    "creative": {
        "name": "创意艺术风格",
        "description": "艺术感强，适合创意内容",
        "template": """Creative artistic infographic with gradient backgrounds.
Title: "{title}" in creative display font with subtle effects.
{visual_description}
Color palette:
- Background: Gradient (purple to blue or orange to pink)
- Elements: White and light colors for contrast
- Accents: Neon or vibrant highlights
Style: Modern, artistic, with subtle 3D effects and glows.
{additional_elements}"""
    }
}

DEFAULT_VISUAL_STYLE = "blueprint"

# =============================================================================
# 默认内置框架 (会被 frameworks/ 目录下的YAML文件扩展)
# =============================================================================

DEFAULT_FRAMEWORKS = {
    "agapism": {
        "name": "Agapism (爱智论)",
        "name_en": "Agapism",
        "origin": "Charles Sanders Peirce",
        "description": "通过吸引/爱/内在驱动实现发展，而非外部强制",
        "description_en": "Evolution through attraction, love, or internal motivation rather than external force",
        "keywords": ["attraction", "love", "internal motivation", "identity", "desire", "sympathy"],
        "anti_pattern": "anancism",
        "visual_elements": ["magnetic field lines", "attractor basin", "flowing curves", "convergence"],
        "use_when": "概念涉及内在动机、价值认同、自发趋向"
    },
    "anancism": {
        "name": "Anancism (必然论)",
        "name_en": "Anancism",
        "origin": "Charles Sanders Peirce",
        "description": "通过规则、约束、机械因果实现控制",
        "description_en": "Evolution through mechanical necessity, rules, and constraints",
        "keywords": ["rules", "constraints", "mechanical", "rigid", "hardcoded", "necessity"],
        "anti_pattern": "agapism",
        "visual_elements": ["geometric lattice", "rigid structures", "interlocking beams", "grid"],
        "use_when": "概念涉及硬性规则、机械约束、强制执行"
    },
    "goodhart": {
        "name": "Goodhart's Law (古德哈特定律)",
        "name_en": "Goodhart's Law",
        "origin": "Charles Goodhart",
        "description": "当度量成为目标时，它就不再是好的度量",
        "description_en": "When a measure becomes a target, it ceases to be a good measure",
        "keywords": ["metric", "optimization", "gaming", "proxy", "gap", "target"],
        "visual_elements": ["diverging lines", "gap visualization", "optimization curves", "metric vs goal"],
        "use_when": "概念涉及优化陷阱、指标失效、目标与度量的偏离"
    },
    "moloch": {
        "name": "Moloch Trap (莫洛克陷阱)",
        "name_en": "Moloch Trap",
        "origin": "Scott Alexander / Coordination Theory",
        "description": "个体理性导致集体非理性的协调失败",
        "description_en": "Coordination failure where individual rationality leads to collective irrationality",
        "keywords": ["coordination", "collective", "trap", "race", "competition", "tragedy"],
        "visual_elements": ["converging arrows to pit", "trap structure", "race to bottom", "prisoners dilemma"],
        "use_when": "概念涉及协调失败、竞争困境、集体行动问题"
    },
    "participatory_knowing": {
        "name": "Participatory Knowing (参与式认知)",
        "name_en": "Participatory Knowing",
        "origin": "John Vervaeke",
        "description": "通过身份认同和参与而非命题知识来理解",
        "description_en": "Understanding through identity and participation rather than propositional knowledge",
        "keywords": ["identity", "being", "participation", "embodiment", "becoming"],
        "visual_elements": ["interconnected nodes", "identity core", "radiating connections", "nested circles"],
        "use_when": "概念涉及身份构建、内化价值、存在性理解"
    },
    "multi_scale": {
        "name": "Multi-Scale Alignment (多尺度对齐)",
        "name_en": "Multi-Scale Alignment",
        "origin": "Systems Theory / AI Alignment",
        "description": "不同层级目标之间的协调与约束传递",
        "description_en": "Coordination and constraint propagation across different hierarchical levels",
        "keywords": ["hierarchy", "levels", "priority", "constraint", "flow", "scale"],
        "visual_elements": ["pyramid", "layered structure", "bidirectional arrows", "nested hierarchy"],
        "use_when": "概念涉及层级结构、优先级排序、跨层级协调"
    },
    "circuit_breaker": {
        "name": "Circuit Breaker (断路器模式)",
        "name_en": "Circuit Breaker Pattern",
        "origin": "Software Engineering / Resilience Patterns",
        "description": "检测异常并自动中断以防止级联失败",
        "description_en": "Detecting anomalies and interrupting to prevent cascading failures",
        "keywords": ["detect", "stop", "reset", "monitor", "interrupt", "safeguard"],
        "visual_elements": ["flowchart with decision", "stop sign", "feedback loop", "monitoring"],
        "use_when": "概念涉及安全机制、自检系统、异常处理"
    },
    "attractor": {
        "name": "Attractor Dynamics (吸引子动力学)",
        "name_en": "Attractor Dynamics",
        "origin": "Dynamical Systems Theory",
        "description": "系统自然趋向某些稳定状态的倾向",
        "description_en": "System's natural tendency to evolve toward certain stable states",
        "keywords": ["basin", "valley", "landscape", "salience", "convergence", "stability"],
        "visual_elements": ["3D terrain", "valleys and peaks", "wireframe surface", "basin of attraction"],
        "use_when": "概念涉及稳定状态、自然趋向、能量最小化"
    }
}

# =============================================================================
# 默认图表类型 (会被 chart_types/ 目录下的YAML文件扩展)
# =============================================================================

DEFAULT_CHART_TYPES = {
    "pyramid": {
        "name": "金字塔图",
        "name_en": "Pyramid Chart",
        "description": "展示层级关系或优先级排序",
        "best_for": ["hierarchy", "priority", "levels", "importance ranking"],
        "template": "3D isometric pyramid with {n_layers} distinct horizontal layers, each labeled",
        "layout": "centered",
        "elements": ["layered pyramid", "level labels", "optional arrows showing flow"]
    },
    "comparison": {
        "name": "对比图",
        "name_en": "Comparison Chart",
        "description": "展示二元对比或对立概念",
        "best_for": ["contrast", "versus", "binary", "trade-off"],
        "template": "Side-by-side comparison layout divided by vertical line",
        "layout": "split",
        "elements": ["left panel", "right panel", "contrasting visuals", "bottom summary"]
    },
    "network": {
        "name": "网络图",
        "name_en": "Network Diagram",
        "description": "展示系统关系或多元连接",
        "best_for": ["relationships", "system", "connections", "dependencies"],
        "template": "Network diagram with {n_nodes} interconnected nodes",
        "layout": "centered",
        "elements": ["nodes", "edges", "labels", "optional clusters"]
    },
    "flowchart": {
        "name": "流程图",
        "name_en": "Flowchart",
        "description": "展示过程、决策或状态转换",
        "best_for": ["process", "decision", "workflow", "state machine"],
        "template": "Flowchart with rectangles, diamonds, and directional arrows",
        "layout": "left-to-right or top-to-bottom",
        "elements": ["process boxes", "decision diamonds", "arrows", "start/end nodes"]
    },
    "terrain": {
        "name": "地形图/热力图",
        "name_en": "Terrain/Heatmap",
        "description": "展示优化空间或权衡关系",
        "best_for": ["optimization", "trade-off", "landscape", "gradient"],
        "template": "3D wireframe surface showing peaks and valleys",
        "layout": "perspective view",
        "elements": ["3D surface", "axis labels", "peak/valley markers", "gradient coloring"]
    },
    "attractor": {
        "name": "吸引子图",
        "name_en": "Attractor Diagram",
        "description": "展示吸引/收敛/磁场效应",
        "best_for": ["attraction", "convergence", "magnetic", "gravity"],
        "template": "Magnetic field-like visualization with central attractor",
        "layout": "centered with radiating lines",
        "elements": ["central attractor", "field lines", "approaching elements", "labels"]
    },
    "timeline": {
        "name": "时间线",
        "name_en": "Timeline",
        "description": "展示时序发展或阶段演进",
        "best_for": ["temporal", "evolution", "phases", "milestones"],
        "template": "Horizontal or vertical timeline with marked events",
        "layout": "linear",
        "elements": ["timeline axis", "event markers", "labels", "connecting lines"]
    },
    "venn": {
        "name": "韦恩图",
        "name_en": "Venn Diagram",
        "description": "展示集合关系或概念重叠",
        "best_for": ["overlap", "intersection", "sets", "shared properties"],
        "template": "Overlapping circles showing intersections",
        "layout": "centered",
        "elements": ["circles", "intersection areas", "labels", "legend"]
    },
    "matrix": {
        "name": "矩阵图",
        "name_en": "Matrix Chart",
        "description": "展示二维分类或象限分析",
        "best_for": ["2x2 analysis", "classification", "quadrants", "positioning"],
        "template": "2x2 or NxM matrix with labeled quadrants",
        "layout": "grid",
        "elements": ["quadrants", "axis labels", "items positioned", "quadrant labels"]
    },
    "cycle": {
        "name": "循环图",
        "name_en": "Cycle Diagram",
        "description": "展示循环过程或反馈回路",
        "best_for": ["cycle", "feedback", "loop", "recurring process"],
        "template": "Circular arrangement with arrows showing flow",
        "layout": "circular",
        "elements": ["circular nodes", "directional arrows", "labels", "center element"]
    }
}
