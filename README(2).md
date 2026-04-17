# 私人服装穿搭助手

基于 AI Agent 的智能服装搭配推荐系统。

## 项目结构

```
├── backend/                 # FastAPI 后端
│   ├── main.py             # 主入口
│   ├── config.py           # 配置文件
│   ├── agent/              # AI Agent (LangGraph)
│   │   ├── agent.py        # Agent 主逻辑
│   │   ├── intent_classifier.py  # 意图识别
│   │   ├── skills/         # 技能模块
│   │   └── tools/          # 工具模块
│   ├── models/             # 数据模型
│   ├── services/            # 业务服务
│   ├── routers/             # API 路由
│   └── import_data.py      # 数据导入脚本
│
├── frontend/                # Streamlit 前端
│   └── app.py              # 主应用
│
├── requirements.txt         # 依赖
├── .env.example            # 环境变量示例
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填写数据库配置
```

### 3. 初始化数据库

确保 MySQL 服务运行中，然后运行导入脚本：

```bash
python backend/import_data.py
```

### 4. 启动后端服务

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 启动前端

在另一个终端运行：

```bash
streamlit run frontend/app.py
```

## 功能特性

- 💬 **AI 对话**: 自然语言交互，智能理解用户需求
- 🔍 **商品搜索**: 多维度筛选，快速找到心仪商品
- 👔 **搭配推荐**: AI 智能推荐完整穿搭方案
- 👔 **虚拟衣橱**: 收藏和管理心仪搭配
- 🖼️ **虚拟试穿**: 生成试穿效果图 (开发中)

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/` | POST | AI 对话 |
| `/api/search/` | POST | 商品搜索 |
| `/api/products/{id}` | GET | 获取商品详情 |
| `/api/wardrobe/save-outfit` | POST | 保存搭配到衣橱 |
| `/api/wardrobe/list/{user_id}` | GET | 获取用户衣橱 |
| `/api/users/{id}` | GET | 获取用户信息 |

## 技术栈

- **后端**: FastAPI, LangGraph, SQLAlchemy
- **前端**: Streamlit
- **数据库**: MySQL
- **AI**: 通义千问 (阿里云 DashScope)
