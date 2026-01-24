# 架构设计文档

## 1. 项目概述

Chato 是一个基于 Tauri 2 和 Vue 3 开发的跨平台桌面应用，专注于提供强大的 AI 对话智能体功能，集成了 MCP（模型控制面板）和企业级 RAG（检索增强生成）能力。

## 2. 整体架构

Chato 采用前后端分离的架构设计，结合了现代 Web 技术和本地桌面应用的优势：

### 2.1 架构分层

```
+-----------------------+
|     前端应用层        |
|  Vue 3 + Composition  |
|       API + UI        |
+-----------------------+
|                       |
|     Tauri 桥接层      |
|   Rust <-> JavaScript |
|                       |
+-----------------------+
|                       |
|     后端服务层        |
|     Python + Rust     |
|                       |
+-----------------------+
|                       |
|     数据存储层        |
|   本地数据库 + 向量库  |
|                       |
+-----------------------+
```

### 2.2 核心技术栈

| 层          | 技术栈                          | 主要职责                        |
|-------------|---------------------------------|---------------------------------|
| 前端应用层  | Vue 3, Composition API, Pinia   | 用户界面渲染、交互逻辑          |
| Tauri 桥接层 | Rust, Tauri 2                   | 前后端通信、系统资源访问        |
| 后端服务层  | Python, FastAPI                 | AI 模型调用、RAG 处理、业务逻辑 |
| 数据存储层  | SQLite, 向量数据库              | 聊天记录、文档、向量数据存储    |

## 3. 前端架构

### 3.1 代码结构

```
src/
├── App.vue                 # 主应用组件
├── main.js                 # 应用入口
├── components/             # 组件目录
│   ├── chat/               # 聊天相关组件
│   ├── common/             # 通用组件
│   ├── file/               # 文件管理组件
│   ├── layout/             # 布局组件
│   ├── library/            # 可复用组件库
│   └── panel/              # 面板组件
├── composables/            # 组合函数
├── services/               # 服务层
├── store/                  # Pinia 状态管理
├── static/                 # 静态资源
├── utils/                  # 工具函数
└── views/                  # 页面视图
```

### 3.2 核心设计模式

1. **组合函数模式**：使用 Vue 3 Composition API 创建可复用的组合函数
2. **状态管理**：使用 Pinia 进行集中状态管理
3. **服务层抽象**：将 API 调用和业务逻辑封装在服务层
4. **组件化设计**：高度组件化，支持组件复用和维护

### 3.3 关键模块

- **聊天系统**：处理消息发送、接收和展示
- **文件管理**：支持文档上传、知识库创建
- **RAG 功能**：检索增强生成，结合外部知识
- **MCP 面板**：模型控制面板，管理 AI 模型

## 4. 后端架构

### 4.1 代码结构

```
src-tauri/python/
├── app/                    # 主应用目录
│   ├── api/                # API 路由
│   ├── core/               # 核心配置和工具
│   ├── mcp/                # MCP 相关功能
│   ├── models/             # 模型定义和管理
│   ├── repositories/       # 数据访问层
│   ├── services/           # 业务逻辑层
│   └── utils/              # 工具函数
├── scripts/                # 辅助脚本
├── tests/                  # 测试代码
├── main.py                 # 应用入口
└── requirements.txt        # 依赖配置
```

### 4.2 分层架构

```
API层 → 服务层 → DataService层 → Repository层 → 数据层
```

#### 4.2.1 各层职责

| 层 | 主要职责 |
|-----|----------|
| **API层** | 处理HTTP请求和响应、参数验证、路由定义、依赖注入管理 |
| **服务层** | 封装业务逻辑、处理业务规则、调用DataService层和Repository层 |
| **DataService层** | 管理内存数据、处理脏标记机制、提供事务管理功能、封装db对象访问 |
| **Repository层** | 基于SQLAlchemy ORM封装数据库访问、提供CRUD操作、处理数据库会话管理 |
| **数据层** | 基于SQLAlchemy的数据持久化、数据库连接池管理、ORM模型定义、数据迁移支持 |

