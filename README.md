# Chato - AI对话智能体

Chato 是一个基于 Tauri 2 和 Vue 3 开发的跨平台桌面应用，专注于提供强大的 AI 对话智能体功能，集成了 MCP（模型控制面板）和企业级 RAG（检索增强生成）能力，为用户提供高效、智能的对话体验和知识管理解决方案。

## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Vue - Official](https://marketplace.visualstudio.com/items?itemName=Vue.volar) + [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode) + [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)

## 核心功能

### AI对话智能体
- 提供流畅的自然语言对话体验
- 支持多轮对话和上下文理解
- 可定制对话风格和行为

### MCP（模型控制面板）
- 集中管理多种AI模型
- 支持模型切换和参数调整
- 实时监控模型性能和资源使用
- 提供模型部署和管理工具

### 企业级RAG（检索增强生成）
- 支持多种文档格式导入（PDF、Word、Markdown等）
- 高效的向量检索和知识库管理
- 可定制的检索策略和阈值调整
- 支持多知识库并行检索
- 企业级数据安全和隐私保护

## 环境要求

在开始开发前，请确保您的系统已安装以下软件：

- [Node.js](https://nodejs.org/) (v16+) - JavaScript 运行时
- [npm](https://www.npmjs.com/) (v7+) - Node.js 包管理器
- [Rust](https://www.rust-lang.org/) (v1.89+) - 系统编程语言
- [Cargo](https://doc.rust-lang.org/cargo/) (v1.89+) - Rust 包管理器

## 快速开始

### 安装依赖

```bash
# 安装前端依赖
npm install

# 安装后端Python依赖
pip install -r src-tauri/python/requirements.txt
```

## 图标库

项目使用 **Font Awesome 7** 作为图标库，所有图标类名均遵循Font Awesome 7规范：
- 实心图标：`fa-solid fa-<icon-name>`
- 常规图标：`fa-regular fa-<icon-name>`
- 品牌图标：`fa-brands fa-<icon-name>`

### 图标使用示例
```vue
<!-- 实心图标 -->
<i class="fa-solid fa-times"></i>

<!-- 常规图标 -->
<i class="fa-regular fa-comment"></i>

<!-- 品牌图标 -->
<i class="fa-brands fa-github"></i>

<!-- ActionButton组件中使用 -->
<ActionButton icon="fa-bars" title="菜单" />
```

### 注意事项
- 请勿混合使用不同版本的Font Awesome类名
- 项目已移除旧版Font Awesome支持，请使用Font Awesome 7类名
- 如有疑问，请参考 [Font Awesome 7官方文档](https://fontawesome.com/docs)

### 端口修改

tauri.conf.json，将devUrl端口与vite.config.js中的端口保持一致

### 前端开发服务器

启动开发服务器，在开发模式下运行应用：

```bash
npm run dev
```

### 开发模式

启动开发服务器，在开发模式下运行应用：

```bash
npm run tauri dev
```

这将同时启动 Vue 开发服务器和 Tauri 应用，任何代码变更都会自动刷新应用。

### 构建生产版本

构建用于发布的生产版本：

```bash
npm run tauri build

npx tauri build
```

构建完成后，可在 `src-tauri/target/release/` 目录下找到可执行文件。

## 项目结构

项目采用前后端分离的架构：

```
├── src/                 # Vue 前端代码
│   ├── App.vue          # 主应用组件
│   ├── main.js          # 应用入口文件
│   ├── components/      # Vue 组件
│   ├── router/          # 路由配置
│   ├── services/        # 服务层
│   ├── store/           # Pinia 状态管理
│   ├── static/          # 静态资源（CSS、JavaScript、字体等）
│   └── views/           # 页面组件
├── src-tauri/           # Tauri 后端代码
│   ├── src/             # Rust 源代码
│   ├── python/          # Python 后端代码
│   │   ├── app/         # Python 应用代码
│   │   ├── scripts/     # Python 脚本
│   │   ├── main.py      # Python 应用入口
│   │   └── requirements.txt # Python 依赖配置
│   ├── Cargo.toml       # Rust 依赖配置
│   └── tauri.conf.json  # Tauri 应用配置
├── index.html           # HTML 入口文件
└── package.json         # npm 项目配置
```

## 开发指南

### Vue 前端开发

- 所有 Vue 组件和前端代码位于 `src/` 目录
- 使用 Vue 3 的 `<script setup>` 语法编写组件
- 可通过 Tauri API 调用后端 Rust 功能

### Tauri 后端开发

- Rust 代码位于 `src-tauri/src/` 目录
- 可通过 Tauri 命令将 Rust 函数暴露给前端
- 配置文件 `tauri.conf.json` 用于设置应用窗口、图标等属性

## Tauri 常用命令

```bash
# 初始化 Tauri 项目（已完成）
npm create tauri-app

# 添加 Android 平台支持
npm run tauri android init

# 启动 Android 开发模式
npm run tauri android dev

# 查看 Tauri 帮助信息
npm run tauri -- --help
```

## 打包虚拟环境
1. python -m venv env_name
2. env_name\Scripts\activate
3. pip install -r src-tauri/resources/python/requirements.txt
4. deactivate

## 学习资源

- [Tauri 官方文档](https://tauri.app/)
- [Vue 3 官方文档](https://v3.vuejs.org/)
- [Rust 官方文档](https://www.rust-lang.org/learn)
- [LangChain 文档](https://python.langchain.com/) - 用于RAG功能开发
- [Hugging Face](https://huggingface.co/) - AI模型资源