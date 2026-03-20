import { defineStore } from 'pinia';
import { StorageManager } from '../utils/storage.js';
import { mergeSettings } from '../utils/data.js';
import { apiService } from '../services/apiService.js';
import { eventBus } from '../services/eventBus.js';
import { showNotification } from '../utils/notificationUtils.js';
import { errorUtils, loadingUtils, notificationUtils as notifyUtils, apiUtils } from '../utils/storeUtils.js';

// 存储键名常量
const STORAGE_KEYS = {
  SETTINGS: 'userSettings',
  LAST_USED: 'lastUsedSettings',
  MODEL_SETTINGS: 'modelSettings',
};

// 定义RAG配置的类型描述
/**
 * @typedef {Object} RagConfig
 * @property {boolean} enabled - 是否启用
 * @property {number} chunk_size - 分块大小
 * @property {number} chunk_overlap - 重叠大小
 * @property {number} k - 检索数量
 * @property {string} retrievalMode - 文档检索模式
 * @property {number} topK - 检索文档数量
 * @property {number} scoreThreshold - 检索相关性阈值
 * @property {string} embedderModel - Embedder模型
 * @property {string} vectorDbPath - 向量数据库路径
 * @property {string} knowledgeBasePath - 知识库存储路径
 */

// 定义系统设置的类型描述
/**
 * @typedef {Object} SystemSettings
 * @property {boolean} darkMode - 深色模式
 * @property {boolean} streamingEnabled - 启用流式输出
 * @property {string} chatStyle - 聊天样式，可选值：'bubble' 或 'document'
 * @property {string} defaultModel - 默认模型
 * @property {string} viewMode - 视图模式
 */

