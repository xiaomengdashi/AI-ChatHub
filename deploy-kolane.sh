#!/bin/bash

# ChatHub 快速部署脚本 - ai.kolane.top
# 专为 ai.kolane.top 域名定制

set -e

echo "🚀 开始部署 ChatHub 到 ai.kolane.top..."

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 域名配置
DOMAIN="ai.kolane.top"
EMAIL="admin@kolane.top"

echo "🌐 配置域名: $DOMAIN"

# 运行基础部署
echo "📦 运行基础部署..."
./deploy.sh

# 配置 Nginx
echo "🔧 配置 Nginx..."
cp nginx.conf /etc/nginx/sites-available/chathub
ln -sf /etc/nginx/sites-available/chathub /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 配置 Supervisor
echo "👥 配置 Supervisor..."
cp chathub.conf /etc/supervisor/conf.d/
mkdir -p /var/log/chathub
chown chathub:chathub /var/log/chathub

# 配置环境变量
echo "⚙️ 配置环境变量..."
cp .env.production /var/www/chathub/backend/.env

# 测试 Nginx 配置
echo "🧪 测试 Nginx 配置..."
nginx -t

# 重新加载服务
echo "🔄 重新加载服务..."
supervisorctl reread
supervisorctl update
supervisorctl start chathub:*

# 启动 Nginx
systemctl restart nginx
systemctl enable nginx

echo "✅ 基础部署完成！"
echo ""
echo "📋 接下来的步骤："
echo "1. 在 AWS 控制台设置 Application Load Balancer"
echo "2. 申请 ACM SSL 证书"
echo "3. 配置 Target Group 指向此 EC2 实例 (端口 80)"
echo "4. 编辑环境变量: sudo nano /var/www/chathub/backend/.env"
echo "5. 添加你的 API 密钥 (OpenAI, Anthropic, Google 等)"
echo ""
echo "📖 详细 ALB 配置指南: 查看 AWS_ALB_SETUP.md"
echo "🌐 临时访问地址: http://$(curl -s ifconfig.me)"
echo "🔐 ALB 配置后访问: https://$DOMAIN"