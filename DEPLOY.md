# 智能服装穿搭助手 - 云端部署指南

## 概述

本项目采用前后端分离架构：

- **前端**: Streamlit Cloud (免费)
- **后端**: Railway (FastAPI)
- **数据库**: Railway MySQL
- **AI**: DashScope 通义千问 API

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│  Streamlit Cloud (免费)                                    │
│  └── frontend/app.py                                      │
│         │                                                  │
│         └──────── HTTP 请求 ────────┐                     │
└──────────────────────────────────│─────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Railway (FastAPI 后端)                                    │
│  └── backend/main.py                                       │
│         │                                                  │
│         └─ Railway MySQL (结构化数据)                      │
│         └─ DashScope API (AI 推荐)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 一、云服务申请

### 1. 必须申请的服务

| 服务 | 申请地址 | 说明 |
|------|----------|------|
| GitHub | https://github.com | 代码仓库 |
| Railway | https://railway.app | 后端 + MySQL |
| DashScope | https://dashscope.console.aliyun.com | 通义千问 API |

### 1.2 Railway MySQL 创建

1. 登录 Railway
2. New Project → Add MySQL
3. 创建后，在 Variables 中查看连接信息

---

## 二、GitHub 仓库创建

### 2.1 创建新仓库

1. 访问 https://github.com/new
2. 填写仓库名称: `fashion-assistant`
3. 选择 Private (私有)
4. 点击 Create repository

### 2.2 推送代码

```bash
cd 智能服装穿搭

git init
git add .
git commit -m "Initial commit"

git remote add origin https://github.com/USERNAME/fashion-assistant.git
git branch -M main
git push -u origin main
```

---

## 三、Railway 后端部署

### 3.1 创建 Railway 项目

1. 登录 https://railway.app
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择刚才创建的仓库
4. **重要**: 在 Deployment Settings 中设置 Root Directory 为 `backend`

### 3.2 配置环境变量

在 Railway 项目 Settings → Variables 中添加：

```env
# MySQL (Railway MySQL 连接信息)
MYSQL_HOST=containers-us-west-XX.railway.internal
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=railway

# DashScope (阿里云控制台获取)
DASHSCOPE_API_KEY=sk-xxxxxxxx

# 关闭 SQLite，使用 MySQL
USE_SQLITE=false
```

### 3.3 获取后端 URL

部署成功后，在项目 Domains 中查看：
```
https://fashion-backend-xxxx.up.railway.app
```

---

## 四、Streamlit Cloud 前端部署

### 4.1 连接 GitHub

1. 访问 https://share.streamlit.io
2. 点击 "New app"
3. 选择 GitHub 仓库和分支
4. Main file path: `frontend/app.py`

### 4.2 配置 Secrets

在 Advanced Settings → Secrets 中添加：

```toml
API_BASE_URL = "https://fashion-backend-xxxx.up.railway.app"
```

### 4.3 部署

点击 "Deploy!"

---

## 五、数据导入

### 5.1 方式一：通过 Railway 终端

1. Railway → Deployments → 最新部署
2. 点击终端图标
3. 运行导入脚本：

```bash
cd /app
python backend/import_data.py
```

### 5.2 方式二：本地导入

```bash
# 配置 .env 连接 Railway MySQL
python backend/import_data.py
```

---

## 六、验证部署

### 6.1 后端健康检查

访问: `https://fashion-backend-xxxx.up.railway.app/health`

预期返回:
```json
{"status": "healthy"}
```

### 6.2 前端访问

访问: `https://share.streamlit.io/USERNAME/fashion-assistant`

### 6.3 测试清单

| 功能 | 测试方法 | 预期结果 |
|------|----------|----------|
| 用户注册 | 注册新用户 | 成功注册 |
| AI 对话 | 发送 "推荐一套商务穿搭" | 返回搭配推荐 |
| 商品搜索 | 搜索 "蓝色衬衫" | 返回商品列表 |
| 衣橱收藏 | 收藏推荐搭配 | 收藏成功保存 |

---

## 七、成本说明

| 服务 | 方案 | 月费用 |
|------|------|--------|
| Railway | Starter | $5 |
| DashScope | 按量 | ~$20-50 |
| **总计** | | **~$25-55/月** |

---

## 八、故障排除

### 8.1 后端无法启动

检查 Railway 日志，常见问题：
- 环境变量未配置
- 依赖安装失败
- 端口配置错误

### 8.2 前端连接失败

1. 确认后端已启动
2. 检查 Streamlit Secrets 中的 API_BASE_URL
3. 查看浏览器开发者工具的网络请求

### 8.3 数据库连接失败

1. 确认 Railway MySQL 已创建
2. 检查环境变量中的连接信息
3. 确认数据库名称正确

---

## 九、更新部署

### 9.1 更新后端

```bash
git add .
git commit -m "Update backend"
git push origin main
```

Railway 会自动检测并重新部署。

### 9.2 更新前端

```bash
git add .
git commit -m "Update frontend"
git push origin main
```

Streamlit Cloud 会自动重新部署。
