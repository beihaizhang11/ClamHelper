# Changelog

All notable changes to the **ClamHelper** project will be documented in this file.

## [Unreleased]

### Added
- **Omakase Mode**: 新增 AI 调酒师 "Kenji" 的厨师发办模式，根据心情和天气推荐特调。
- **Share Card**: 活动统计页面新增“生成酒单卡片”功能，支持一键生成并下载包含 AI 总结的日式战报图片。
- **Structured AI Response**: AI 服务升级为返回严格 JSON 格式，支持前端自动填充配方名称、原料和步骤，优化保存体验。
- **UI Visual Overhaul**: 全面升级为“日式调酒酒吧”风格。
    - 引入 `style.css`，采用深色木纹背景、米白纸质卡片和哑光金配色。
    - 字体更新为衬线体 (Noto Serif SC)。
    - 添加了 Tab 切换动画和按钮微交互。
- **UX Optimization**: 
    - 实现了 POST 请求后的**智能锚点定位**，提交表单后自动保持在当前标签页，不再强制跳回首页顶部。
- **Deployment Support**: 
    - 更新 `requirements.txt`，锁定依赖版本。
    - 添加 `gunicorn` 支持，便于生产环境部署。

### Changed
- **AI Service Provider**: 
    - 迁移至 **阿里云百炼 (DashScope)**，使用 `qwen-plus` 模型以获得更好的中文体验和性价比。
    - 更新 `llm_service.py` 逻辑以优先读取 `DASHSCOPE_API_KEY`。

---

## [0.3.0] - 2026-01-21

### Added
- **Event Statistics**: 
    - 新增独立统计页面 `/event/<id>/stats`。
    - 可视化展示活动消耗（Chart.js 甜甜圈图）。
    - 详细的“酒神排行榜”和饮酒明细。
- **Inventory Management**: 
    - 新增库存条目的**编辑**和**删除**功能。
    - 优化了库存分类显示（支持基酒细分）。

### Fixed
- **Database Schema**: 修复了 `consumption` 表缺少 `event_id` 导致的数据库错误，添加了自动迁移脚本。

---

## [0.2.0] - 2026-01-21

### Added
- **Recipe Management**:
    - 支持**手动创建**配方。
    - 支持现有配方的**编辑**和**删除**。
- **Event System**:
    - 新增 `Event` (活动) 实体。
    - 支持创建活动、为活动添加/移除专属酒单。
    - 饮酒记录 (`Consumption`) 现可关联具体活动。

### Changed
- **Database Models**: 重构了数据库模型，引入 `Event` 表及多对多关系 (`event_recipe`)。

---

## [0.1.0] - 2026-01-21

### Initial Release
- **Core Features**:
    - 基础 Web 框架搭建 (Flask + Bootstrap)。
    - 饮酒记录功能 (Log Drink)。
    - 基础库存管理 (Inventory)。
    - 参与者管理 (Participants)。
    - AI 调酒助手 (基于 OpenAI GPT-3.5)，支持根据库存推荐配方。
