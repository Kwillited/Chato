# API接口文档

## 1. 概述

本文档详细描述了 Chato 应用的 API 接口，包括接口地址、请求方法、参数说明、响应格式等。

## 2. 基本信息

### 2.1 API 基础 URL

在开发环境中，API 基础 URL 为：`http://localhost:8000/api/v1`

### 2.2 请求格式

- **Content-Type**: `application/json`
- 请求参数：JSON 格式

### 2.3 响应格式

所有 API 响应均采用 JSON 格式，包含以下字段：

```json
{
  "success": true,
  "data": {},
  "message": "成功",
  "code": 200
}
```

### 2.4 错误处理

当请求失败时，响应格式如下：

```json
{
  "success": false,
  "data": null,
  "message": "错误信息",
  "code": 错误码
}
```

常见错误码：

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 3. 聊天相关接口

### 3.1 创建新聊天

- **接口地址**: `/chats`
- **请求方法**: `POST`
- **请求参数**:
  ```json
  {
    "title": "聊天标题（可选）",
    "model_id": "模型ID（可选）"
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "id": "chat_123456",
      "title": "新聊天",
      "created_at": "2026-01-25T10:00:00Z",
      "updated_at": "2026-01-25T10:00:00Z",
      "model_id": "model_123"
    },
    "message": "聊天创建成功",
    "code": 201
  }
  ```

### 3.2 获取聊天列表

- **接口地址**: `/chats`
- **请求方法**: `GET`
- **查询参数**:
  - `page`: 页码，默认1
  - `page_size`: 每页数量，默认20
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "chats": [
        {
          "id": "chat_123456",
          "title": "新聊天",
          "created_at": "2026-01-25T10:00:00Z",
          "updated_at": "2026-01-25T10:00:00Z",
          "model_id": "model_123"
        }
      ],
      "total": 1,
      "page": 1,
      "page_size": 20
    },
    "message": "查询成功",
    "code": 200
  }
  ```

### 3.3 获取聊天详情

- **接口地址**: `/chats/{chat_id}`
- **请求方法**: `GET`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "id": "chat_123456",
      "title": "新聊天",
      "created_at": "2026-01-25T10:00:00Z",
      "updated_at": "2026-01-25T10:00:00Z",
      "model_id": "model_123"
    },
    "message": "查询成功",
    "code": 200
  }
  ```

### 3.4 更新聊天

- **接口地址**: `/chats/{chat_id}`
- **请求方法**: `PUT`
- **请求参数**:
  ```json
  {
    "title": "更新后的标题",
    "model_id": "new_model_id"
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "id": "chat_123456",
      "title": "更新后的标题",
      "created_at": "2026-01-25T10:00:00Z",
      "updated_at": "2026-01-25T10:30:00Z",
      "model_id": "new_model_id"
    },
    "message": "聊天更新成功",
    "code": 200
  }
  ```

### 3.5 删除聊天

- **接口地址**: `/chats/{chat_id}`
- **请求方法**: `DELETE`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": null,
    "message": "聊天删除成功",
    "code": 200
  }
  ```

### 3.6 获取聊天消息

- **接口地址**: `/chats/{chat_id}/messages`
- **请求方法**: `GET`
- **查询参数**:
  - `page`: 页码，默认1
  - `page_size`: 每页数量，默认50
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "messages": [
        {
          "id": "msg_123456",
          "chat_id": "chat_123456",
          "content": "你好",
          "role": "user",
          "created_at": "2026-01-25T10:00:00Z"
        },
        {
          "id": "msg_789012",
          "chat_id": "chat_123456",
          "content": "你好，我是AI助手",
          "role": "assistant",
          "created_at": "2026-01-25T10:00:01Z"
        }
      ],
      "total": 2,
      "page": 1,
      "page_size": 50
    },
    "message": "查询成功",
    "code": 200
  }
  ```

### 3.7 发送消息

- **接口地址**: `/chats/{chat_id}/messages`
- **请求方法**: `POST`
- **请求参数**:
  ```json
  {
    "content": "你好，AI",
    "role": "user",
    "model_id": "model_123",
    "rag_enabled": true,
    "knowledge_base_ids": ["kb_123"]
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "id": "msg_345678",
      "chat_id": "chat_123456",
      "content": "你好，AI",
      "role": "user",
      "created_at": "2026-01-25T10:15:00Z"
    },
    "message": "消息发送成功",
    "code": 201
  }
  ```

