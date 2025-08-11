# ChatHub - AI API 集成平台

一个现代化的AI API集成平台，提供多种AI模型的统一访问接口，让您轻松管理和使用各种AI服务。

## 🚀 项目特色

- **多模型支持**: 集成 GPT-4、Claude 3、Gemini Pro 等主流AI模型
- **统一管理**: 一个平台管理所有AI模型和API密钥
- **实时聊天**: 流式输出，支持 Markdown 渲染和代码高亮
- **用户系统**: 完整的用户注册、登录、权限管理
- **使用统计**: 详细的使用记录和额度管理
- **响应式设计**: 支持桌面端和移动端访问

## 📁 项目结构

```
chathub/
├── frontend/              # Vue.js 前端应用
│   ├── src/
│   │   ├── components/    # 可复用组件
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   └── utils/         # 工具函数
│   ├── package.json       # 前端依赖
│   └── Dockerfile         # 前端容器配置
├── backend/               # Flask 后端API
│   ├── routes/            # API 路由
│   ├── models/            # 数据模型
│   ├── utils/             # 工具函数
│   ├── database/          # SQLite 数据库
│   ├── requirements.txt   # 后端依赖
│   └── Dockerfile         # 后端容器配置
├── docker-compose.yml     # Docker 编排配置
├── start.sh              # 一键启动脚本
└── README.md
```

## 🤖 支持的AI模型

| 模型 | 提供商 | 功能特性 |
|------|--------|----------|
| GPT-4o | OpenAI | 文本生成、视觉理解、函数调用 |
| GPT-4o Mini | OpenAI | 高性价比文本生成 |
| Claude 3.5 Sonnet | Anthropic | 高质量文本生成、代码编写 |
| Claude 3 Haiku | Anthropic | 快速响应、经济实用 |
| Gemini 1.5 Pro | Google | 多模态理解、长文本处理 |
| Gemini 1.5 Flash | Google | 快速响应、高效处理 |

## 🛠️ 技术栈

- **前端**: Vue 3 + Vite + Ant Design Vue + Vue Router
- **后端**: Flask + SQLAlchemy + Flask-CORS + PyJWT
- **数据库**: SQLite
- **部署**: Docker + Docker Compose
- **样式**: CSS3 + 响应式设计
- **其他**: Axios、Markdown-it、Prism.js

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 方式一：使用启动脚本（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd chathub

# 一键启动
./start.sh
```

### 方式二：手动启动

#### 后端启动
```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

#### 前端启动
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 方式三：Docker 部署

```bash
# 构建并启动所有服务
docker compose up --build

# 后台运行
docker compose up -d --build

# 停止服务
docker compose down
```

## 🌐 访问地址

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5001
- **API文档**: 查看 `backend/API_DOCUMENTATION.md`

## ⚙️ 配置说明

### 环境变量配置

复制并修改环境变量文件：

```bash
# 前端配置
cp frontend/.env.example frontend/.env.development

# 根据需要修改配置
```

### API密钥配置

1. 访问 http://localhost:3000
2. 注册/登录账户
3. 进入"API密钥管理"页面
4. 添加各AI服务商的API密钥

## 📖 功能说明

- **聊天界面**: 支持多轮对话，Markdown渲染，代码高亮
- **模型管理**: 添加、编辑、启用/禁用AI模型
- **API密钥管理**: 安全存储和管理各服务商的API密钥
- **用户管理**: 用户注册、登录、权限控制
- **使用统计**: 查看API调用次数、费用统计
- **价格方案**: 不同的订阅方案和使用额度

## 🔧 开发说明

### 项目初始化

```bash
# 初始化默认模型数据
cd backend
python init_default_models.py
```

### 数据库管理

项目使用 SQLite 数据库，数据文件位于 `backend/database/chathub.db`

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请提交 Issue 或联系开发团队。