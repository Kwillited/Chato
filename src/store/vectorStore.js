import { defineStore } from 'pinia';
import { apiService } from '../services/apiService.js';
import { errorUtils, loadingUtils, apiUtils } from '../utils/storeUtils.js';

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
    // 当前选中的文件夹（用于RAG检索范围）
    currentSelectedFolder: null,
    // 兼容ragStore的files属性，用于存储当前文件夹中的文件列表
    files: [],
    // 扩展预留
    extensions: {}
  }),

  getters: {
    // 获取加载状态
    isLoading: (state) => {
      return state.loading;
    },

    // 获取错误信息
    getError: (state) => {
      return state.error;
    },

    // 获取检索配置（兼容旧代码）
    retrievalConfig: (state) => {
      return {
        mode: state.config.retrieval.mode,
        topK: state.config.retrieval.topK,
        scoreThreshold: state.config.retrieval.threshold
      };
    }
  },

  actions: {
    // 设置错误信息
    setError(error) {
      errorUtils.setError(this, error);
    },
    
    // 清空错误信息
    clearError() {
      errorUtils.clearError(this);
    },
    
    // 设置上传进度
    setUploadProgress(progress) {
      this.uploadProgress = progress;
    },
    
    // 重置上传进度
    resetUploadProgress() {
      this.uploadProgress = 0;
    },
    
    // 更新向量配置
    updateConfig(config) {
      this.config = { ...this.config, ...config };
    },
    
    // 更新检索配置
    updateRetrievalConfig(retrievalConfig) {
      this.config.retrieval = { ...this.config.retrieval, ...retrievalConfig };
    },
    
    // 更新嵌入配置
    updateEmbeddingConfig(embeddingConfig) {
      this.config.embedding = { ...this.config.embedding, ...embeddingConfig };
    },
    
    // 更新存储配置
    updateStorageConfig(storageConfig) {
      this.config.storage = { ...this.config.storage, ...storageConfig };
    },
    
    // 更新检索范围
    updateScope(scopeConfig) {
      this.config.scope = { ...this.config.scope, ...scopeConfig };
    },
    
    // 设置当前选中的文件夹（用于RAG检索范围）
    setCurrentSelectedFolder(folder) {
      this.currentSelectedFolder = folder;
    },
    
    // ========== 兼容ragStore的API ==========
    
    // 设置RAG配置（兼容ragStore）
    setRagConfig(config) {
      this.config = {
        ...this.config,
        enabled: config.enabled !== undefined ? config.enabled : this.config.enabled,
        retrieval: {
          ...this.config.retrieval,
          topK: config.topK !== undefined ? config.topK : this.config.retrieval.topK,
          threshold: config.scoreThreshold !== undefined ? config.scoreThreshold : this.config.retrieval.threshold,
          mode: config.searchType !== undefined ? config.searchType : this.config.retrieval.mode
        }
      };
    },
    
    // 获取RAG配置（兼容ragStore）
    getRagConfig() {
      return {
        enabled: this.config.enabled,
        topK: this.config.retrieval.topK,
        scoreThreshold: this.config.retrieval.threshold,
        searchType: this.config.retrieval.mode
      };
    },

    // 搜索文件内容
    async searchFileContent(query) {
      if (!query.trim()) return [];

      try {
        const results = await apiUtils.wrapApiCall(this, async () => {
          // 调用后端API搜索文件内容
          const response = await apiService.post('/vectors/search-documents', {
            query, 
            k: this.config.retrieval.topK,
            score_threshold: this.config.retrieval.threshold,
            search_type: this.config.retrieval.mode
          });
          
          // 确保正确处理响应格式
          return response.success && response.results ? response.results : [];
        }, '搜索文件内容失败');
        
        return results;
      } catch (error) {
        return [];
      }
    },

    // 生成增强响应
    async generateRagResponse(query, chatHistory, k = 5) {
      try {
        const response = await apiUtils.wrapApiCall(this, async () => {
          // 调用后端API生成增强响应
          const response = await apiService.post('/vectors/enhanced-prompt', {
            query,
            chatHistory,
            k,
            ragConfig: {
              enabled: this.config.enabled,
              topK: this.config.retrieval.topK,
              scoreThreshold: this.config.retrieval.threshold,
              searchType: this.config.retrieval.mode
            }
          });
          
          // 确保正确处理响应格式
          return response.success ? response : { success: false, error: response.message || '生成增强响应失败' };
        }, '生成增强响应失败');
        
        return response;
      } catch (error) {
        return { success: false, error: error.message || '生成增强响应失败' };
      }
    },

    // 重新加载向量库
    async reloadVectorStore() {
      try {
        const response = await apiUtils.wrapApiCall(this, async () => {
          // 调用后端API重新加载向量库
          const response = await apiService.post('/vectors/manage', {
            action: 'reload'
          });
          
          // 确保正确处理响应格式
          if (response.success) {
            return { success: true, message: response.message || '向量库重新加载成功' };
          } else {
            return { success: false, error: response.message || '向量库重新加载失败' };
          }
        }, '重新加载向量库失败');
        
        return response;
      } catch (error) {
        return { success: false, error: error.message || '重新加载向量库失败' };
      }
    },

    // 加载向量库列表
    async loadVectorStores() {
      try {
        await apiUtils.wrapApiCall(this, async () => {
          // 调用后端API获取向量库列表
          const response = await apiService.get('/vectors/stores');
          
          if (response.success && Array.isArray(response.stores)) {
            this.vectorStores = response.stores;
            if (response.stores.length > 0 && !this.currentVectorStore) {
              this.currentVectorStore = response.stores[0].id;
            }
          }
        }, '加载向量库列表失败');
      } catch (error) {
        // 错误已在 wrapApiCall 中处理
      }
    },

    // 切换向量库
    async switchVectorStore(storeId) {
      try {
        const response = await apiUtils.wrapApiCall(this, async () => {
          // 调用后端API切换向量库
          const response = await apiService.post('/vectors/switch', {
            store_id: storeId
          });
          
          if (response.success) {
            this.currentVectorStore = storeId;
            return { success: true, message: response.message || '向量库切换成功' };
          } else {
            return { success: false, error: response.message || '向量库切换失败' };
          }
        }, '切换向量库失败');
        
        return response;
      } catch (error) {
        return { success: false, error: error.message || '切换向量库失败' };
      }
    },
    
    // 搜索知识库（兼容ragStore）
    async searchKnowledgeBase(query) {
      if (!query.trim()) return;
      
      try {
        // 调用搜索文件内容方法
        const results = await this.searchFileContent(query);
        console.log('知识库搜索结果:', results);
        return results;
      } catch (error) {
        console.error('知识库搜索失败:', error);
        errorUtils.setError(this, `搜索失败: ${error.message || '未知错误'}`);
        return [];
      }
    },
    
    // 加载文件列表（兼容ragStore）
    async loadFiles() {
      try {
        loadingUtils.startLoading(this);
        
        // 调用fileStore的loadFiles方法
        const fileStore = await import('./fileStore.js').then(m => m.useFileStore());
        await fileStore.loadFiles();
        
        // 将fileStore的文件列表同步到vectorStore的files属性
        this.files = fileStore.files;
        
        loadingUtils.setLoadingFalse(this);
        return this.files;
      } catch (error) {
        console.error('加载文件列表失败:', error);
        errorUtils.setError(this, `加载文件列表失败: ${error.message || '未知错误'}`);
        loadingUtils.setLoadingFalse(this);
        this.files = [];
        return this.files;
      }
    },
    
    // 批量上传文件（兼容ragStore）
    async batchUploadFiles(files) {
      try {
        loadingUtils.startLoading(this);
        
        // 调用fileStore的batchUploadFiles方法
        const fileStore = await import('./fileStore.js').then(m => m.useFileStore());
        const result = await fileStore.batchUploadFiles(files);
        
        // 重新加载文件列表
        await this.loadFiles();
        
        loadingUtils.setLoadingFalse(this);
        return result;
      } catch (error) {
        console.error('批量上传文件失败:', error);
        errorUtils.setError(this, `批量上传文件失败: ${error.message || '未知错误'}`);
        loadingUtils.setLoadingFalse(this);
        return { successCount: 0, failCount: files.length, uploadResults: [] };
      }
    },
    
    // 删除文件（兼容ragStore）
    async deleteFile(fileId, folderId) {
      try {
        loadingUtils.startLoading(this);
        
        // 查找要删除的文件
        const fileToDelete = this.files.find(f => f.id === fileId);
        if (!fileToDelete) {
          throw new Error('文件不存在');
        }
        
        // 调用fileStore的deleteDocument方法
        const fileStore = await import('./fileStore.js').then(m => m.useFileStore());
        await fileStore.deleteDocument(fileToDelete.name, folderId);
        
        // 重新加载文件列表
        await this.loadFiles();
        
        loadingUtils.setLoadingFalse(this);
        return { success: true };
      } catch (error) {
        console.error('删除文件失败:', error);
        errorUtils.setError(this, `删除文件失败: ${error.message || '未知错误'}`);
        loadingUtils.setLoadingFalse(this);
        return { success: false, error: error.message };
      }
    },
    
    // 验证文件（兼容ragStore）
    validateFile(file) {
      // 简单的文件验证逻辑
      const maxSize = 50 * 1024 * 1024; // 50MB
      const supportedTypes = ['pdf', 'docx', 'txt', 'csv', 'xlsx', 'pptx', 'md'];
      const fileExtension = file.name.split('.').pop().toLowerCase();
      
      if (file.size > maxSize) {
        return { valid: false, message: `文件太大: ${file.name} - 最大支持50MB` };
      }
      
      if (!supportedTypes.includes(fileExtension)) {
        return { valid: false, message: `不支持的文件类型: ${file.name} - 支持类型: ${supportedTypes.join(', ')}` };
      }
      
      return { valid: true };
    }
  },
});