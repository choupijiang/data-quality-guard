#!/bin/bash

echo "DQ管理系统停止脚本"
echo "=================="

# 停止后端服务
echo "正在停止后端服务..."
pkill -f "python3 main.py" || true

# 停止前端服务
echo "正在停止前端服务..."
pkill -f "npm run dev" || true
pkill -f "vite" || true

# 等待进程完全停止
sleep 2

echo "服务已停止！"