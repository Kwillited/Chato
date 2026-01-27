import { showNotification } from './notificationUtils.js';

/**
 * 错误处理工具函数
 */
export const errorUtils = {
  /**
   * 设置错误信息
   * @param {Object} state - store 状态对象
   * @param {string} message - 错误信息
   */
  setError(state, message) {
    state.error = message;
  },

  /**
   * 清除错误信息
   * @param {Object} state - store 状态对象
   */
  clearError(state) {
    state.error = null;
  }
};

/**
 * 加载状态管理工具函数
 */
export const loadingUtils = {
  /**
   * 设置加载状态为 true
   * @param {Object} state - store 状态对象
   */
  setLoading(state) {
    state.loading = true;
  },

  /**
   * 设置加载状态为 false
   * @param {Object} state - store 状态对象
   */
  setLoadingFalse(state) {
    state.loading = false;
  },

  /**
   * 开始加载操作（设置加载状态为 true 并清除错误）
   * @param {Object} state - store 状态对象
   */
  startLoading(state) {
    state.loading = true;
    if (errorUtils.clearError) {
      errorUtils.clearError(state);
    }
  }
};

/**
 * 通知工具函数
 */
export const notificationUtils = {
  /**
   * 显示成功通知
   * @param {string} message - 通知消息
   */
  showSuccess(message) {
    showNotification(message, 'success');
  },

  /**
   * 显示错误通知
   * @param {string} message - 通知消息
   */
  showError(message) {
    showNotification(message, 'error');
  }
};

/**
 * API 调用工具函数
 */
export const apiUtils = {
  /**
   * 包装 API 调用，处理错误和加载状态
   * @param {Object} state - store 状态对象
   * @param {Function} apiCall - API 调用函数
   * @param {string} errorMessage - 错误消息前缀
   * @returns {Promise<any>} API 调用结果
   */
  async wrapApiCall(state, apiCall, errorMessage = '操作失败') {
    loadingUtils.startLoading(state);

    try {
      const response = await apiCall();
      loadingUtils.setLoadingFalse(state);
      return response;
    } catch (error) {
      console.error(`${errorMessage}:`, error);
      errorUtils.setError(state, `${errorMessage}: ${error.message || '未知错误'}`);
      loadingUtils.setLoadingFalse(state);
      throw error;
    }
  }
};

/**
 * 状态更新工具函数
 */
export const stateUtils = {
  /**
   * 强制更新对象，确保响应式系统能够检测到变化
   * @param {Object} store - store 实例
   * @param {string} property - 要更新的属性名
   * @param {any} value - 新值
   */
  forceUpdate(store, property, value) {
    store[property] = { ...value };
  }
};
