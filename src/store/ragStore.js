import { defineStore } from 'pinia';
import { eventBus } from '../services/eventBus.js';
import { apiService } from '../services/apiService.js';

export const useRagStore = defineStore('rag', {
  state: () => ({
    // 加载状态
    loading: false,
    // 错误信息
    error: null,
    // 上传进度（仅用于RAG相关上传）
    uploadProgress: 0,
    // 当前选中的文件夹（用于RAG检索范围）
    currentSelectedFolder: null,
    // RAG配置
    ragConfig: {
      enabled: true,
      topK: 3,
      scoreThreshold: 0.7,
      searchType: 'similarity'
    }
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

    // 搜索文件内容
    async searchFileContent(query) {
      if (!query.trim()) return [];

      this.loading = true;
      this.clearError();

      try {
        // 调用后端API搜索文件内容
        const response = await apiService.get('/api/rag/search', {
          params: { query }
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

    // 设置RAG配置
    setRagConfig(config) {
      this.ragConfig = { ...this.ragConfig, ...config };
    },

    // 获取RAG配置
    getRagConfig() {
      return this.ragConfig;
    },

    // 设置当前选中的文件夹（用于RAG检索范围）
    setCurrentSelectedFolder(folder) {
      this.currentSelectedFolder = folder;
    },

    // 生成增强响应
    async generateRagResponse(query, chatHistory, k = 5) {
      this.loading = true;
      this.clearError();

      try {
        // 调用后端API生成增强响应
        const response = await apiService.post('/api/rag/generate', {
          query,
          chatHistory,
          k,
          ragConfig: this.ragConfig
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
        const response = await apiService.post('/api/rag/reload');
        
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
  },
});
