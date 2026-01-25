import { ref } from 'vue';
import { generateId } from './helpers.js';

/**
 * 模型适配器 - 统一处理模型配置格式
 */
export class ModelAdapter {
  /**
   * 标准化模型配置格式
   * @param {Object} modelConfig - 原始模型配置
   * @returns {Object} 标准化后的模型配置
   */
  static standardizeModelConfig(modelConfig) {
    if (!modelConfig) return null;

    // 标准化模型版本配置
    const standardizedVersions = (modelConfig.versions || []).map(version => ({
      id: version.id || `${modelConfig.name}-${version.version_name}`,
      version_name: version.version_name || version.name || 'default',
      custom_name: version.custom_name || version.display_name || version.version_name || 'Default',
      api_key: version.api_key || version.apiKey || '',
      api_base_url: version.api_base_url || version.apiBaseUrl || '',
      streaming: version.streaming || version.streamingConfig || version.streaming_config || false,
      enabled: version.enabled !== false,
      created_at: version.created_at || version.createdAt || Date.now(),
      updated_at: version.updated_at || version.updatedAt || Date.now()
    }));

    // 标准化模型配置
    return {
      id: modelConfig.id || modelConfig.name,
      name: modelConfig.name || '',
      custom_name: modelConfig.custom_name || modelConfig.display_name || modelConfig.name || '',
      provider: modelConfig.provider || modelConfig.name.split('-')[0] || 'unknown',
      configured: modelConfig.configured !== false,
      enabled: modelConfig.enabled !== false,
      versions: standardizedVersions,
      capabilities: modelConfig.capabilities || ['chat', 'completion'],
      created_at: modelConfig.created_at || modelConfig.createdAt || Date.now(),
      updated_at: modelConfig.updated_at || modelConfig.updatedAt || Date.now()
    };
  }

  /**
   * 标准化模型ID格式
   * @param {string} modelId - 原始模型ID
   * @returns {string} 标准化后的模型ID
   */
  static standardizeModelId(modelId) {
    if (!modelId) return null;

    // 确保模型ID使用name-version_name格式
    if (!modelId.includes('-')) {
      // 旧格式：只包含version_name，需要转换为name-version_name格式
      return `default-${modelId}`;
    }
    return modelId;
  }

  /**
   * 格式化模型显示名称
   * @param {string} modelId - 模型ID
   * @param {Array} models - 模型列表
   * @returns {string} 格式化后的模型显示名称
   */
  static formatModelDisplayName(modelId, models) {
    if (!modelId) return '默认模型';

    // 处理不同的模型ID格式
    const standardizedModelId = ModelAdapter.standardizeModelId(modelId);
    const [modelName, versionName] = standardizedModelId.split('-', 2);

    const model = models.find(m => m.name === modelName);
    if (model && model.versions) {
      const version = model.versions.find(v => v.version_name === versionName);
      if (version) {
        return `${model.custom_name || model.name}-${version.custom_name || version.version_name}`;
      }
    }

    return modelId;
  }
  
  /**
   * 从ID中提取模型信息
   * @param {string} modelId - 模型ID
   * @param {Array} models - 模型列表
   * @returns {Object|null} 包含model和version的对象，或null
   */
  static getModelFromId(modelId, models) {
    if (!modelId || !Array.isArray(models)) return null;
    
    // 标准化模型ID
    const standardizedModelId = ModelAdapter.standardizeModelId(modelId);
    const [modelName, versionName] = standardizedModelId.split('-', 2);
    
    // 查找模型
    const model = models.find(m => m.name === modelName);
    if (!model || !Array.isArray(model.versions)) return null;
    
    // 查找版本
    const version = model.versions.find(v => v.version_name === versionName);
    if (!version) return null;
    
    return { model, version };
  }
  
  /**
   * 检查模型是否支持流式输出
   * @param {string} modelId - 模型ID
   * @param {Array} models - 模型列表
   * @returns {boolean} 是否支持流式输出
   */
  static checkModelStreamingSupport(modelId, models) {
    const modelInfo = ModelAdapter.getModelFromId(modelId, models);
    if (!modelInfo) return false;
    
    const { version } = modelInfo;
    // 支持多种字段名，兼容不同版本的后端返回格式
    return version.streaming || version.streamingConfig || version.streaming_config || false;
  }
}

/**
 * 消息适配器 - 统一处理消息格式
 */
export class MessageAdapter {
  /**
   * 标准化消息格式，统一使用ref包装
   * @param {Object|ref} message - 原始消息
   * @returns {ref} 标准化后的ref包装消息
   */
  static standardizeMessage(message) {
    if (!message) return ref(null);

    // 如果已经是ref对象，直接返回
    if (typeof message.value !== 'undefined') {
      return message;
    }

    // 标准化消息数据
    const standardizedData = {
      id: message.id || generateId('msg'),
      role: message.role || 'ai',
      content: message.content || '',
      timestamp: message.timestamp || Date.now(),
      status: message.status || 'received',
      isTyping: message.isTyping || false,
      model: message.model || '',
      error: message.error || null,
      files: Array.isArray(message.files) ? message.files : [],
      lastUpdate: message.lastUpdate || Date.now(),
      metadata: message.metadata || {}
    };

    // 使用ref包装
    return ref(standardizedData);
  }

  /**
   * 标准化消息列表，统一使用ref包装
   * @param {Array} messages - 原始消息列表
   * @returns {Array} 标准化后的ref包装消息列表
   */
  static standardizeMessageList(messages) {
    if (!Array.isArray(messages)) return [];

    return messages.map(message => MessageAdapter.standardizeMessage(message));
  }
}