## 4. 文件相关接口

### 4.1 上传文件

- **接口地址**: `/files`
- **请求方法**: `POST`
- **请求参数**: 表单数据
  - `file`: 文件对象
  - `folder_id`: 文件夹ID（可选）
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "id": "file_123456",
      "name": "document.pdf",
      "path": "/uploads/document.pdf",
      "size": 1024000,
      "type": "application/pdf",
      "folder_id": null,
      "created_at": "2026-01-25T10:30:00Z"
    },
    "message": "文件上传成功",
    "code": 201
  }
  ```

### 4.2 获取文件列表

- **接口地址**: `/files`
- **请求方法**: `GET`
- **查询参数**:
  - `folder_id`: 文件夹ID（可选）
  - `page`: 页码，默认1
  - `page_size`: 每页数量，默认20
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "files": [
        {
          "id": "file_123456",
          "name": "document.pdf",
          "path": "/uploads/document.pdf",
          "size": 1024000,
          "type": "application/pdf",
          "folder_id": null,
          "created_at": "2026-01-25T10:30:00Z"
        }
      ],
      "total": 1,
      "page": 1,
      "page_size": 20
    },
    "message": "查询成功",
    "code": 200
  }
  ```

### 4.3 删除文件

- **接口地址**: `/files/{file_id}`
- **请求方法**: `DELETE`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": null,
    "message": "文件删除成功",
    "code": 200
  }
  ```

### 4.4 创建文件夹

- **接口地址**: `/folders`
- **请求方法**: `POST`
- **请求参数**:
  ```json
  {
    "name": "新文件夹",
    "parent_id": null
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "id": "folder_123456",
      "name": "新文件夹",
      "parent_id": null,
      "created_at": "2026-01-25T10:45:00Z"
    },
    "message": "文件夹创建成功",
    "code": 201
  }
  ```

### 4.5 获取文件夹列表

- **接口地址**: `/folders`
- **请求方法**: `GET`
- **查询参数**:
  - `parent_id`: 父文件夹ID（可选）
- **响应示例**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "folder_123456",
        "name": "新文件夹",
        "parent_id": null,
        "created_at": "2026-01-25T10:45:00Z"
      }
    ],
    "message": "查询成功",
    "code": 200
  }
  ```

## 5. 模型相关接口

### 5.1 获取模型列表

- **接口地址**: `/models`
- **请求方法**: `GET`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "model_123",
        "name": "GPT-4",
        "provider": "openai",
        "type": "chat",
        "created_at": "2026-01-25T09:00:00Z"
      },
      {
        "id": "model_456",
        "name": "Claude 3",
        "provider": "anthropic",
        "type": "chat",
        "created_at": "2026-01-25T09:00:00Z"
      }
    ],
    "message": "查询成功",
    "code": 200
  }
  ```

### 5.2 获取模型详情

- **接口地址**: `/models/{model_id}`
- **请求方法**: `GET`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "id": "model_123",
      "name": "GPT-4",
      "provider": "openai",
      "type": "chat",
      "parameters": {
        "temperature": 0.7,
        "max_tokens": 4096
      },
      "created_at": "2026-01-25T09:00:00Z"
    },
    "message": "查询成功",
    "code": 200
  }
  ```

### 5.3 更新模型参数

- **接口地址**: `/models/{model_id}`
- **请求方法**: `PUT`
- **请求参数**:
  ```json
  {
    "parameters": {
      "temperature": 0.5,
      "max_tokens": 8192
    }
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "id": "model_123",
      "name": "GPT-4",
      "provider": "openai",
      "type": "chat",
      "parameters": {
        "temperature": 0.5,
        "max_tokens": 8192
      },
      "created_at": "2026-01-25T09:00:00Z"
    },
    "message": "模型参数更新成功",
    "code": 200
  }
  ```

## 6. RAG 相关接口

### 6.1 创建知识库

