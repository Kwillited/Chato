// src/store/baseStore.js
import logger from '../utils/logger.js';

/**
 * 基础Store功能，提供通用的状态管理和API调用封装
 * @returns {Object} 包含通用状态、getters和actions的对象
 */
export function useBaseStore() {
  // 通用状态
  const state = () => ({
    // 加载状态
    isLoading: false,
    // 错误信息
    error: null,
  });

  // 通用getters
  const getters = {
    // 获取加载状态
    isLoading: (state) => state.isLoading,
    // 获取错误信息
    getError: (state) => state.error,
  };

  // 通用actions
  const actions = {
    /**
     * 设置加载状态
     * @param {boolean} loading - 加载状态
     */
    setLoading(loading) {
      this.isLoading = loading;
    },

    /**
     * 设置错误信息
     * @param {string|null} error - 错误信息
     */
    setError(error) {
      this.error = error;
      if (error) {
        logger.error('Store错误:', error);
      }
    },

    /**
     * 清空错误信息
     */
    clearError() {
      this.error = null;
    },

    /**
     * 封装API调用，自动处理加载状态和错误
     * @param {Function} apiCall - API调用函数
     * @param {Object} options - 配置选项
     * @param {boolean} [options.handleLoading=true] - 是否自动处理加载状态
     * @param {boolean} [options.handleError=true] - 是否自动处理错误
     * @returns {Promise<any>} API调用结果
     */
    async callApi(apiCall, options = {}) {
      const { handleLoading = true, handleError = true } = options;

      try {
        if (handleLoading) {
          this.setLoading(true);
        }
        this.clearError();

        const result = await apiCall();
        return result;
      } catch (error) {
        if (handleError) {
          this.setError(error.message || '操作失败');
        }
        throw error;
      } finally {
        if (handleLoading) {
          this.setLoading(false);
        }
      }
    },
  };

  return {
    state,
    getters,
    actions,
  };
}