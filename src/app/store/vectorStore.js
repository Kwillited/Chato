import { defineStore } from 'pinia';
import { apiService } from '../../shared/api/apiService.js';
import logger from '../../shared/utils/logger.js';
import { useBaseStore } from './baseStore.js';

// 获取基础Store功能
const baseStore = useBaseStore();

export const useVectorStore = defineStore('vector', {
  state: () => ({
    // 基础状态
    ...baseStore.state(),
    // 操作状态
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
    // 基础getters
    ...baseStore.getters,
  },

  actions: {
    // 基础actions
    ...baseStore.actions,
    
    // 设置上传进度
    setUploadProgress(progress) {
      this.uploadProgress = progress;
    },
    
    // 重置上传进度
    resetUploadProgress() {
      this.uploadProgress = 0;
    },
    
    // 设置当前选中的文件夹（用于RAG检索范围）
    setCurrentSelectedFolder(folder) {
      this.currentSelectedFolder = folder;
    },

    // 搜索文件内容
    async searchFileContent(query) {
      if (!query.trim()) return [];

      return this.callApi(async () => {
        // 动态导入settingsStore，获取向量配置
        const { useSettingsStore } = await import('./settingsStore.js');
        const settingsStore = useSettingsStore();
        const vectorConfig = settingsStore.vectorConfig;
        
        // 调用后端API搜索文件内容
        const response = await apiService.post('/api/vectors/search-documents', {
          query, 
          k: vectorConfig.retrieval.topK,
          score_threshold: vectorConfig.retrieval.threshold,
          search_type: vectorConfig.retrieval.mode
        });
        
        // 确保正确处理响应格式
        return response.success && response.results ? response.results : [];
      }, { handleError: true });
    },

    // 生成增强响应
    async generateRagResponse(query, chatHistory, k = 5) {
      return this.callApi(async () => {
        // 动态导入settingsStore，获取向量配置
        const { useSettingsStore } = await import('./settingsStore.js');
        const settingsStore = useSettingsStore();
        const vectorConfig = settingsStore.vectorConfig;
        
        // 调用后端API生成增强响应
        const response = await apiService.post('/api/vectors/enhanced-prompt', {
          query,
          chatHistory,
          k,
          ragConfig: {
            enabled: vectorConfig.enabled,
            topK: vectorConfig.retrieval.topK,
            scoreThreshold: vectorConfig.retrieval.threshold,
            searchType: vectorConfig.retrieval.mode
          }
        });
        
        // 确保正确处理响应格式
        return response.success ? response : { success: false, error: response.message || '生成增强响应失败' };
      }, { handleError: true });
    },

    // 重新加载向量库
    async reloadVectorStore() {
      return this.callApi(async () => {
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
      }, { handleError: true });
    },

    // 加载向量库列表
    async loadVectorStores() {
      return this.callApi(async () => {
        // 调用后端API获取向量库列表
        const response = await apiService.get('/api/vectors/stores');
        
        if (response.success && Array.isArray(response.stores)) {
          this.vectorStores = response.stores;
          if (response.stores.length > 0 && !this.currentVectorStore) {
            this.currentVectorStore = response.stores[0].id;
          }
        }
      }, { handleError: true });
    },

    // 切换向量库
    async switchVectorStore(storeId) {
      return this.callApi(async () => {
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
      }, { handleError: true });
    },
    
    // 搜索知识库
    async searchKnowledgeBase(query) {
      if (!query.trim()) return [];
      
      return this.callApi(async () => {
        // 调用搜索文件内容方法
        const results = await this.searchFileContent(query);
        logger.info('知识库搜索结果:', results);
        return results;
      }, { handleError: true });
    }
  },
});