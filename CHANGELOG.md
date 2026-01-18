# Changelog

All notable changes to Concept Visualizer Agent will be documented in this file.

## [0.3.0] - 2025-01-17

### Changed
- **Blueprint 风格优化**：移除尺寸标注、角落装饰（title block、stamps）
- **信息量提升**：文本框从 2-4 个增加到 3-5 个，包含更多文章原文内容
- **Prompt 扩展**：image_prompt 字数从 200-400 词增加到 300-500 词

### Fixed
- 修复 `map_framework.py` 中 JSON 解析 bug（处理尾部 ``` 符号）

### Added
- 新增 13 个从文章中学习的理论框架

---

## [0.2.0] - 2025-01-16

### Added
- 统一视觉风格系统，支持交互式选择
- 真正的 4K 分辨率支持
- `/learn` 命令：从示例作品学习风格
- 闭环验证机制

### Changed
- 升级到 Gemini 3 模型
- 增强中文输出质量
- 恢复 Intuition Machine 技术简报风格
- 锁定默认样式，防止被 `/learn` 覆盖

### Fixed
- 图片文件扩展名处理
- 避免初始化时触发交互式提示

### Security
- 移除硬编码 API key，改用环境变量
- 添加 `.env` 支持

---

## [0.1.0] - 2025-01-15

### Added
- 初始版本：Concept Visualizer Agent - Polymathic Edition
- 核心 pipeline：analyze → map → design → generate
- 理论框架映射系统
- 多图表类型支持（pyramid、network、flowchart 等）
- Blueprint 技术蓝图风格