### 4.3 核心设计模式

1. **分层架构**：严格的分层设计，禁止跨层访问
2. **依赖注入**：使用依赖注入管理服务和资源
3. **模型适配器**：统一不同 AI 模型的接口
4. **RAG 架构**：文档加载 → 文本分割 → 向量存储 → 检索生成
5. **Repository模式**：将数据访问逻辑与业务逻辑分离
6. **脏标记机制**：内存数据变更时设置脏标记，定期自动保存到数据库

### 4.4 主要模块说明

#### 4.4.1 API层

| 模块 | 功能 | 文件路径 |
|------|------|----------|
| chats | 处理聊天相关请求 | app/api/chats_router.py |
| files | 处理文件管理请求 | app/api/files_router.py |
| models | 处理模型相关请求 | app/api/models_router.py |
| mcp | 处理MCP相关请求 | app/api/mcp_router.py |
| settings | 处理设置相关请求 | app/api/settings_router.py |
| vector | 处理向量相关请求 | app/api/vector_router.py |
| health | 处理健康检查请求 | app/api/health_router.py |

#### 4.4.2 服务层

| 模块 | 功能 | 文件路径 |
|------|------|----------|
| ChatService | 聊天业务逻辑 | app/services/chat/chat_service.py |
| GenerationService | 生成服务 | app/services/chat/generation_service.py |
| ModelService | 模型管理逻辑 | app/services/model/model_service.py |
| MCPService | MCP业务逻辑 | app/services/mcp/mcp_service.py |
| DocumentService | 文档管理服务 | app/services/file/document_service.py |
| FileService | 文件服务 | app/services/file/file_service.py |
| SettingService | 设置管理逻辑 | app/services/settings/setting_service.py |
| VectorService | 向量服务 | app/services/vector/vector_service.py |
| VectorStoreService | 向量存储管理 | app/services/vector/vector_store_service.py |
| VectorDBService | 向量数据库服务 | app/services/vector/vector_db_service.py |
| DataService | 数据管理服务 | app/services/data_service.py |

#### 4.4.3 Repository层

| 模块 | 功能 | 文件路径 |
|------|------|----------|
| BaseRepository | 基础仓库类 | app/repositories/base_repository.py |
| ChatRepository | 对话数据访问 | app/repositories/chat_repository.py |
| MessageRepository | 消息数据访问 | app/repositories/message_repository.py |
| ModelRepository | 模型数据访问 | app/repositories/model_repository.py |
| SettingRepository | 设置数据访问 | app/repositories/setting_repository.py |
| DocumentRepository | 文档数据访问 | app/repositories/document_repository.py |
| DocumentChunkRepository | 文档分块数据访问 | app/repositories/document_chunk_repository.py |
| FolderRepository | 文件夹数据访问 | app/repositories/folder_repository.py |
| VectorRepository | 向量数据访问 | app/repositories/vector_repository.py |

#### 4.4.4 核心模块

- **ModelManager**：统一的模型管理接口，支持多种AI模型，提供流式和非流式对话接口
- **VectorStoreService**：向量存储管理、文档嵌入和检索、查询缓存
- **DataService**：内存数据管理、脏标记机制、事务管理

### 4.5 关键流程

#### 4.5.1 聊天流程

1. API层接收聊天请求
2. ChatService处理请求，解析模型信息
3. 调用DataService获取模型配置
4. 调用ModelManager获取AI回复
5. 保存聊天记录到数据库
6. 返回响应

#### 4.5.2 RAG增强流程

1. 文档上传到系统
2. 文档加载器加载文档
3. 文本分割器分割文档
4. 嵌入模型生成向量
5. 向量存储到Chroma
6. 用户查询时，生成查询向量
7. 检索相关文档
8. 构建增强提示
9. 调用AI模型生成回复

#### 4.5.3 模型配置流程

