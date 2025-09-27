# DQ数据库质量巡检系统

一个基于Vue 3 + FastAPI的全栈数据库质量巡检系统。

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite (构建工具)
- Element Plus (UI组件库)
- Pinia (状态管理)
- Axios (HTTP客户端)

### 后端
- Python 3.11
- FastAPI (Web框架)
- SQLAlchemy (ORM)
- Pydantic (数据验证)
- PostgreSQL (数据库)
- Redis (缓存)

## 功能特性

### 项目管理
- 创建项目
- 删除项目

### 数据源管理
- 支持MySQL、ClickHouse、StarRocks等数据源
- 数据源连接测试
- SQL模式获取和提示

### 巡检任务管理
- 创建巡检任务
- 配置检查SQL和期望SQL（带SQL提示功能）
- 设置检查表达式（如：检查项==期望项）
- 支持Cron定时执行
- 任务执行历史记录
- 任务所属的项目

### 巡检执行检查
- 切换项目
- 最新执行的任务考前，如果任务失败，需要标红，如果成功标绿

### 首页
- 各个项目的执行情况 成功的数量 失败的数量 

## 快速开始

### 环境要求
- Docker
- Docker Compose
- Node.js 18+ (用于开发)

### 一键启动
```bash
# 启动服务
./start.sh
```
 

### 开发环境

#### 分别启动
```bash
# 前端开发
cd frontend
npm install
npm run dev

# 后端开发
cd backend
source venv/bin/activate  # 激活虚拟环境
python main.py
```

#### 一键启动开发环境
```bash
./dev-start.sh  # 同时启动前端和后端
```

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 项目结构

```
dq/
├── frontend/          # Vue 3前端项目
├── backend/           # Python后端项目
│   ├── app/
│   │   ├── api/       # API路由
│   │   ├── core/      # 核心配置
│   │   ├── models/    # 数据模型
│   │   ├── schemas/   # 数据验证
│   │   └── services/  # 业务逻辑
│   └── main.py        # FastAPI应用入口
├── Dockerfile         # Docker构建配置
├── docker-compose.yml # Docker编排配置
├── nginx.conf         # Nginx配置
└── start.sh           # 启动脚本
```

## 系统功能详解

### 1. 数据源注册
用户可以在系统中注册多种类型的数据源：
- MySQL数据库
- ClickHouse数据库  
- StarRocks数据库
- postgres数据库

每个数据源需要配置连接信息，系统会测试连接有效性并提供SQL模式信息用于提示。

### 2. 巡检任务配置
巡检任务包含以下核心字段：

**检验项**
- SQL代码，必须返回单个值、NULL或空行
- 支持SQL提示功能，基于数据源模式信息

**期望项**
- SQL代码，必须返回单个值、NULL或空行
- 同样支持SQL提示功能

**检查表达式**
- 用于对比检验项和期望项的结果
- 支持的操作符：==、!=、>、<、>=、<=
- 例如：检查项==期望项

**执行调度**
- 使用Cron表达式配置执行时间和频率
- 支持定时自动执行

**告警机制**
- 当检查表达式不成立时，任务标记为失败
- 系统会发送告警通知

### 3. 巡检执行检查
- 监控所有巡检任务的执行结果
- 成功的任务需要标绿
- 对失败任务进行告警，并且将执行的任务标红
- 记录告警历史和处理状态

## 配置说明

### 环境变量
主要配置文件位于 `backend/.env`，包含：
- 数据库连接配置
- Redis连接配置
- JWT密钥配置
- CORS配置

