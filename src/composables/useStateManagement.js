import { ref, computed } from 'vue';

/**
 * 通用状态管理组合函数，处理loading和error状态
 * @returns {Object} 包含状态和方法的对象
 */
export function useStateManagement() {
  // 状态
  const loading = ref(false);
  const error = ref(null);

  // 计算属性
  const isLoading = computed(() => loading.value);
  const getError = computed(() => error.value);

  // 方法
  const setLoading = (value) => {
    loading.value = value;
  };

  const setError = (message) => {
    error.value = message;
  };

  const clearError = () => {
    error.value = null;
  };

  const resetState = () => {
    loading.value = false;
    error.value = null;
  };

  return {
    // 状态
    loading,
    error,
    
    // 计算属性
    isLoading,
    getError,
    
    // 方法
    setLoading,
    setError,
    clearError,
    resetState
  };
}
