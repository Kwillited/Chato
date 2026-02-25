# Chato - AI对话智能体

Chato 是一个基于 Vue 3 和 Python FastAPI +Pywebview开发的跨平台桌面应用，专注于提供强大的 AI 对话智能体功能，集成了 MCP（模型上下文协议）和企业级 RAG（检索增强生成）能力，为用户提供高效、智能的对话体验和知识管理解决方案。

## 项目特点

- **现代化技术栈**：Vue 3 + FastAPI + Python，提供流畅的用户体验和高性能后端
- **跨平台支持**：基于 Web 技术，可在多种操作系统上运行
- **模块化架构**：清晰的前后端分离设计，便于维护和扩展
- **丰富的功能**：集成 AI 对话、模型管理、文档处理等多种功能

## 核心功能

### AI对话智能体
- 提供流畅的自然语言对话体验
- 支持多轮对话和上下文理解
- 可定制对话风格和行为
- 支持智能工具调用和agent功能

### MCP（模型上下文协议）
- 集成 Anthropic 模型上下文协议，支持工具调用
- 连接多个 MCP 服务器，加载和管理外部工具
- 将 MCP 工具转换为 LangChain 工具，与智能体集成
- 提供 MCP 工具的上传、管理和配置功能

### 企业级RAG（检索增强生成）
- 支持多种文档格式导入（PDF、Word、Markdown等）
- 高效的向量检索和知识库管理
- 可定制的检索策略和阈值调整
- 支持多知识库并行检索
- 企业级数据安全和隐私保护

### 可视化功能
- 知识图谱可视化
- 上下文可视化
- 工具执行状态展示

## 技术栈

### 前端
- **框架**：Vue 3 (Composition API + `<script setup>`)
- **状态管理**：Pinia
- **路由**：Vue Router
- **构建工具**：Vite
- **UI组件**：自定义组件 + Font Awesome 7
- **其他**：Three.js (3D可视化), Monaco Editor (代码编辑), KaTeX (数学公式)

### 后端
- **框架**：FastAPI
- **数据库**：SQLAlchemy ORM
- **AI集成**：LangChain, 多种LLM提供商支持
- **向量存储**：支持多种向量数据库
- **API设计**：RESTful API
- **桌面应用**：PyWebView

## 环境要求

在开始开发前，请确保您的系统已安装以下软件：

- [Node.js](https://nodejs.org/) (v16+) - JavaScript 运行时
- [npm](https://www.npmjs.com/) (v7+) - Node.js 包管理器
- [Python](https://www.python.org/) (v3.8+) - Python 运行时
- [pip](https://pip.pypa.io/en/stable/) - Python 包管理器


## 快速开始

### 安装依赖

```bash
# 安装前端依赖
npm install

# 安装后端Python依赖
pip install -r backend/requirements.txt
```

### 启动开发服务器

#### 前端开发服务器
```bash
npm run dev
```

#### 后端开发服务器
```bash
python backend/main.py
```

#### 启动桌面应用
```bash
python backend/webview_main.py
```

## 项目结构

项目采用前后端分离的架构：

```
├── src/                 # Vue 前端代码
│   ├── assets/          # 静态资源
│   ├── components/      # Vue 组件
│   ├── composables/     # Vue 组合式函数
│   ├── layout/          # 布局组件
│   ├── router/          # 路由配置
│   ├── services/        # 服务层
│   ├── store/           # Pinia 状态管理
│   ├── static/          # 静态资源（CSS、JavaScript、字体等）
│   ├── utils/           # 工具函数
│   ├── views/           # 页面组件
│   ├── App.vue          # 主应用组件
│   └── main.js          # 应用入口文件
├── backend/             # Python 后端代码
│   ├── app/             # Python 应用代码
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心功能
│   │   ├── llm/         # LLM 相关功能
│   │   ├── models/      # 数据模型
│   │   ├── repositories/ # 数据访问层
│   │   ├── services/    # 业务逻辑层
│   │   └── utils/       # 工具函数
│   ├── config/          # 配置文件
│   ├── main.py          # 后端应用入口
│   ├── webview_main.py  # 桌面应用入口
│   └── requirements.txt # Python 依赖配置
├── index.html           # HTML 入口文件
└── package.json         # npm 项目配置
```

## 开发指南

### Vue 前端开发

- 所有 Vue 组件和前端代码位于 `src/` 目录
- 使用 Vue 3 的 `<script setup>` 语法编写组件
- 状态管理使用 Pinia
- 路由配置位于 `src/router/` 目录

### Python 后端开发

- 后端代码位于 `backend/` 目录
- 使用 FastAPI 框架构建 RESTful API
- 业务逻辑分层清晰：API 层 -> 服务层 -> 数据访问层
- 配置文件位于 `backend/config/` 目录

## 部署指南

### 开发环境

1. 安装依赖（见快速开始部分）
2. 启动前端和后端开发服务器
3. 访问前端开发服务器地址（默认：http://localhost:5173）

### 生产环境

1. 构建前端静态文件：
   ```bash
   npm run build
   ```
2. 部署后端应用（可使用 uvicorn、gunicorn 等）
3. 配置前端静态文件服务

## API 接口

后端提供了丰富的 API 接口，包括：
- 聊天相关：`/api/chats`
- 模型管理：`/api/models`
- 嵌入模型：`/api/embedding-models`
- 文件管理：`/api/files`
- MCP 管理：`/api/mcp`
- 向量存储：`/api/vector`
- 设置管理：`/api/settings`
- 健康检查：`/api/health`

## 学习资源

- [Vue 3 官方文档](https://v3.vuejs.org/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/) - 用于RAG功能开发

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支
3. 提交代码变更
4. 发起 Pull Request

## 许可证

MIT License