- **接口地址**: `/knowledge-bases`
- **请求方法**: `POST`
- **请求参数**:
  ```json
  {
    "name": "新知识库",
    "description": "知识库描述",
    "file_ids": ["file_123456"]
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "id": "kb_123456",
      "name": "新知识库",
      "description": "知识库描述",
      "created_at": "2026-01-25T11:00:00Z"
    },
    "message": "知识库创建成功",
    "code": 201
  }
  ```

### 6.2 获取知识库列表

- **接口地址**: `/knowledge-bases`
- **请求方法**: `GET`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "kb_123456",
        "name": "新知识库",
        "description": "知识库描述",
        "created_at": "2026-01-25T11:00:00Z"
      }
    ],
    "message": "查询成功",
    "code": 200
  }
  ```

### 6.3 向知识库添加文件

- **接口地址**: `/knowledge-bases/{kb_id}/files`
- **请求方法**: `POST`
- **请求参数**:
  ```json
  {
    "file_ids": ["file_789012"]
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": null,
    "message": "文件添加成功",
    "code": 200
  }
  ```

### 6.4 从知识库移除文件

- **接口地址**: `/knowledge-bases/{kb_id}/files/{file_id}`
- **请求方法**: `DELETE`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": null,
    "message": "文件移除成功",
    "code": 200
  }
  ```

### 6.5 删除知识库

- **接口地址**: `/knowledge-bases/{kb_id}`
- **请求方法**: `DELETE`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": null,
    "message": "知识库删除成功",
    "code": 200
  }
  ```

## 7. 设置相关接口

### 7.1 获取设置

- **接口地址**: `/settings`
- **请求方法**: `GET`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "language": "zh-CN",
      "theme": "light",
      "notification_enabled": true,
      "notification_display_time": 3000
    },
    "message": "查询成功",
    "code": 200
  }
  ```

### 7.2 更新设置

- **接口地址**: `/settings`
- **请求方法**: `PUT`
- **请求参数**:
  ```json
  {
    "language": "en-US",
    "theme": "dark",
    "notification_enabled": false
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "language": "en-US",
      "theme": "dark",
      "notification_enabled": false,
      "notification_display_time": 3000
    },
    "message": "设置更新成功",
    "code": 200
  }
  ```

## 8. 健康检查接口

### 8.1 检查服务状态

- **接口地址**: `/health`
- **请求方法**: `GET`
- **响应示例**:
  ```json
  {
    "success": true,
    "data": {
      "status": "ok",
      "timestamp": "2026-01-25T11:30:00Z",
      "version": "1.0.0"
    },
    "message": "服务正常",
    "code": 200
  }
  ```

## 9. WebSocket 接口

### 9.1 聊天实时通信

- **接口地址**: `ws://localhost:8000/ws/chat/{chat_id}`
- **连接方式**: WebSocket

#### 9.1.1 发送消息

```json
{
  "type": "message",
  "data": {
    "content": "你好",
    "role": "user"
  }
}
```

#### 9.1.2 接收消息

```json
{
  "type": "message",
  "data": {
    "id": "msg_123456",
    "content": "你好，我是AI助手",
    "role": "assistant",
    "created_at": "2026-01-25T11:45:00Z"
  }
}
```

```json
{
  "type": "stream",
  "data": {
    "content": "正在生成...",
    "done": false
  }
}
```

```json
{
  "type": "stream",
  "data": {
    "content": "完整回复",
    "done": true
  }
}
```

## 10. 认证与授权

### 10.1 API 密钥认证

部分 API 接口需要 API 密钥认证，在请求头中添加：

```
Authorization: Bearer <api_key>
```

### 10.2 权限管理

- **普通用户**: 可以访问自己的聊天记录、文件等
- **管理员**: 可以访问所有资源，管理用户和系统设置

## 11. 速率限制

API 接口实施速率限制，防止滥用：

- **普通用户**: 每分钟 60 次请求
- **管理员**: 每分钟 300 次请求
- **WebSocket**: 每分钟 100 条消息

## 12. 版本控制

API 版本通过 URL 路径进行控制，当前版本为 `v1`。

## 13. 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-01-25 | 初始版本，包含聊天、文件、模型、RAG、设置等接口 |
