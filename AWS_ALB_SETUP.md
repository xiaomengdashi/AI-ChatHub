# AWS Application Load Balancer + SSL 证书配置指南

本指南将帮助你在 AWS 上设置 Application Load Balancer (ALB) 和 SSL 证书，为 ChatHub 项目提供 HTTPS 支持。

## 🎯 架构概览

```
Internet → ALB (SSL 终止) → Target Group → EC2 (Nginx:80)
```

- **ALB**: 处理 SSL 终止和负载均衡
- **SSL 证书**: AWS Certificate Manager (ACM) 提供
- **EC2**: 运行 Nginx (仅 HTTP 80 端口)

## 📋 前置要求

- AWS 账户
- 域名 `ai.kolane.top` 已在 Route 53 或其他 DNS 提供商配置
- EC2 实例已部署 ChatHub 应用

## 🚀 配置步骤

### 1. 申请 SSL 证书 (ACM)

#### 1.1 进入 AWS Certificate Manager
- 登录 AWS 控制台
- 搜索并进入 "Certificate Manager"
- 选择与你的 EC2 相同的区域

#### 1.2 申请证书
```
1. 点击 "Request a certificate"
2. 选择 "Request a public certificate"
3. 域名配置:
   - Domain name: ai.kolane.top
   - 可选: *.kolane.top (通配符证书)
4. 验证方法: 选择 "DNS validation"
5. 点击 "Request"
```

#### 1.3 DNS 验证
```
1. 在证书详情页面，找到 DNS 验证记录
2. 复制 CNAME 记录的名称和值
3. 在你的 DNS 提供商处添加这些 CNAME 记录
4. 等待验证完成 (通常 5-30 分钟)
```

### 2. 创建 Target Group

#### 2.1 进入 EC2 控制台
- 在左侧菜单选择 "Target Groups"
- 点击 "Create target group"

#### 2.2 配置 Target Group
```
Basic configuration:
- Target type: Instances
- Target group name: chathub-targets
- Protocol: HTTP
- Port: 80
- VPC: 选择你的 EC2 所在的 VPC

Health checks:
- Health check protocol: HTTP
- Health check path: /health
- Health check port: 80
- Healthy threshold: 2
- Unhealthy threshold: 2
- Timeout: 5 seconds
- Interval: 30 seconds
- Success codes: 200
```

#### 2.3 注册目标
```
1. 点击 "Next"
2. 选择你的 EC2 实例
3. Port: 80
4. 点击 "Include as pending below"
5. 点击 "Create target group"
```

### 3. 创建 Application Load Balancer

#### 3.1 创建 ALB
- 在 EC2 控制台，选择 "Load Balancers"
- 点击 "Create Load Balancer"
- 选择 "Application Load Balancer"

#### 3.2 基本配置
```
Basic configuration:
- Load balancer name: chathub-alb
- Scheme: Internet-facing
- IP address type: IPv4

Network mapping:
- VPC: 选择你的 EC2 所在的 VPC
- Mappings: 选择至少 2 个可用区的公有子网
```

#### 3.3 安全组配置
```
Security groups:
- 创建新安全组或选择现有安全组
- 入站规则:
  - HTTP (80): 0.0.0.0/0
  - HTTPS (443): 0.0.0.0/0
```

#### 3.4 监听器配置
```
Listeners:
1. HTTP:80 监听器:
   - Protocol: HTTP
   - Port: 80
   - Default action: Redirect to HTTPS

2. HTTPS:443 监听器:
   - Protocol: HTTPS
   - Port: 443
   - Default action: Forward to target group
   - Target group: chathub-targets
   - SSL certificate: 选择之前创建的 ACM 证书
```

### 4. 配置 Route 53 (如果使用)

#### 4.1 创建 A 记录
```
Record name: ai
Record type: A
Alias: Yes
Route traffic to: Application Load Balancer
Region: 选择 ALB 所在区域
Load balancer: 选择 chathub-alb
```

### 5. 更新 EC2 安全组

#### 5.1 修改 EC2 安全组
```
入站规则:
- HTTP (80): 来源设置为 ALB 的安全组 ID
- SSH (22): 你的 IP 地址
- 移除直接的 HTTPS (443) 规则
```

## 🔧 验证配置

### 1. 检查健康状态
```
1. 进入 Target Groups
2. 选择 chathub-targets
3. 查看 Targets 标签页
4. 确保状态为 "healthy"
```

### 2. 测试访问
```
1. 获取 ALB 的 DNS 名称
2. 在浏览器中访问: http://[ALB-DNS-NAME]
3. 应该自动重定向到 HTTPS
4. 访问: https://ai.kolane.top
```

## 📊 监控和日志

### 1. CloudWatch 指标
- ALB 请求数量
- 目标健康状态
- 响应时间

### 2. 访问日志 (可选)
```
1. 在 ALB 详情页面
2. 选择 "Attributes" 标签页
3. 启用 "Access logs"
4. 指定 S3 存储桶
```

## 🔍 故障排除

### 常见问题

1. **502 Bad Gateway**
   - 检查 Target Group 健康状态
   - 确认 EC2 安全组允许来自 ALB 的流量
   - 检查 Nginx 是否在端口 80 运行

2. **SSL 证书问题**
   - 确认证书状态为 "Issued"
   - 检查域名是否正确配置
   - 验证 DNS 记录

3. **健康检查失败**
   - 确认 `/health` 端点可访问
   - 检查 EC2 实例状态
   - 查看 Nginx 日志

### 有用的命令

```bash
# 检查 Nginx 状态
sudo systemctl status nginx

# 检查端口监听
sudo netstat -tlnp | grep :80

# 测试健康检查端点
curl http://localhost/health

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/chathub_access.log
```

## 💰 成本优化

1. **使用单个 AZ** (开发环境)
2. **选择合适的实例类型**
3. **启用 ALB 访问日志** (仅在需要时)
4. **定期检查 CloudWatch 指标**

## 🔐 安全最佳实践

1. **最小权限原则**: 安全组只开放必要端口
2. **定期更新**: 保持 EC2 实例和应用更新
3. **监控访问**: 启用 CloudTrail 和访问日志
4. **备份策略**: 定期备份数据和配置

---

**注意**: 
- ALB 按小时和处理的请求数量收费
- ACM 证书是免费的
- 确保在同一区域创建所有资源