# ChatHub AWS 部署指南

本指南将帮助你在 Amazon Web Services (AWS) 上部署 ChatHub 项目，包括 Nginx 反向代理配置。

## 📋 前置要求

- AWS EC2 实例 (推荐 t3.medium 或更高配置)
- Ubuntu 20.04 LTS 或更新版本
- 域名 (可选，用于 SSL 证书)
- 基本的 Linux 命令行知识

## 🚀 快速部署

### 1. 准备 EC2 实例

```bash
# 连接到你的 EC2 实例
ssh -i your-key.pem ubuntu@your-ec2-ip

# 更新系统
sudo apt update && sudo apt upgrade -y
```

### 2. 上传项目文件

```bash
# 方法1: 使用 SCP 上传
scp -i your-key.pem -r /path/to/chathub ubuntu@your-ec2-ip:/home/ubuntu/

# 方法2: 使用 Git 克隆
git clone https://github.com/your-username/chathub.git
```

### 3. 运行部署脚本

```bash
# 进入项目目录
cd chathub

# 给脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
sudo ./deploy.sh
```

### 4. 配置 Nginx

```bash
# 复制 Nginx 配置
sudo cp nginx.conf /etc/nginx/sites-available/chathub

# 创建软链接
sudo ln -s /etc/nginx/sites-available/chathub /etc/nginx/sites-enabled/

# 删除默认配置
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 5. 配置 Supervisor

```bash
# 复制 Supervisor 配置
sudo cp chathub.conf /etc/supervisor/conf.d/

# 创建日志目录
sudo mkdir -p /var/log/chathub
sudo chown chathub:chathub /var/log/chathub

# 重新加载 Supervisor 配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动应用
sudo supervisorctl start chathub:*
```

### 6. 配置环境变量

```bash
# 复制生产环境配置
cp .env.production /var/www/chathub/backend/.env

# 编辑配置文件，添加你的 API 密钥
sudo nano /var/www/chathub/backend/.env
```

### 7. 快速部署 (推荐)

使用专为 ai.kolane.top 定制的部署脚本：

```bash
# 给脚本执行权限
chmod +x deploy-kolane.sh

# 运行快速部署
sudo ./deploy-kolane.sh
```

### 8. 设置 AWS Application Load Balancer + SSL

使用 AWS 自带的 SSL 证书和负载均衡器：

```bash
# 查看详细的 ALB 配置指南
cat AWS_ALB_SETUP.md
```

**主要步骤：**
1. 在 AWS Certificate Manager 申请 SSL 证书
2. 创建 Target Group (指向 EC2:80)
3. 创建 Application Load Balancer
4. 配置 HTTPS 监听器使用 ACM 证书
5. 更新 Route 53 A 记录指向 ALB

## 🔧 详细配置

### EC2 安全组配置

确保你的 EC2 安全组允许以下端口：

- **HTTP (80)**: 0.0.0.0/0
- **HTTPS (443)**: 0.0.0.0/0
- **SSH (22)**: 你的 IP 地址

### DNS 配置

**使用 ALB 时的 DNS 配置：**

在你的域名管理面板中，添加 CNAME 记录：

```
类型: CNAME
名称: ai
值: [ALB的DNS名称，如: chathub-alb-123456789.us-east-1.elb.amazonaws.com]
TTL: 300 (或默认值)
```

**或者使用 Route 53 (推荐)：**

```
类型: A
名称: ai
别名: 是
路由流量到: Application Load Balancer
区域: [选择ALB所在区域]
负载均衡器: chathub-alb
```

### 环境变量配置

编辑 `/var/www/chathub/backend/.env` 文件：

```bash
# 必须修改的配置
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# CORS 配置 (已配置为 ai.kolane.top)
CORS_ORIGINS=https://ai.kolane.top
```

### 防火墙配置

```bash
# 启用 UFW 防火墙
sudo ufw enable

# 允许必要端口
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# 检查状态
sudo ufw status
```

## 📊 监控和维护

### 查看应用状态

```bash
# 查看 Supervisor 状态
sudo supervisorctl status

# 查看应用日志
sudo tail -f /var/log/chathub/backend.log

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/chathub_access.log
sudo tail -f /var/log/nginx/chathub_error.log
```

### 重启服务

```bash
# 重启后端应用
sudo supervisorctl restart chathub:*

# 重启 Nginx
sudo systemctl restart nginx

# 重新加载 Nginx 配置
sudo nginx -s reload
```

### 更新应用

```bash
# 进入项目目录
cd /var/www/chathub

# 拉取最新代码
git pull origin main

# 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 重新构建前端
cd ../frontend
npm install
npm run build

# 重启应用
sudo supervisorctl restart chathub:*
```

## 🔍 故障排除

### 常见问题

1. **502 Bad Gateway**
   - 检查后端应用是否运行：`sudo supervisorctl status`
   - 查看后端日志：`sudo tail -f /var/log/chathub/backend.log`

2. **静态文件无法加载**
   - 检查文件权限：`ls -la /var/www/chathub/frontend/dist/`
   - 确保 Nginx 有读取权限

3. **API 请求失败**
   - 检查 Nginx 配置：`sudo nginx -t`
   - 查看 Nginx 错误日志：`sudo tail -f /var/log/nginx/chathub_error.log`

### 性能优化

1. **启用 Gzip 压缩** (已在 nginx.conf 中配置)
2. **设置静态文件缓存** (已在 nginx.conf 中配置)
3. **使用 CDN** (可选)
4. **数据库优化** (如果使用 PostgreSQL/MySQL)

## 📈 扩展部署

### 使用 Docker (可选)

如果你更喜欢使用 Docker：

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps
```

### 负载均衡 (高流量场景)

对于高流量场景，可以考虑：

1. 使用 AWS Application Load Balancer
2. 部署多个 EC2 实例
3. 使用 AWS RDS 作为数据库
4. 使用 AWS ElastiCache 作为缓存

## 🔐 安全建议

1. **定期更新系统和依赖包**
2. **使用强密码和密钥**
3. **启用防火墙**
4. **定期备份数据库**
5. **监控访问日志**
6. **使用 HTTPS**

## 📞 支持

如果遇到问题，请检查：

1. 应用日志：`/var/log/chathub/backend.log`
2. Nginx 日志：`/var/log/nginx/chathub_*.log`
3. 系统日志：`sudo journalctl -u nginx -f`

---

**注意**: 请确保在生产环境中修改所有默认密钥和配置！