#!/bin/bash

echo "DQ管理系统本地启动脚本"
echo "=================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3未安装，请先安装Python3"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: Node.js未安装，请先安装Node.js"
    exit 1
fi

# 根据参数启动服务
if [ "$1" = "backend" ]; then
    echo "正在启动后端服务..."
    cd backend
    
    # 检查虚拟环境是否存在
    if [ ! -d "venv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    echo "安装后端依赖..."
    pip install -r requirements.txt
    
    # 启动后端
    echo "启动后端服务..."
    python main.py &
    BACKEND_PID=$!
    
    echo "后端服务已启动 (PID: $BACKEND_PID)"
    echo "后端API: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    echo "停止服务: kill $BACKEND_PID"
    
elif [ "$1" = "frontend" ]; then
    echo "正在启动前端服务..."
    cd frontend
    
    # 检查是否已安装依赖
    if [ ! -d "node_modules" ]; then
        echo "安装前端依赖..."
        npm install
    fi
    
    # 启动前端
    echo "启动前端服务..."
    npm run dev &
    FRONTEND_PID=$!
    
    echo "前端服务已启动 (PID: $FRONTEND_PID)"
    echo "前端地址: http://localhost:5173"
    echo "停止服务: kill $FRONTEND_PID"
    
else
    echo "正在启动所有服务..."
    
    echo "正在启动后端服务..."
    cd backend
    
    # 检查虚拟环境是否存在
    if [ ! -d "venv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    echo "安装后端依赖..." 
    pip install -r requirements.txt
    
    # 启动后端
    python main.py &
    BACKEND_PID=$!
    
    echo "后端服务已启动 (PID: $BACKEND_PID)"
    echo "等待后端服务启动..."
    sleep 5
    
    echo "正在启动前端服务..."
    cd ../frontend
    
    # 检查是否已安装依赖
    if [ ! -d "node_modules" ]; then
        echo "安装前端依赖..."
        npm install
    fi
    
    # 启动前端
    npm run dev &
    FRONTEND_PID=$!
    
    echo "前端服务已启动 (PID: $FRONTEND_PID)"
    
    echo ""
    echo "服务已启动！"
    echo "前端地址: http://localhost:5173"
    echo "后端API: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    echo ""
    echo "停止服务: kill $BACKEND_PID $FRONTEND_PID"
    echo "或使用: pkill -f 'python simple_main.py' && pkill -f 'npm run dev'"
fi