1. API层接收模型配置请求
2. ModelService处理请求
3. 调用ModelRepository更新数据库
4. 调用DataService更新内存数据
5. 设置脏标记
6. 返回响应

### 4.6 开发规范

- **代码风格**：使用PEP 8代码风格，函数和类名采用驼峰命名法，变量名采用下划线命名法
- **分层架构规范**：严格的分层依赖关系，禁止跨层访问
- **日志规范**：使用统一的日志记录器，日志格式为`%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **错误处理**：使用统一的异常处理机制，API层返回统一的错误格式
- **数据验证**：使用Pydantic V2进行数据验证，为所有API请求和响应定义Pydantic模型
- **ORM使用规范**：所有数据库操作通过Repository层进行，避免在服务层直接使用SQLAlchemy会话

### 4.7 部署说明

#### 4.7.1 开发环境部署

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn main:app --reload --port 8000
```

#### 4.7.2 生产环境部署

```bash
# 安装依赖
pip install -r requirements.txt

# 使用uvicorn启动服务（多进程）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用gunicorn作为WSGI服务器
# gunicorn -w 4 -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker main:app
```

#### 4.7.3 配置管理

- 配置文件：使用platformdirs管理配置文件
- 配置项：app.debug, app.host, app.port, rag.enabled, mcp.enabled等
- 配置更新：通过API更新配置，会自动保存到数据库

## 5. 前后端通信

### 5.1 通信机制

Chato 使用 Tauri 提供的 IPC（进程间通信）机制实现前后端通信：

1. **前端调用后端**：通过 `window.__TAURI__.invoke()` 调用 Rust 函数
2. **后端调用前端**：通过 Tauri 提供的事件系统发送事件
3. **HTTP API**：部分功能通过本地 HTTP API 通信

### 5.2 通信流程

```
前端组件 → 组合函数 → API 服务 → Tauri IPC → Rust 桥接 → Python 服务
```

## 6. 数据存储设计

### 6.1 存储分层

1. **关系型数据**：使用 SQLite 存储聊天记录、用户设置等结构化数据
2. **向量数据**：使用向量数据库存储文档向量，用于 RAG 检索
3. **文件存储**：本地文件系统存储上传的文档和资源

### 6.2 数据模型

- **聊天会话**：id, title, created_at, updated_at
- **消息**：id, chat_id, content, role, created_at
- **文档**：id, name, path, size, created_at
- **文档块**：id, document_id, content, chunk_num
- **向量**：id, chunk_id, vector

## 7. 扩展性设计

### 7.1 模型扩展

- 支持多种 AI 模型接入（OpenAI, Anthropic, Ollama 等）
- 模型适配器模式，便于添加新模型

### 7.2 功能扩展

- 模块化设计，便于添加新功能模块
- 插件系统支持，允许扩展应用功能

### 7.3 部署扩展

- 支持跨平台部署（Windows, macOS, Linux）
- 支持多种安装方式（安装包、便携版）

## 8. 性能优化

### 8.1 前端优化

- 组件懒加载
- 虚拟滚动处理大量消息
- 响应式数据优化
- 缓存策略

### 8.2 后端优化

- 异步处理
- 连接池管理
- 向量检索优化
- 模型调用缓存

### 8.3 通信优化

- 批量请求处理
- 数据压缩
- 事件驱动设计

## 9. 安全性设计

### 9.1 数据安全

- 本地数据存储，保护用户隐私
- 加密存储敏感信息
- 安全的数据传输

### 9.2 模型安全

- 模型访问控制
- 输入输出过滤
- 安全的模型调用

### 9.3 应用安全

- 权限管理
- 安全的系统资源访问
- 防止恶意代码注入

## 10. 监控与日志

- 统一日志系统
- 性能监控
- 错误追踪
- 曳光弹追踪系统

## 11. 未来架构演进

- 支持更多 AI 模型
- 增强 RAG 功能
- 优化性能和用户体验
- 支持插件系统
- 增强协作功能
