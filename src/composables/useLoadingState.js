import { ref, computed } from 'vue';
import { useUiStore } from '../store/uiStore.js';
import { useSettingsStore } from '../store/settingsStore.js';

/**
 * 加载状态管理组合函数
 * 用于管理应用的加载状态、错误状态等
 */
export function useLoadingState() {
  const uiStore = useUiStore();
  const settingsStore = useSettingsStore();
  
  // 局部加载状态
  const isLocalLoading = ref(false);
  
  // 局部错误状态
  const localError = ref(null);
  
  // 计算属性：全局加载状态
  const isGlobalLoading = computed(() => uiStore.isLoading);
  
  // 计算属性：UI 错误状态
  const uiError = computed(() => uiStore.uiError);
  
  // 计算属性：模型加载状态
  const isModelLoading = computed(() => settingsStore.isModelLoading);
  
  // 计算属性：模型错误状态
  const modelError = computed(() => settingsStore.currentModelError);
  
  // 方法：设置局部加载状态
  const setLocalLoading = (loading) => {
    isLocalLoading.value = loading;
  };
  
  // 方法：设置局部错误
  const setLocalError = (error) => {
    localError.value = error;
  };
  
  // 方法：清除局部错误
  const clearLocalError = () => {
    localError.value = null;
  };
  
  // 方法：设置全局加载状态
  const setGlobalLoading = (loading) => {
    uiStore.setLoading(loading);
  };
  
  // 方法：设置 UI 错误
  const setUiError = (error) => {
    uiStore.setUiError(error);
  };
  
  // 方法：清除 UI 错误
  const clearUiError = () => {
    uiStore.clearUiError();
  };
  
  // 方法：执行带加载状态的异步操作
  const withLoading = async (asyncFunction, options = {}) => {
    const {
      global = false, // 是否使用全局加载状态
      model = false, // 是否使用模型加载状态
      onError = null // 错误处理函数
    } = options;
    
    try {
      // 设置加载状态
      if (global) {
        setGlobalLoading(true);
      } else if (model) {
        settingsStore.setModelLoading(true);
      } else {
        setLocalLoading(true);
      }
      
      // 执行异步操作
      const result = await asyncFunction();
      
      // 清除错误状态
      if (global) {
        clearUiError();
      } else if (model) {
        settingsStore.setModelError(null);
      } else {
        clearLocalError();
      }
      
      return result;
    } catch (error) {
      // 处理错误
      if (onError) {
        onError(error);
      } else {
        console.error('操作失败:', error);
      }
      
      // 设置错误状态
      if (global) {
        setUiError(error.message || '操作失败');
      } else if (model) {
        settingsStore.setModelError(error.message || '模型操作失败');
      } else {
        setLocalError(error.message || '操作失败');
      }
      
      throw error;
    } finally {
      // 清除加载状态
      if (global) {
        setGlobalLoading(false);
      } else if (model) {
        settingsStore.setModelLoading(false);
      } else {
        setLocalLoading(false);
      }
    }
  };
  
  return {
    // 状态
    isLocalLoading,
    localError,
    isGlobalLoading,
    uiError,
    isModelLoading,
    modelError,
    
    // 方法
    setLocalLoading,
    setLocalError,
    clearLocalError,
    setGlobalLoading,
    setUiError,
    clearUiError,
    withLoading,
  };
}
