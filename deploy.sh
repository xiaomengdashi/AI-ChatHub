#!/bin/bash

# ChatHub AWS 部署脚本
# 使用方法: ./deploy.sh

set -e

echo "🚀 开始部署 ChatHub 到 AWS 服务器..."

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 更新系统
echo "📦 更新系统包..."
apt update && apt upgrade -y

# 安装必要的软件包
echo "📦 安装必要软件包..."
apt install -y nginx python3 python3-pip python3-venv nodejs npm git curl supervisor

# 创建应用目录
APP_DIR="/var/www/chathub"
echo "📁 创建应用目录: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# 如果是首次部署，克隆代码（假设代码已经上传到服务器）
if [ ! -d "$APP_DIR/.git" ]; then
    echo "📥 请确保代码已上传到 $APP_DIR"
    # git clone <your-repo-url> .
fi

# 设置后端
echo "🐍 设置 Python 后端..."
cd $APP_DIR/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt

# 初始化数据库（如果需要）
if [ ! -f "database/chathub.db" ]; then
    echo "🗄️ 初始化数据库..."
    python init_default_models.py
fi

# 设置前端
echo "🌐 设置前端..."
cd $APP_DIR/frontend

# 安装 Node.js 依赖
npm install

# 构建生产版本
npm run build

# 创建系统用户
echo "👤 创建系统用户..."
if ! id "chathub" &>/dev/null; then
    useradd -r -s /bin/false chathub
fi

# 设置文件权限
echo "🔐 设置文件权限..."
chown -R chathub:chathub $APP_DIR
chmod -R 755 $APP_DIR

echo "✅ 部署完成！"
echo "📝 请运行以下命令完成配置："
echo "1. sudo systemctl start nginx"
echo "2. sudo systemctl enable nginx"
echo "3. sudo systemctl start supervisor"
echo "4. sudo systemctl enable supervisor"