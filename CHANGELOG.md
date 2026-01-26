# Changelog

All notable changes to the **ClamHelper** project will be documented in this file.

## [0.4.0] - 2026-01-25

### Added
- **Authentication System**:
    - 全局**密码保护**功能，通过环境变量 `APP_PASSWORD` 配置。
    - 独立且风格统一的**登录页面**，支持自动重定向。
- **Japanese Menu (PDF)**:
    - 配方本新增**“生成日式酒单”**功能。
    - 自动生成极简风格的 PDF 菜单（A4），支持多页。
    - 采用 **KaiTi (楷体)** 字体，支持 UTF-8 中文显示。
    - 智能文本换行逻辑，防止长配方超出页面宽度。
- **Ingredient Usage Stats**:
    - 活动统计页面新增**“原料消耗统计”**功能。
    - 自动计算每场活动中各基酒、利口酒和辅料的总消耗量。
- **Structured Recipe Data**:
    - 数据库新增 `RecipeIngredient` 表，支持结构化存储原料（名称、用量、单位）。
    - 配方编辑器升级，支持**动态添加/删除原料行**。
    - 引入 `<datalist>` 实现原料名称的自动补全（基于现有库存）。

### Changed
- **Frontend Refinement**:
    - 登录页面 UI 升级为与主站一致的日式风格。
    - 配方列表卡片现支持**多选**，用于批量生成 PDF 酒单。
    - 优化了统计页面的 CSS，修复了深色背景下的文字可见性问题。
- **AI Integration**:
    - 更新 AI Prompt，使其返回结构化的 JSON 原料数组（Name/Amount/Unit），无缝对接新数据库结构。
    - 修复了 AI 生成配方在前端渲染为 `[object Object]` 的显示 Bug。
- **Business Logic**:
    - 首页“今日战况”的统计逻辑更新为**“营业日”模式**（当日 04:00 至次日 04:00）。

### Fixed
- **Deployment**:
    - 修复了 PDF 生成时的字体依赖问题，现支持从项目根目录 `fonts/` 加载本地字体，确保服务器部署时的中文显示正常。
    - 修复了 `.env` 文件加载问题，引入 `python-dotenv` 自动读取环境变量。

---

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
