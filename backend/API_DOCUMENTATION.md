# ChatHub RESTful API 文档

ChatHub 后端现在提供纯粹的 RESTful API 服务，不包含前端页面。

## 基础信息

- **基础URL**: `http://127.0.0.1:5001`
- **认证方式**: Bearer Token (在请求头中添加 `Authorization: Bearer <token>`)
- **测试Token**: `demo-token` (用于开发测试)
- **数据库**: SQLite数据库文件位于 `backend/database/chathub.db`

## 项目结构

```
chathub/
├── backend/           # 后端API服务
│   ├── app.py        # Flask应用入口
│   ├── models/       # 数据模型
│   ├── routes/       # API路由
│   ├── utils/        # 工具函数
│   └── database/     # 数据库目录
│       └── chathub.db # SQLite数据库文件
└── frontend/         # 前端Vue应用
    ├── src/
    └── dist/
```

## API 端点

### 1. 健康检查

**GET** `/api/health`

检查API服务状态

**响应示例**:
```json
{
  "status": "healthy",
  "message": "AI API服务运行正常"
}
```

### 2. 模型管理

#### 获取模型列表
**GET** `/api/models`

获取所有可用的AI模型，支持查询参数过滤。

**查询参数**:
- `active_only`: 仅获取激活的模型 (true/false)
- `provider`: 按提供商过滤
- `type`: 按模型类型过滤

**响应示例**:
```json
[
  {
    "id": 1,
    "model_name": "Qwen/QwQ-32B-Instruct",
    "display_name": "QwQ-32B",
    "model_provider": "siliconflow",
    "model_type": "chat",
    "max_tokens": 32768,
    "supports_streaming": true,
    "supports_function_calling": false,
    "supports_vision": false,
    "input_price_per_1k": 0.5,
    "output_price_per_1k": 1.5,
    "description": "通义千问推理模型",
    "is_active": true,
    "sort_order": 0,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
]
```

#### 创建模型
**POST** `/api/models`

需要管理员权限。创建新的模型配置。

**请求体**:
```json
{
  "model_name": "gpt-4o",
  "display_name": "GPT-4o",
  "model_provider": "openai",
  "model_type": "chat",
  "max_tokens": 4096,
  "supports_streaming": true,
  "supports_function_calling": true,
  "supports_vision": true,
  "input_price_per_1k": 5.0,
  "output_price_per_1k": 15.0,
  "description": "OpenAI最新的多模态模型",
  "is_active": true,
  "sort_order": 0
}
```

#### 更新模型
**PUT** `/api/models/{model_id}`

需要管理员权限。更新指定模型的配置。

#### 删除模型
**DELETE** `/api/models/{model_id}`

需要管理员权限。删除指定模型。

#### 切换模型状态
**POST** `/api/models/{model_id}/toggle`

需要管理员权限。切换模型的启用/禁用状态。

#### 批量更新模型排序
**POST** `/api/models/batch-update-order`

需要管理员权限。批量更新模型的排序顺序。

### 3. 提供商管理

#### 获取提供商列表
**GET** `/api/providers`

需要认证。获取所有启用的AI模型提供商列表。

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "provider_key": "openai",
      "display_name": "OpenAI",
      "default_base_url": "https://api.openai.com/v1",
      "is_active": true,
      "sort_order": 0,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### 创建提供商
**POST** `/api/providers`

需要管理员权限。创建新的模型提供商。

**请求体**:
```json
{
  "provider_key": "custom_provider",
  "display_name": "自定义提供商",
  "default_base_url": "https://api.custom.com/v1",
  "is_active": true,
  "sort_order": 0
}
```

#### 更新提供商
**PUT** `/api/providers/{provider_id}`

需要管理员权限。更新指定提供商的信息。

#### 删除提供商
**DELETE** `/api/providers/{provider_id}`

需要管理员权限。删除指定提供商（软删除，设置为不活跃状态）。

#### 获取单个提供商
**GET** `/api/providers/{provider_id}`

需要认证。获取指定提供商的详细信息。

### 4. 用户认证

#### 登录
**POST** `/api/auth/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例**:
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@chathub.com",
    "subscription_type": "premium",
    "role": "admin"
  },
  "message": "登录成功"
}
```

#### 用户注册
**POST** `/api/auth/register`

普通用户注册。

