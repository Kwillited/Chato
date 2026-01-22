import { defineStore } from 'pinia';
import { apiService } from '../services/apiService.js';

export const useVectorStore = defineStore('vector', {
  state: () => ({
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
    },
    
    // 搜索知识库
    async searchKnowledgeBase(query) {
      if (!query.trim()) return;
      
      try {
        this.loading = true;
        this.clearError();
        
        // 调用搜索文件内容方法
        const results = await this.searchFileContent(query);
        console.log('知识库搜索结果:', results);
        return results;
      } catch (error) {
        console.error('知识库搜索失败:', error);
        this.setError(`搜索失败: ${error.message || '未知错误'}`);
        return [];
      } finally {
        this.loading = false;
      }
    }
  },
});