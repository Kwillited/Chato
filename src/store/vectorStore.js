import { defineStore } from 'pinia';
import { eventBus } from '../services/eventBus.js';
import { apiService } from '../services/apiService.js';

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
      this.error = error;
    },

    // 清空错误信息
    clearError() {
      this.error = null;
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

    // 搜索文件内容
    async searchFileContent(query) {
      if (!query.trim()) return [];

      this.loading = true;
      this.clearError();

      try {
        // 调用后端API搜索文件内容
        const response = await apiService.post('/api/vectors/search-documents', {
          query, 
          k: this.config.retrieval.topK,
          score_threshold: this.config.retrieval.threshold,
          search_type: this.config.retrieval.mode
        });
        
        // 确保正确处理响应格式
        return response.success && response.results ? response.results : [];
      } catch (error) {
        console.error('搜索文件内容失败:', error);
        this.setError(`搜索失败: ${error.message || '未知错误'}`);
        return [];
      } finally {
        this.loading = false;
      }
    },

    // 生成增强响应
    async generateRagResponse(query, chatHistory, k = 5) {
      this.loading = true;
      this.clearError();

      try {
        // 调用后端API生成增强响应
        const response = await apiService.post('/api/vectors/enhanced-prompt', {
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
      } catch (error) {
        console.error('生成增强响应失败:', error);
        this.setError(`生成增强响应失败: ${error.message || '未知错误'}`);
        return { success: false, error: error.message || '生成增强响应失败' };
      } finally {
        this.loading = false;
      }
    },

    // 重新加载向量库
    async reloadVectorStore() {
      this.loading = true;
      this.clearError();

      try {
        // 调用后端API重新加载向量库
        const response = await apiService.post('/api/vectors/manage', {
          action: 'reload'
        });
        
        // 确保正确处理响应格式
        if (response.success) {
          return { success: true, message: response.message || '向量库重新加载成功' };
        } else {
          return { success: false, error: response.message || '向量库重新加载失败' };
        }
      } catch (error) {
        console.error('重新加载向量库失败:', error);
        this.setError(`重新加载向量库失败: ${error.message || '未知错误'}`);
        return { success: false, error: error.message || '重新加载向量库失败' };
      } finally {
        this.loading = false;
      }
    },

    // 加载向量库列表
    async loadVectorStores() {
      this.loading = true;
      this.clearError();

      try {
        // 调用后端API获取向量库列表
        const response = await apiService.get('/api/vectors/stores');
        
        if (response.success && Array.isArray(response.stores)) {
          this.vectorStores = response.stores;
          if (response.stores.length > 0 && !this.currentVectorStore) {
            this.currentVectorStore = response.stores[0].id;
          }
        }
      } catch (error) {
        console.error('加载向量库列表失败:', error);
        this.setError(`加载向量库列表失败: ${error.message || '未知错误'}`);
      } finally {
        this.loading = false;
      }
    },

    // 切换向量库
    async switchVectorStore(storeId) {
      this.loading = true;
      this.clearError();

      try {
        // 调用后端API切换向量库
        const response = await apiService.post('/api/vectors/switch', {
          store_id: storeId
        });
        
        if (response.success) {
          this.currentVectorStore = storeId;
          return { success: true, message: response.message || '向量库切换成功' };
        } else {
          return { success: false, error: response.message || '向量库切换失败' };
        }
      } catch (error) {
        console.error('切换向量库失败:', error);
        this.setError(`切换向量库失败: ${error.message || '未知错误'}`);
        return { success: false, error: error.message || '切换向量库失败' };
      } finally {
        this.loading = false;
      }
    }
  },
});