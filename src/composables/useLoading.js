import { ref } from 'vue';
import logger from '../utils/logger.js';

/**
 * 加载状态管理Hook
 * @param {Object} options 配置选项
 * @param {boolean} options.initialLoading 初始加载状态
 * @param {Function} options.onStart 加载开始回调
 * @param {Function} options.onEnd 加载结束回调
 * @returns {Object} 加载状态管理对象
 */
export function useLoading(options = {}) {
  const {
    initialLoading = false,
    onStart,
    onEnd
  } = options;

  // 加载状态
  const isLoading = ref(initialLoading);
  
  // 加载计数，用于处理并发请求
  const loadingCount = ref(0);

  // 开始加载
  const startLoading = () => {
    loadingCount.value++;
    isLoading.value = true;
    
    if (onStart) {
      onStart();
    }
  };

  // 结束加载
  const endLoading = () => {
    if (loadingCount.value > 0) {
      loadingCount.value--;
      
      if (loadingCount.value === 0) {
        isLoading.value = false;
        
        if (onEnd) {
          onEnd();
        }
      }
    }
  };

  // 切换加载状态
  const toggleLoading = () => {
    if (isLoading.value) {
      endLoading();
    } else {
      startLoading();
    }
  };

  // 执行异步函数并自动管理加载状态
  const withLoading = async (asyncFn, options = {}) => {
    const {
      showLoading = true,
      onSuccess,
      onError
    } = options;

    if (showLoading) {
      startLoading();
    }

    try {
      const result = await asyncFn();
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      return result;
    } catch (error) {
      if (onError) {
        onError(error);
      } else {
        logger.error('Error in withLoading:', error);
      }
      
      throw error;
    } finally {
      if (showLoading) {
        endLoading();
      }
    }
  };

  return {
    isLoading,
    loadingCount,
    startLoading,
    endLoading,
    toggleLoading,
    withLoading
  };
}