**请求体**:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123"
}
```

#### 管理员注册用户
**POST** `/api/auth/admin/register`

需要管理员权限。管理员为其他用户注册账户。

#### 验证Token
**GET** `/api/auth/verify`

需要认证。验证当前token的有效性。

#### 登出
**POST** `/api/auth/logout`

需要认证。用户登出。

### 5. 聊天功能

#### 发送消息
**POST** `/api/chat`

需要认证。发送消息给AI模型。

**请求体**:
```json
{
  "message": "你好，请介绍一下自己",
  "model": "Qwen/Qwen2.5-72B-Instruct",
  "conversation_id": "可选，不提供则自动生成",
  "user_id": 1
}
```

**响应示例**:
```json
{
  "conversation_id": "uuid-string",
  "response": "AI的回复内容",
  "model": "Qwen/Qwen2.5-72B-Instruct",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 流式聊天
**POST** `/api/chat/stream`

需要认证。支持Server-Sent Events的流式聊天。

**请求体**: 同上

**响应**: SSE流，每个事件包含：
```json
{
  "type": "content",
  "content": "部分回复内容"
}
```

### 6. 对话管理

#### 获取对话列表
**GET** `/api/conversations`

需要认证。获取用户的所有对话。

#### 获取对话消息
**GET** `/api/conversations/{conversation_id}/messages`

需要认证。获取特定对话的所有消息。

#### 更新对话
**PUT** `/api/conversations/{conversation_id}`

需要认证。更新对话信息（如重命名标题）。

**请求体**:
```json
{
  "title": "新的对话标题"
}
```

#### 删除对话
**DELETE** `/api/conversations/{conversation_id}`

需要认证。删除指定对话。

### 7. API密钥管理

#### 保存API密钥
**POST** `/api/apikeys`

需要认证。保存第三方API密钥。

**请求体**:
```json
{
  "model_provider": "siliconflow",
  "api_key": "your-api-key",
  "base_url": "https://api.siliconflow.cn/v1/chat/completions"
}
```

#### 获取API密钥列表
**GET** `/api/apikeys`

需要认证。获取已保存的API密钥列表（密钥会被部分隐藏）。

#### 更新API密钥
**PUT** `/api/apikeys/{key_id}`

需要认证。更新指定的API密钥。

#### 删除API密钥
**DELETE** `/api/apikeys/{key_id}`

需要认证。删除指定的API密钥。

#### 切换API密钥状态
**POST** `/api/apikeys/{key_id}/toggle`

需要认证。切换API密钥的启用/禁用状态。

### 8. 统计信息

**GET** `/api/stats`

需要认证。获取用户的使用统计信息。

### 9. 用户管理

#### 获取用户列表
**GET** `/api/users`

需要管理员权限。获取所有用户列表，支持分页和搜索。

**查询参数**:
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 10)
- `search`: 搜索关键词（用户名或邮箱）
- `role`: 按角色过滤

#### 获取单个用户
**GET** `/api/users/{user_id}`

需要管理员权限。获取指定用户的详细信息。

#### 更新用户信息
**PUT** `/api/users/{user_id}`

需要管理员权限。更新指定用户的信息。

#### 删除用户
**DELETE** `/api/users/{user_id}`

需要管理员权限。禁用指定用户（软删除）。

#### 重置用户密码
**POST** `/api/users/{user_id}/reset-password`

需要管理员权限。重置指定用户的密码。

#### 获取个人信息
**GET** `/api/users/profile`

需要认证。获取当前用户的个人信息。

#### 更新个人信息
**PUT** `/api/users/profile`

需要认证。更新当前用户的个人信息。

## 错误响应

所有错误响应都遵循以下格式：

```json
{
  "error": "错误描述信息"
}
```

常见HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未认证或认证失败
- `404`: 资源不存在
- `500`: 服务器内部错误

## 使用示例

### 使用curl测试API

```bash
# 健康检查
curl -X GET http://127.0.0.1:5001/api/health

# 获取模型列表
curl -X GET http://127.0.0.1:5001/api/models

# 登录获取token
curl -X POST http://127.0.0.1:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 发送聊天消息（需要替换token）
curl -X POST http://127.0.0.1:5001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo-token" \
  -d '{"message":"你好","model":"gpt-3.5-turbo","user_id":1}'
```

## 注意事项

1. 使用硅基流动模型（Qwen、DeepSeek）需要先配置相应的API密钥
2. 测试环境可以使用 `demo-token` 作为认证token
3. 生产环境建议使用JWT token进行认证
4. 所有时间戳都使用ISO 8601格式
5. 流式聊天需要客户端支持Server-Sent Events