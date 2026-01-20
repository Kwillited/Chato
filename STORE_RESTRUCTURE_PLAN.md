# Store结构调整方案

## 1. 现有问题分析

### 1.1 配置重复
- **ragConfig** 在 `ragStore.js` 和 `settingsStore.js` 中重复定义
- 两个store中的字段名称和默认值不一致（如 `searchType` vs `retrievalMode`，`enabled` 默认值不同）
- 存在数据不一致风险，难以维护

### 1.2 职责划分不清晰
- `ragStore` 同时处理RAG配置和向量操作
- 缺乏专门的向量操作管理机制
- 扩展性不足，难以支持未来向量相关功能扩展

### 1.3 命名不准确
- `ragStore` 命名局限于RAG场景，无法涵盖所有向量操作
- 不便于未来扩展向量相关功能

## 2. 新Store结构设计

### 2.1 核心Store规划

| Store名称 | 主要职责 | 包含内容 | 扩展预留 |
|---------|---------|---------|---------|
| **modelSettingStore** | 模型生成参数管理 | 温度、top_p、top_k、max_tokens、频率惩罚 | 模型特定参数扩展 |
| **vectorStore** | 向量操作与配置管理 | 向量检索配置、向量存储管理、向量库操作 | 向量索引、向量生成、多向量库支持 |
| **settingsStore** | 全局系统设置 | 暗黑模式、字体、语言、通知设置 | 系统级配置扩展 |
| **chatStore** | 聊天会话管理 | 消息历史、当前会话状态 | 会话模板、会话类型扩展 |

### 2.2 详细Store设计

#### 2.2.1 vectorStore（新增/重构自ragStore）

**核心职责**：管理所有向量相关操作和配置

**State结构**：
```javascript
export const useVectorStore = defineStore('vector', {
  state: () => ({
    // 向量配置（合并原ragConfig）
    config: {
      // 启用状态
      enabled: false,
      // 检索配置
      retrieval: {
        mode: 'vector', // vector/keyword/hybrid
        topK: 3,        // 检索数量
        threshold: 0.7, // 相关性阈值
        similarityType: 'cosine' // 相似度计算方式
      },
      // 嵌入模型配置
      embedding: {
        model: 'qwen3-embedding-0.6b',
        chunkSize: 1000,
        chunkOverlap: 100
      },
      // 向量存储配置
      storage: {
        type: 'chroma',
        path: '',
        knowledgeBasePath: ''
      },
      // 检索范围
      scope: {
        selectedFolders: [],
        selectedKnowledgeBases: []
      }
    },
    // 操作状态
    loading: false,
    error: null,
    uploadProgress: 0,
    // 向量库状态
    vectorStores: [], // 支持多向量库
    currentVectorStore: null,
    // 扩展预留
    extensions: {}
  }),
  
  // Getters和Actions...
});
```

**职责说明**：
- 统一管理所有向量相关配置
- 提供向量检索、向量生成、向量存储等操作
- 支持多向量库管理
- 预留扩展点，便于未来添加新的向量功能

#### 2.2.2 modelSettingStore（保留并优化）

**核心职责**：管理模型生成参数

**状态结构**：
```javascript
export const useModelSettingStore = defineStore('modelSetting', {
  state: () => ({
    // 模型列表和配置
    availableModels: [],
    models: [],
    // 模型生成参数
    generationParams: {
      temperature: 0.7,
      max_tokens: 2000,
      top_p: 1.0,
      top_k: 50,
      frequency_penalty: 0.0
    },
    // 加载状态
    isLoading: false,
    error: null
  }),
  
  // Getters和Actions...
});
```

**优化建议**：
- 将 `modelParams` 重命名为 `generationParams`，更准确反映其用途
- 统一管理所有模型生成相关参数

#### 2.2.3 settingsStore（简化）

**核心职责**：管理全局系统设置

**状态结构**：
```javascript
export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // 面板和视图状态
    activePanel: 'history',
    activeContent: 'sendMessage',
    // 系统设置
    system: {
      darkMode: false,
      fontSize: 16,
      fontFamily: 'Inter, system-ui, sans-serif',
      language: 'zh-CN',
      autoScroll: true,
      showTimestamps: true,
      confirmDelete: true,
      streamingEnabled: true,
      chatStyleDocument: false
    },
    // MCP设置
    mcp: {
      enabled: false,
      serverAddress: '',
      serverPort: 8080,
      timeout: 30
    },
    // 通知设置
    notifications: {
      enabled: true,
      newMessage: true,
      sound: false,
      system: true,
      displayTime: '5秒'
    }
  }),
  
  // 移除RAG配置相关内容
  // Getters和Actions...
});
```

**简化说明**：
- 移除重复的RAG配置
- 保留全局系统设置
- 将各配置分组，提高可读性

### 2.3 各Store职责边界

