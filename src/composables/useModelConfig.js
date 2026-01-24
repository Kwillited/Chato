import { ref, computed, watch } from 'vue';
import { useSettingsStore } from '../store/settingsStore.js';
import { ModelAdapter } from '../utils/modelAdapter.js';
import logger from '../utils/logger.js';

/**
 * 模型配置管理组合函数，统一处理模型相关逻辑
 * @returns {Object} 包含模型配置和方法的对象
 */
export function useModelConfig() {
  const settingsStore = useSettingsStore();
  const modelAdapter = new ModelAdapter();

  // 响应式状态
  const selectedModel = ref(null);
  const modelList = ref([]);

  // 计算属性
  const configuredModels = computed(() => {
    return settingsStore.configuredModels || [];
  });

  const availableModels = computed(() => {
    return modelList.value.filter(model => model.enabled !== false);
  });

  /**
   * 加载模型列表
   */
  const loadModels = async () => {
    try {
      await settingsStore.loadModels();
      modelList.value = settingsStore.configuredModels || [];
      return modelList.value;
    } catch (error) {
      logger.error('加载模型列表失败:', error);
      throw error;
    }
  };

  /**
   * 根据模型ID获取模型信息
   * @param {string} modelId - 模型ID
   * @returns {Object|null} 模型信息
   */
  const getModelById = (modelId) => {
    return modelAdapter.getModelFromId(modelId);
  };

  /**
   * 检查模型是否支持流式输出
   * @param {string|Object} model - 模型ID或模型对象
   * @returns {boolean} 是否支持流式输出
   */
  const checkStreamingSupport = (model) => {
    return modelAdapter.checkModelStreamingSupport(model);
  };

  /**
   * 标准化模型ID
   * @param {string} modelId - 模型ID
   * @returns {string} 标准化后的模型ID
   */
  const standardizeModelId = (modelId) => {
    return modelAdapter.standardizeModelId(modelId);
  };

  /**
   * 设置选中的模型
   * @param {string|Object} model - 模型ID或模型对象
   */
  const setSelectedModel = (model) => {
    if (typeof model === 'string') {
      selectedModel.value = getModelById(model) || model;
    } else {
      selectedModel.value = model;
    }
  };

  /**
   * 获取模型的默认参数
   * @param {string|Object} model - 模型ID或模型对象
   * @returns {Object} 模型默认参数
   */
  const getModelDefaultParams = (model) => {
    const modelInfo = typeof model === 'string' ? getModelById(model) : model;
    if (!modelInfo) {
      return {};
    }
    
    return {
      temperature: modelInfo.temperature || 0.7,
      top_p: modelInfo.top_p || 0.9,
      max_tokens: modelInfo.max_tokens || 1000,
      stream: modelInfo.streaming_config || false
    };
  };

  // 监听配置模型变化，自动更新模型列表
  watch(
    () => settingsStore.configuredModels,
    (newModels) => {
      modelList.value = newModels || [];
    },
    { deep: true }
  );

  return {
    // 响应式状态
    selectedModel,
    modelList,
    
    // 计算属性
    configuredModels,
    availableModels,
    
    // 方法
    loadModels,
    getModelById,
    checkStreamingSupport,
    standardizeModelId,
    setSelectedModel,
    getModelDefaultParams
  };
}
