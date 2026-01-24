import logger from '../utils/logger.js';

/**
 * API调用封装组合函数，处理API请求的通用逻辑
 * @param {Object} options 配置选项
 * @param {Function} [options.onError] 错误处理回调
 * @param {Function} [options.onSuccess] 成功处理回调
 * @returns {Object} 包含API调用方法的对象
 */
export function useApiCall(options = {}) {
  const { onError, onSuccess } = options;

  /**
   * 封装的API调用方法
   * @param {Function} asyncFn 异步函数，返回Promise
   * @param {Object} callOptions 调用选项
   * @param {boolean} [callOptions.showLoading=true] 是否显示加载状态
   * @param {boolean} [callOptions.handleError=true] 是否自动处理错误
   * @returns {Promise<any>} API调用结果
   */
  const callApi = async (asyncFn, callOptions = {}) => {
    const { showLoading = true, handleError = true } = callOptions;
    let loadingState = null;

    try {
      // 如果提供了状态管理，设置加载状态
      if (options.stateManagement) {
        const { setLoading, clearError } = options.stateManagement;
        if (showLoading) setLoading(true);
        clearError();
        loadingState = options.stateManagement;
      }

      // 调用异步函数
      const result = await asyncFn();

      // 调用成功回调
      if (onSuccess) {
        onSuccess(result);
      }

      return result;
    } catch (error) {
      logger.error('API调用失败:', error);

      // 处理错误
      if (handleError) {
        // 调用错误回调
        if (onError) {
          onError(error);
        } 
        // 如果提供了状态管理，设置错误信息
        else if (loadingState) {
          loadingState.setError(error.message || 'API调用失败');
        }
      }

      throw error;
    } finally {
      // 重置加载状态
      if (loadingState && showLoading) {
        loadingState.setLoading(false);
      }
    }
  };

  return {
    callApi
  };
}