| 功能领域 | 负责Store | 说明 |
|---------|---------|-----|
| 模型生成参数 | modelSettingStore | 温度、top_p、top_k、max_tokens等 |
| 向量检索配置 | vectorStore | 检索模式、检索数量、相关性阈值等 |
| 向量存储管理 | vectorStore | 向量库类型、存储路径、嵌入模型等 |
| 向量操作 | vectorStore | 向量检索、向量生成、向量库管理等 |
| 全局系统设置 | settingsStore | 暗黑模式、字体、语言等 |
| 聊天会话管理 | chatStore | 消息历史、当前会话状态等 |

## 3. 后端数据存储调整

### 3.1 数据结构调整

**建议调整**：
- 统一RAG/向量配置的数据结构，与前端store保持一致
- 在数据库中创建专门的 `vector_config` 表，存储向量相关配置
- 表结构示例：
  ```sql
  CREATE TABLE vector_config (
      id INT PRIMARY KEY AUTO_INCREMENT,
      user_id INT NOT NULL,
      enabled BOOLEAN DEFAULT FALSE,
      retrieval_mode VARCHAR(20) DEFAULT 'vector',
      top_k INT DEFAULT 3,
      threshold FLOAT DEFAULT 0.7,
      similarity_type VARCHAR(20) DEFAULT 'cosine',
      embedding_model VARCHAR(100) DEFAULT 'qwen3-embedding-0.6b',
      chunk_size INT DEFAULT 1000,
      chunk_overlap INT DEFAULT 100,
      vector_db_type VARCHAR(20) DEFAULT 'chroma',
      vector_db_path VARCHAR(255) DEFAULT '',
      knowledge_base_path VARCHAR(255) DEFAULT '',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
  );
  ```

### 3.2 API调整

**建议调整**：
- 提供统一的向量配置API，替换现有的RAG配置API
- API路径示例：
  - `GET /api/vectors/config` - 获取向量配置
  - `PUT /api/vectors/config` - 更新向量配置
  - `POST /api/vectors/search` - 执行向量检索
  - `POST /api/vectors/generate` - 生成向量

## 4. 迁移计划

### 4.1 前端迁移步骤

1. **创建vectorStore**：
   - 实现新的vectorStore.js
   - 合并ragStore和settingsStore中的RAG配置
   - 实现向量操作相关的actions

2. **修改依赖组件**：
   - 更新使用ragStore的组件，改为使用vectorStore
   - 更新使用settingsStore中ragConfig的组件，改为使用vectorStore

3. **移除重复配置**：
   - 从ragStore中移除ragConfig
   - 从settingsStore中移除ragConfig
   - 简化ragStore，或将其功能整合到vectorStore

4. **测试验证**：
   - 验证所有功能正常工作
   - 验证配置数据一致性
   - 验证向量操作正常

### 4.2 后端迁移步骤

1. **创建vector_config表**：
   - 实现新的数据表结构
   - 迁移现有RAG配置数据

2. **更新API**：
   - 实现新的向量配置API
   - 更新现有API以使用新的数据结构

3. **数据迁移**：
   - 从现有配置表迁移RAG配置数据到vector_config表
   - 确保数据完整性和一致性

4. **测试验证**：
   - 验证API正常工作
   - 验证数据迁移正确
   - 验证前端和后端数据一致性

## 5. 扩展预留

### 5.1 向量功能扩展
- 支持多向量库管理
- 支持向量索引优化
- 支持自定义嵌入模型
- 支持向量相似性可视化
- 支持向量召回率统计

### 5.2 API扩展预留
- 向量生成API
- 向量索引管理API
- 向量库统计API
- 向量可视化数据API

## 6. 预期收益

1. **职责清晰**：各Store职责明确，便于维护和扩展
2. **数据一致**：消除配置重复，避免数据不一致风险
3. **扩展性强**：专门的vectorStore便于未来向量相关功能扩展
4. **命名准确**：vectorStore更准确反映其功能范围
5. **便于测试**：各Store职责单一，便于单元测试和集成测试
6. **用户体验**：统一的配置管理，提升用户体验

## 7. 风险评估

### 7.1 迁移风险
- 数据迁移可能导致配置丢失
- 组件依赖更新可能引入新问题
- 需要全面测试确保功能正常

### 7.2 缓解措施
- 数据迁移前备份现有数据
- 逐步迁移，先在开发环境测试
- 编写详细的测试用例
- 提供回滚方案

## 8. 实施建议

1. **分阶段实施**：先实现vectorStore，再逐步迁移组件
2. **保持向后兼容**：在迁移过程中保持现有API的兼容性
3. **充分测试**：在每个阶段进行全面测试
4. **文档更新**：更新API文档和开发文档
5. **培训开发人员**：确保开发团队理解新的store结构和职责划分

通过以上调整方案，可以建立一个职责清晰、扩展性强的store结构，为未来向量相关功能的扩展奠定基础。