// 定义模型参数的类型描述
/**
 * @typedef {Object} ModelParams
 * @property {number} temperature - 温度参数
 * @property {number} max_tokens - 最大生成token数
 * @property {number} top_p - 采样参数
 * @property {number} top_k - 采样参数
 * @property {number} frequency_penalty - 频率惩罚
 */

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // 通知相关设置
    notificationsConfig: {
      newMessage: true,
      sound: true,
      system: true,
      displayTime: '5秒',
    },

    // 系统设置
    systemSettings: {
      darkMode: false,
      streamingEnabled: true,
      chatStyle: 'bubble',
      viewMode: 'grid',
    },

    // 初始设置值，用于比较修改
    initialSettings: null,

    // 模型相关设置
    availableModels: [],
    models: [],
    modelParams: {
      temperature: 0.7,
      max_tokens: 2000,
      top_p: 1.0,
      top_k: 50,
      frequency_penalty: 1.0,
    },
    
    // 模型加载状态
    modelLoading: false,
    // 模型错误信息
    modelError: null,

    // 嵌入模型相关设置
    embeddingModels: [],
    embeddingModelLoading: false,
    embeddingModelError: null,
  }),

  getters: {
    // 获取当前系统设置
    currentSystemSettings: (state) => state.systemSettings,

    // 获取当前通知配置
    currentNotificationsConfig: (state) => state.notificationsConfig,

    // 获取当前模型的参数
    currentModelParams: (state) => state.modelParams,
    
    // 获取可用模型列表
    availableModelList: (state) => state.availableModels,
    
    // 获取所有模型配置
    allModels: (state) => state.models,
    
    // 获取已配置的模型列表
    configuredModels: (state) => state.models.filter(model => model.configured),
    
    // 获取未配置的模型列表
    unconfiguredModels: (state) => state.models.filter(model => !model.configured),
    
    // 获取默认模型
    defaultModel: (state) => state.models.find(model => model.is_default),

    // 获取模型加载状态
    isModelLoading: (state) => state.modelLoading,

    // 获取模型错误
    currentModelError: (state) => state.modelError,

    // 获取所有嵌入模型
    allEmbeddingModels: (state) => state.embeddingModels,
    
    // 获取已配置的嵌入模型
    configuredEmbeddingModels: (state) => state.embeddingModels.filter(model => model.configured),
    
    // 获取未配置的嵌入模型
    unconfiguredEmbeddingModels: (state) => state.embeddingModels.filter(model => !model.configured),
    
    // 获取嵌入模型加载状态
    isEmbeddingModelLoading: (state) => state.embeddingModelLoading,
    
    // 获取嵌入模型错误
    currentEmbeddingModelError: (state) => state.embeddingModelError,
  },

  actions: {
    // 初始化设置监听
    initSettingsWatch() {
      // 简化实现：设置保存和应用通过组件内的watch和@change事件处理
    },
    
    // 注册事件总线监听器
    registerEventListeners() {
      // 监听获取模型列表的请求
      eventBus.on('getModels', (data) => {
        if (data && data.callback) {
          data.callback(this.models);
        }
      });
      
      // 监听获取系统设置的请求
      eventBus.on('getSystemSettings', (data) => {
        if (data && data.callback) {
          data.callback(this.systemSettings);
        }
      });
      
      // 监听获取当前模型参数的请求
      eventBus.on('getCurrentModelParams', (data) => {
        if (data && data.callback) {
          data.callback(this.modelParams);
        }
      });
    },
    


    // 更新通知配置
    updateNotificationsConfig(config) {
      this.notificationsConfig = { ...this.notificationsConfig, ...config };
      this.saveSettings();
    },

    // 切换暗黑模式
    toggleDarkMode() {
      this.systemSettings.darkMode = !this.systemSettings.darkMode;
      this.applyDarkMode();
      this.saveSettings();
    },

    // 应用暗黑模式
    applyDarkMode() {
      if (this.systemSettings.darkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },

    // 更新系统设置
    updateSystemSettings(settings) {
      this.systemSettings = { ...this.systemSettings, ...settings };

      // 特殊处理需要立即应用的设置
      this.applyImmediateSettings(settings);

      this.saveSettings();
    },

    // 应用需要立即生效的设置
    applyImmediateSettings(settings) {
      // 总是应用darkMode设置，确保立即生效
      this.applyDarkMode();
    },

    // 重置设置为默认值
    resetSettings() {
      this.notificationsConfig = {
        newMessage: true,
        sound: true,
        system: true,
        displayTime: '5秒',
      };

      this.systemSettings = {
        darkMode: false,
        streamingEnabled: true,
        chatStyle: 'bubble',
        viewMode: 'grid',
      };

      this.modelParams = {
        temperature: 0.7,
        max_tokens: 2000,
        top_p: 1.0,
        top_k: 50,
        frequency_penalty: 1.0,
      };

      this.availableModels = [];
      this.modelError = null;

      this.applyDarkMode();
      this.saveSettings();
      this.saveModelSettings();
    },

    // 从后端API加载设置
    async loadSettingsFromApi() {
      try {
        // 加载系统设置（包含通知设置）
        const systemSettings = await apiService.get('/settings/system');
        if (systemSettings) {
          // 更新系统设置，转换字段名以匹配前端模型
          const updatedSystemSettings = {
            darkMode: systemSettings.dark_mode,
            chatStyle: systemSettings.chat_style,
            viewMode: systemSettings.view_mode,
            streamingEnabled: systemSettings.streaming_enabled
          };
          this.systemSettings = { ...this.systemSettings, ...updatedSystemSettings };
          
          // 更新通知设置
          const updatedNotificationsConfig = {
            newMessage: systemSettings.newMessage,
            sound: systemSettings.sound,
            system: systemSettings.system,
            displayTime: systemSettings.displayTime
          };
          this.notificationsConfig = { ...this.notificationsConfig, ...updatedNotificationsConfig };
        }
        
        // 加载模型列表
        await this.loadModels();
        
        // 加载嵌入模型列表（新增）
        await this.loadEmbeddingModels();
        
        // 保存初始设置值，用于后续比较修改
        this.initialSettings = {
          // 系统设置
          dark_mode: this.systemSettings.darkMode,
          chat_style: this.systemSettings.chatStyle,
          view_mode: this.systemSettings.viewMode,
          streaming_enabled: this.systemSettings.streamingEnabled,
          // 通知设置
          newMessage: this.notificationsConfig.newMessage,
          sound: this.notificationsConfig.sound,
          system: this.notificationsConfig.system,
          displayTime: this.notificationsConfig.displayTime
        };
      } catch (error) {
        console.error('从后端加载设置失败:', error);
      }
    },

    // 仅从存储中加载设置，不请求API
    async loadSettingsFromStorageOnly() {
      try {
        // 只从localStorage加载设置，不请求API
        const savedSettings = StorageManager.getItem(STORAGE_KEYS.SETTINGS);
        if (savedSettings) {
          this.mergeSavedSettings(savedSettings);
        }

        // 加载模型设置
        this.loadModelSettings();

        // 应用保存的设置
        this.applyDarkMode();

        // 记录最后使用时间
        this.updateLastUsedTime();
      } catch (error) {
        console.error('仅从存储加载设置失败:', error);
        // 加载失败时使用默认设置
        this.resetSettings();
      }
    },

    // 从存储中加载设置（包含API请求）
    async loadSettings() {
      try {
        // 先从localStorage加载设置
        const savedSettings = StorageManager.getItem(STORAGE_KEYS.SETTINGS);
        if (savedSettings) {
          this.mergeSavedSettings(savedSettings);
        }
        
        // 加载模型设置
        this.loadModelSettings();
        
        // 再从后端API加载最新设置，覆盖localStorage的设置
        await this.loadSettingsFromApi();

        // 应用保存的设置
        this.applyDarkMode();

        // 记录最后使用时间
        this.updateLastUsedTime();
      } catch (error) {
        console.error('加载设置失败:', error);
        // 加载失败时使用默认设置
        this.resetSettings();
      }
    },

    // 合并保存的设置
    mergeSavedSettings(savedSettings) {
      if (savedSettings.notificationsConfig && typeof savedSettings.notificationsConfig === 'object') {
        this.notificationsConfig = mergeSettings(this.notificationsConfig, savedSettings.notificationsConfig);
      }

      if (savedSettings.systemSettings && typeof savedSettings.systemSettings === 'object') {
        this.systemSettings = mergeSettings(this.systemSettings, savedSettings.systemSettings);
      }
    },

    // 更新最后使用时间
    updateLastUsedTime() {
      try {
        StorageManager.setItem(STORAGE_KEYS.LAST_USED, {
          timestamp: Date.now(),
        });
      } catch (error) {
        console.error('更新最后使用时间失败:', error);
      }
    },

    // 保存设置到后端API
    async saveSettingsToApi() {
      try {
        // 构建完整的设置对象
        const currentSettings = {
          // 系统设置
          dark_mode: this.systemSettings.darkMode,
          chat_style: this.systemSettings.chatStyle,
          view_mode: this.systemSettings.viewMode,
          streaming_enabled: this.systemSettings.streamingEnabled,
          // 通知设置
          newMessage: this.notificationsConfig.newMessage,
          sound: this.notificationsConfig.sound,
          system: this.notificationsConfig.system,
          displayTime: this.notificationsConfig.displayTime
        };
        
        // 与初始设置比较，只保留修改的字段
        const changedSettings = {};
        for (const [key, value] of Object.entries(currentSettings)) {
          if (this.initialSettings && this.initialSettings[key] !== value) {
            changedSettings[key] = value;
          }
        }
        
        // 如果没有修改的字段，直接返回
        if (Object.keys(changedSettings).length === 0) {
          console.log('没有修改的设置，跳过保存');
          return;
        }
        
        // 发送修改的字段
        console.log('保存修改的设置:', changedSettings);
        await apiService.patch('/settings/system', changedSettings);
        
        // 更新初始设置值，以便下次比较
        this.initialSettings = { ...currentSettings };
      } catch (error) {
        console.error('保存设置到后端失败:', error);
      }
    },

    // 保存设置的核心功能
    async _saveSettingsCore() {
      try {
        const settingsToSave = {
          notificationsConfig: this.notificationsConfig,
          systemSettings: this.systemSettings,
          timestamp: Date.now(),
        };

        // 保存到localStorage
        const saved = StorageManager.setItem(STORAGE_KEYS.SETTINGS, settingsToSave);
        
        // 保存到后端API
        await this.saveSettingsToApi();
        
        if (saved) {
          // 记录最后保存时间
          this.updateLastUsedTime();
        }
        
        return saved;
      } catch (error) {
        console.error('保存设置失败:', error);
        return false;
      }
    },

    // 防抖保存设置
    saveSettings: async function() {
      // 直接调用核心保存功能，确保this上下文正确
      return await this._saveSettingsCore();
    },

    // 模型管理相关操作
    // 设置模型加载状态
    setModelLoading(loading) {
      this.modelLoading = loading;
    },
    
    // 设置模型错误信息
    setModelError(error) {
      errorUtils.setError(this, error);
      if (error) {
        console.error('模型管理错误:', error);
      }
    },
    
    // 选择模型（仅同步到本地存储，主要通过settingsStore管理）
    selectModel(model) {
      if (this.availableModels.includes(model)) {
        // 此处保留方法以确保向后兼容性
        this.saveModelSettings();
      }
    },

    // 更新模型参数
    updateModelParams(params) {
      this.modelParams = { ...this.modelParams, ...params };
      this.saveModelSettings();
    },

    // 包装模型API调用
    async _wrapModelApiCall(apiCall, options = {}) {
      return await apiUtils.wrapApiCall(this, apiCall, {
        loadingProperty: 'modelLoading',
        errorProperty: 'modelError',
        ...options
      });
    },

    // 包装嵌入模型API调用
    async _wrapEmbeddingModelApiCall(apiCall, options = {}) {
      return await apiUtils.wrapApiCall(this, apiCall, {
        loadingProperty: 'embeddingModelLoading',
        errorProperty: 'embeddingModelError',
        ...options
      });
    },

    // 从后端加载模型列表
    async loadModels() {
      await this._wrapModelApiCall(async () => {
        // 从后端加载模型列表
        const response = await apiService.models.getModels();
        // 确保models是数组
        this.models = Array.isArray(response.models) ? response.models : [];
        
        // 更新可用模型列表
        this.updateAvailableModels();
        
        // 通知事件总线，模型列表已更新
        eventBus.emit('modelsLoaded', { models: this.models });
      }, {
        errorMessage: '加载模型列表失败'
      });
    },

    // 更新模型数据，添加图标URL
    updateModelsWithIcons(configuredModels, unconfiguredModels) {
      // 首先更新已配置模型
      const updatedModels = [...this.models];
      
      // 更新已配置模型
      configuredModels.forEach(configuredModel => {
        const index = updatedModels.findIndex(m => m.name === configuredModel.name);
        if (index !== -1) {
          updatedModels[index] = configuredModel;
        }
      });
      
      // 更新未配置模型
      unconfiguredModels.forEach(unconfiguredModel => {
        const index = updatedModels.findIndex(m => m.name === unconfiguredModel.name);
        if (index !== -1) {
          updatedModels[index] = unconfiguredModel;
        }
      });
      
      // 更新store中的models状态
      this.models = updatedModels;
      
      // 更新可用模型列表
      this.updateAvailableModels();
    },
    
    // 更新可用模型列表，与select组件保持一致的模型ID格式
    updateAvailableModels() {
      const available = [];
      
      this.models.forEach(model => {
        if (model.configured && model.versions) {
          model.versions.forEach(version => {
            if (version && version.version_name) {
              // 检查是否是默认模型版本
              const isDefaultVersion = model.is_default && model.default_version === version.version_name;
              // 包含启用的版本或默认版本
              if (version.enabled || isDefaultVersion) {
                // 与select组件保持一致：只使用version_name构建模型标识
                // 格式：model.name-version_name
                available.push(`${model.name}-${version.version_name}`);
              }
            }
          });
        }
      });
      
      this.availableModels = available;
    },

    // 保存模型配置
    async saveModelConfig(modelName, config) {
      await this._wrapModelApiCall(async () => {
        // 调用后端API保存配置
        await apiService.post(`/models/${modelName}`, {
          custom_name: config.customName,
          api_key: config.apiKey,
          api_base_url: config.apiBaseUrl,
          version_name: config.versionName,
          streaming_config: config.streamingConfig
        });
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
      }, {
        errorMessage: '保存模型配置失败'
      });
      
      return true;
    },

    // 删除模型配置
    async deleteModelConfig(modelName) {
      await this._wrapModelApiCall(async () => {
        // 调用后端API删除配置
        await apiService.delete(`/models/${modelName}`);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
      }, {
        errorMessage: '删除模型配置失败',
        successMessage: `已删除${modelName}的配置`,
        showSuccessNotification: true,
        showErrorNotification: true
      });
      
      return true;
    },

    // 切换模型启用状态
    async toggleModelEnabled(modelName, enabled) {
      await this._wrapModelApiCall(async () => {
        // 调用后端API更新启用状态
        await apiService.patch(`/models/${modelName}/enabled`, {
          enabled: enabled
        });
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
      }, {
        errorMessage: '更新模型启用状态失败'
      });
      
      return true;
    },

    // 添加模型版本
    async addModelVersion(modelName, versionConfig) {
      await this._wrapModelApiCall(async () => {
        // 构建请求数据
        const modelConfig = {
          custom_name: versionConfig.customName,
          api_key: versionConfig.apiKey,
          api_base_url: versionConfig.apiBaseUrl,
          version_name: versionConfig.versionName,
          streaming_config: versionConfig.streamingConfig,
          enabled: true // 新添加的版本默认启用
        };
        
        console.log('发送的API请求数据:', JSON.stringify(modelConfig));
        
        // 调用后端API保存配置
        await apiService.post(`/models/${modelName}`, modelConfig);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
      }, {
        errorMessage: '添加模型版本失败'
      });
      
      return true;
    },

    // 编辑模型版本
    async updateModelVersion(modelName, versionName, versionConfig) {
      await this._wrapModelApiCall(async () => {
        // 构建请求数据
        const requestData = {
          custom_name: versionConfig.customName,
          api_key: versionConfig.apiKey,
          api_base_url: versionConfig.apiBaseUrl,
          version_name: versionConfig.versionName,
          streaming_config: versionConfig.streamingConfig,
          enabled: versionConfig.enabled !== false // 编辑时保持原有启用状态，默认启用
        };
        
        // 调用API保存配置
        await apiService.post(`/models/${modelName}`, requestData);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
      }, {
        errorMessage: '更新模型版本失败'
      });
      
      return true;
    },

    // 删除模型版本
    async deleteModelVersion(modelName, versionName) {
      // 查找模型和版本信息用于通知
      const model = this.models.find(m => m.name === modelName);
      const version = model?.versions?.find(v => v.version_name === versionName);
      const versionNameForNotification = version?.custom_name || versionName;
      
      await this._wrapModelApiCall(async () => {
        // 调用后端API删除模型版本
        await apiService.delete(`/models/${modelName}/versions/${versionName}`);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
      }, {
        errorMessage: '删除模型版本失败',
        successMessage: `已删除${modelName}的版本 ${versionNameForNotification}`,
        showSuccessNotification: true,
        showErrorNotification: true
      });
      
      return true;
    },

    // 设置默认模型版本
    async setDefaultModelVersion(modelName, versionName) {
      // 查找模型和版本信息用于通知
      const model = this.models.find(m => m.name === modelName);
      const version = model?.versions?.find(v => v.version_name === versionName);
      const versionNameForNotification = version?.custom_name || versionName;
      
      await this._wrapModelApiCall(async () => {
        // 调用后端API设置默认模型版本
        await apiService.patch(`/models/${modelName}/versions/${versionName}/default`);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
      }, {
        errorMessage: '设置默认模型版本失败',
        successMessage: `已将${modelName}的版本 ${versionNameForNotification} 设置为默认`,
        showSuccessNotification: true,
        showErrorNotification: true
      });
    },

    // 设置默认嵌入模型版本
    async setDefaultEmbeddingModelVersion(modelName, versionName) {
      // 查找模型和版本信息用于通知
      const model = this.embeddingModels.find(m => m.name === modelName);
      const version = model?.versions?.find(v => v.version_name === versionName);
      const versionNameForNotification = version?.custom_name || versionName;
      
      await this._wrapModelApiCall(async () => {
        // 调用后端API设置默认嵌入模型版本
        await apiService.put(`/embedding-models/${modelName}/versions/${versionName}/default`);
        
        // 重新加载模型列表以更新状态
        await this.loadEmbeddingModels();
      }, {
        errorMessage: '设置默认嵌入模型版本失败',
        successMessage: `已将${modelName}的版本 ${versionNameForNotification} 设置为默认`,
        showSuccessNotification: true,
        showErrorNotification: true
      });
    },

    // 重置模型设置为默认值
    resetModelSettings() {
      this.modelParams = {
        temperature: 0.7,
        max_tokens: 2000,
        top_p: 1.0,
        top_k: 50,
        frequency_penalty: 1.0,
      };
      this.availableModels = [];
      this.modelError = null;
      this.saveModelSettings();
    },

    // 从存储中加载模型设置
    loadModelSettings() {
      try {
        const savedSettings = StorageManager.getItem(STORAGE_KEYS.MODEL_SETTINGS);
        if (savedSettings) {
          this.mergeSavedModelSettings(savedSettings);
        }
      } catch (error) {
        console.error('加载模型设置失败:', error);
        // 加载失败时使用默认设置
        this.resetModelSettings();
      }
    },

    // 合并保存的模型设置
    mergeSavedModelSettings(savedSettings) {
      if (savedSettings.modelParams && typeof savedSettings.modelParams === 'object') {
        this.modelParams = mergeSettings(this.modelParams, savedSettings.modelParams);
      }
    },

    // 保存模型设置的核心功能
    _saveModelSettingsCore: function() {
      try {
        const settingsToSave = {
          modelParams: this.modelParams,
          timestamp: Date.now(),
        };

        const saved = StorageManager.setItem(STORAGE_KEYS.MODEL_SETTINGS, settingsToSave);
        return saved;
      } catch (error) {
        console.error('保存模型设置失败:', error);
        return false;
      }
    },

    // 保存模型设置
    saveModelSettings: function() {
      return this._saveModelSettingsCore();
    },

    // 加载嵌入模型列表
    async loadEmbeddingModels() {
      await this._wrapEmbeddingModelApiCall(async () => {
        // 从后端加载嵌入模型列表
        const response = await apiService.embeddingModels.getModels();
        // 确保models是数组
        this.embeddingModels = Array.isArray(response.models) ? response.models : [];
        
        // 通知事件总线，嵌入模型列表已更新
        eventBus.emit('embeddingModelsLoaded', { models: this.embeddingModels });
      }, {
        errorMessage: '加载嵌入模型列表失败'
      });
    },

    // 更新嵌入模型数据，添加图标URL和type属性
    updateEmbeddingModelsWithIcons(configuredModels, unconfiguredModels) {
      // 首先更新已配置模型
      const updatedModels = [...this.embeddingModels];
      
      // 更新已配置模型，添加type: 'embedding'属性
      configuredModels.forEach(configuredModel => {
        const index = updatedModels.findIndex(m => m.name === configuredModel.name);
        if (index !== -1) {
          updatedModels[index] = {
            ...configuredModel,
            type: 'embedding' // 添加type属性，用于前端区分模型类型
          };
        }
      });
      
      // 更新未配置模型，添加type: 'embedding'属性
      unconfiguredModels.forEach(unconfiguredModel => {
        const index = updatedModels.findIndex(m => m.name === unconfiguredModel.name);
        if (index !== -1) {
          updatedModels[index] = {
            ...unconfiguredModel,
            type: 'embedding' // 添加type属性，用于前端区分模型类型
          };
        }
      });
      
      // 更新store中的embeddingModels状态
      this.embeddingModels = updatedModels;
    },

    // 保存嵌入模型配置
    async saveEmbeddingModelConfig(modelName, config) {
      await this._wrapEmbeddingModelApiCall(async () => {
        // 调用后端API保存配置
        await apiService.post(`/embedding-models/${modelName}`, {
          custom_name: config.customName,
          api_key: config.apiKey,
          api_base_url: config.apiBaseUrl,
          version_name: config.versionName,
          model_path: config.modelPath,
          dimension: config.dimension
        });
        
        // 重新加载嵌入模型列表以更新状态
        await this.loadEmbeddingModels();
      }, {
        errorMessage: '保存嵌入模型配置失败'
      });
      
      return true;
    },

    // 删除嵌入模型配置
    async deleteEmbeddingModelConfig(modelName) {
      await this._wrapEmbeddingModelApiCall(async () => {
        // 调用后端API删除配置
        await apiService.delete(`/embedding-models/${modelName}`);
        
        // 重新加载嵌入模型列表以更新状态
        await this.loadEmbeddingModels();
      }, {
        errorMessage: '删除嵌入模型配置失败',
        successMessage: `已删除${modelName}的配置`,
        showSuccessNotification: true,
        showErrorNotification: true
      });
      
      return true;
    },

    // 切换嵌入模型启用状态
    async toggleEmbeddingModelEnabled(modelName, enabled) {
      await this._wrapEmbeddingModelApiCall(async () => {
        // 调用后端API更新启用状态
        await apiService.post(`/embedding-models/${modelName}/enabled`, {
          enabled: enabled
        });
        
        // 重新加载嵌入模型列表以更新状态
        await this.loadEmbeddingModels();
      }, {
        errorMessage: '更新嵌入模型启用状态失败'
      });
      
      return true;
    },

    // 删除嵌入模型版本
    async deleteEmbeddingModelVersion(modelName, versionName) {
      await this._wrapEmbeddingModelApiCall(async () => {
        // 调用后端API删除模型版本
        await apiService.delete(`/embedding-models/${modelName}/versions/${versionName}`);
        
        // 重新加载嵌入模型列表以更新状态
        await this.loadEmbeddingModels();
      }, {
        errorMessage: '删除嵌入模型版本失败',
        successMessage: `已删除${modelName}的版本 ${versionName}`,
        showSuccessNotification: true,
        showErrorNotification: true
      });
      
      return true;
    },
  },
});
