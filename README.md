# 聚会调酒助手 (ClamHelper) 🍸

ClamHelper 是一个优雅的、基于 Web 的家庭聚会调酒辅助工具。它专为家庭调酒师设计，帮助您管理酒库、规划聚会酒单，并利用 AI 智能推荐鸡尾酒配方。

不仅如此，它还采用了典雅的**日式酒吧 (Bar Aesthetic)** 设计风格，为您的聚会增添一份独特的仪式感。

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)

## ✨ 核心功能

*   **🥂 饮酒记录 (Log Drink)**
    *   快速记录每位朋友喝了什么。
    *   实时追踪“今日战况”，了解聚会消耗。
*   **🍾 酒库管理 (Inventory)**
    *   精细化管理基酒（威士忌、金酒等）、利口酒及辅料。
    *   支持增删改查，清晰掌握库存状态。
*   **🎉 活动管理 (Events)**
    *   创建专属聚会活动（如“周五 Whisky 之夜”）。
    *   定制活动专属酒单，从配方库中挑选酒款。
    *   **📊 活动战报**：生成独立的统计页面，展示消耗总览、最受欢迎酒款及“酒神”排行榜。
*   **🤖 AI 调酒助手 (AI Bartender)**
    *   集成 **阿里云百炼 (DashScope/Qwen)** 大模型。
    *   **Omakase 模式**：根据您的心情和天气，AI 酒吧老板 "Kenji" 为您特调一杯并附带治愈寄语。
    *   **精准推荐**：根据现有库存智能推荐鸡尾酒配方。
    *   **结构化保存**：AI 生成的配方可自动解析并填入表单，一键保存到配方本。
*   **📜 配方本 (Recipes)**
    *   管理您的经典配方或 AI 创意配方。
    *   支持手动创建、编辑和删除配方。
    *   **PDF 酒单生成**：支持多选配方，一键生成优雅的**日式风格 PDF 酒单**（支持中文、自动分页与排版）。
*   **🔐 安全保护**
    *   支持简单的密码访问控制，保护您的私有酒单和数据。
*   **👥 朋友管理**
    *   管理常来聚会的朋友名单。
*   **📸 分享卡片**
    *   一键生成日式风格的**“今夜酒单”**图片。
    *   包含活动统计、MVP 酒神榜单以及 AI 生成的活动总结。

## 🛠️ 技术栈

*   **后端**: Python, Flask, SQLAlchemy (SQLite)
*   **前端**: HTML5, Bootstrap 5, Jinja2, Chart.js
*   **AI**: 阿里云百炼 (DashScope) / OpenAI 兼容接口
*   **部署**: Gunicorn (生产环境支持)

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd ClamHelper
```

### 2. 环境配置
建议使用 Python 虚拟环境：
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

安装依赖：
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制示例配置文件并重命名为 `.env`：
```bash
cp .env.example .env
```
编辑 `.env` 文件，填入您的 API Key（推荐使用阿里云百炼）：
```ini
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
APP_PASSWORD=your_secret_password  # 可选：设置访问密码
```

### 4. 运行应用
**开发模式：**
```bash
python app.py
```
访问：`http://127.0.0.1:5000`

**生产环境 (Linux/Mac)：**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📂 项目结构

```
ClamHelper/
├── app.py                  # Flask 应用入口与路由逻辑
├── models.py               # 数据库模型定义
├── services/
│   └── llm_service.py      # AI 服务接口封装
├── static/
│   └── css/
│       └── style.css       # 日式酒吧风格样式表
├── templates/
│   ├── index.html          # 主界面 (SPA 风格 Tab页)
│   └── event_stats.html    # 活动统计独立页面
├── instance/
│   └── bar.db              # SQLite 数据库 (自动生成)
├── requirements.txt        # 项目依赖
└── .env.example            # 环境变量示例
```

## 🎨 设计理念

项目前端采用了**日式调酒酒吧**的视觉风格：
*   **配色**：深炭色木纹背景搭配米白纸质卡片，点缀哑光金。
*   **排版**：使用衬线字体 (Noto Serif SC)，体现菜单的精致感。
*   **交互**：平滑的淡入淡出动画与智能的锚点定位，确保操作流畅不迷路。

## 📝 License

MIT License
