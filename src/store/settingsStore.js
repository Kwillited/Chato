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
 * @property {string} vectorDbType - 向量数据库类型
 * @property {string} knowledgeBasePath - 知识库存储路径
 */

// 定义系统设置的类型描述
/**
 * @typedef {Object} SystemSettings
 * @property {boolean} darkMode - 深色模式
 * @property {number} fontSize - 字体大小
 * @property {string} fontFamily - 字体
 * @property {string} language - 语言
 * @property {boolean} autoScroll - 自动滚动
 * @property {boolean} showTimestamps - 显示时间戳
 * @property {boolean} confirmDelete - 删除确认
 * @property {boolean} streamingEnabled - 启用流式输出
 * @property {boolean} chatStyleDocument - 使用文档样式
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
    // MCP相关设置
    mcpConfig: {
      enabled: false,
      serverAddress: '',
      serverPort: 8080,
      timeout: 30,
    },

    // 通知相关设置
    notificationsConfig: {
      enabled: true,
      newMessage: true,
      sound: false,
      system: true,
      displayTime: '5秒',
    },

    // 系统设置
    systemSettings: {
      darkMode: false,
      fontSize: 16,
      fontFamily: 'Inter, system-ui, sans-serif',
      language: 'zh-CN',
      autoScroll: true,
      showTimestamps: true,
      graphLayout: 'force',
      graphNodeSize: 40,
      showGraphNodeLabels: true,
      graphAnimations: true,
      confirmDelete: true,
      streamingEnabled: true,
      chatStyleDocument: false,
      defaultModel: '',
      viewMode: 'grid',
    },

    // 模型相关设置
    availableModels: [],
    models: [],
    modelParams: {
      temperature: 0.7,
      max_tokens: 2000,
      top_p: 1.0,
      top_k: 50,
      frequency_penalty: 0.0,
    },
    
    // 模型加载状态
    modelLoading: false,
    // 模型错误信息
    modelError: null,
  }),

  getters: {
    // 获取当前系统设置
    currentSystemSettings: (state) => state.systemSettings,

    // 获取当前MCP配置
    currentMcpConfig: (state) => state.mcpConfig,

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
  },

  actions: {
    // 初始化设置监听
    initSettingsWatch() {
      // 简化实现：设置保存和应用通过组件内的watch和@change事件处理
    },
    
    // 设置默认模型
    setDefaultModel(model) {
      this.systemSettings.defaultModel = model;
      this.saveSettings();
    },
    
    // 获取默认模型
    getDefaultModel() {
      return this.systemSettings.defaultModel;
    },

    // 切换MCP功能
    toggleMcp(enabled) {
      this.mcpConfig.enabled = enabled;
      this.saveSettings();
    },

    // 更新MCP配置
    updateMcpConfig(config) {
      this.mcpConfig = { ...this.mcpConfig, ...config };
      this.saveSettings();
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

      if ('fontSize' in settings) {
        document.documentElement.style.fontSize = `${this.systemSettings.fontSize}px`;
      }

      if ('fontFamily' in settings) {
        document.body.style.fontFamily = this.systemSettings.fontFamily;
      }
    },

    // 重置设置为默认值
    resetSettings() {
      this.mcpConfig = {
        enabled: false,
        serverAddress: '',
        serverPort: 8080,
        timeout: 30,
      };

      this.notificationsConfig = {
        enabled: true,
        newMessage: true,
        sound: false,
        system: true,
        displayTime: '5秒',
      };

      this.systemSettings = {
        darkMode: false,
        fontSize: 16,
        fontFamily: 'Inter, system-ui, sans-serif',
        language: 'zh-CN',
        autoScroll: true,
        showTimestamps: true,
        confirmDelete: true,
        streamingEnabled: true,
        chatStyleDocument: false,
        viewMode: 'grid',
      };

      this.modelParams = {
        temperature: 0.7,
        max_tokens: 2000,
        top_p: 1.0,
        top_k: 50,
        frequency_penalty: 0.0,
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
        // 使用现有的apiService来调用后端API
        const notificationSettings = await apiService.get('/api/settings/notification');
        this.notificationsConfig = notificationSettings;
        
        // 加载MCP设置
        const mcpSettings = await apiService.get('/api/mcp');
        if (mcpSettings) {
          this.mcpConfig = {
            enabled: mcpSettings.enabled,
            serverAddress: mcpSettings.server_address,
            serverPort: mcpSettings.server_port,
            timeout: mcpSettings.timeout
          };
        }
        
        // 加载系统设置
        const systemSettings = await apiService.get('/api/settings/system');
        if (systemSettings) {
          // 更新系统设置，转换字段名以匹配前端模型
          const updatedSystemSettings = {
            darkMode: systemSettings.dark_mode,
            fontSize: systemSettings.font_size,
            chatStyleDocument: systemSettings.chat_style_document,
            viewMode: systemSettings.view_mode,
            showHiddenFiles: systemSettings.show_hidden_files,
            autoRefreshFiles: systemSettings.auto_refresh_files,
            maxRecentFiles: systemSettings.max_recent_files
          };
          this.systemSettings = { ...this.systemSettings, ...updatedSystemSettings };
        }
        
        // 加载模型列表
        await this.loadModels();
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
        if (this.systemSettings.fontSize) {
          document.documentElement.style.fontSize = `${this.systemSettings.fontSize}px`;
        }
        if (this.systemSettings.fontFamily) {
          document.body.style.fontFamily = this.systemSettings.fontFamily;
        }

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
        if (this.systemSettings.fontSize) {
          document.documentElement.style.fontSize = `${this.systemSettings.fontSize}px`;
        }
        if (this.systemSettings.fontFamily) {
          document.body.style.fontFamily = this.systemSettings.fontFamily;
        }

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
      if (savedSettings.mcpConfig && typeof savedSettings.mcpConfig === 'object') {
        this.mcpConfig = mergeSettings(this.mcpConfig, savedSettings.mcpConfig);
      }

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
        // 使用现有的apiService来调用后端API
        await apiService.post('/api/settings/notification', this.notificationsConfig);
        
        // 保存MCP设置，转换字段名
        const mcpSettingsToSave = {
          enabled: this.mcpConfig.enabled,
          server_address: this.mcpConfig.serverAddress,
          server_port: this.mcpConfig.serverPort,
          timeout: this.mcpConfig.timeout
        };
        await apiService.post('/api/mcp', mcpSettingsToSave);
        
        // 保存系统设置，转换字段名以匹配后端模型
        const systemSettingsToSave = {
          dark_mode: this.systemSettings.darkMode,
          font_size: this.systemSettings.fontSize,
          chat_style_document: this.systemSettings.chatStyleDocument,
          view_mode: this.systemSettings.viewMode,
          show_hidden_files: this.systemSettings.showHiddenFiles || false,
          auto_refresh_files: this.systemSettings.autoRefreshFiles || true,
          max_recent_files: this.systemSettings.maxRecentFiles || 10
        };
        await apiService.post('/api/settings/system', systemSettingsToSave);
      } catch (error) {
        console.error('保存设置到后端失败:', error);
      }
    },

    // 保存设置的核心功能
    async _saveSettingsCore() {
      try {
        const settingsToSave = {
          mcpConfig: this.mcpConfig,
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

    // 从后端加载模型列表
    async loadModels() {
      try {
        this.setModelLoading(true);
        this.setModelError(null);
        
        // 从后端加载模型列表
        const response = await apiService.models.getModels();
        // 确保models是数组
        this.models = Array.isArray(response.models) ? response.models : [];
        
        // 更新可用模型列表
        this.updateAvailableModels();
        
        // 通知事件总线，模型列表已更新
        eventBus.emit('modelsLoaded', { models: this.models });
      } catch (error) {
        this.setModelError('加载模型列表失败');
        console.error('加载模型列表失败:', error);
      } finally {
        this.setModelLoading(false);
      }
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
        if (model.configured && model.enabled && model.versions) {
          model.versions.forEach(version => {
            if (version && version.version_name) {
              // 与select组件保持一致：只使用version_name构建模型标识
              // 格式：model.name-version_name
              available.push(`${model.name}-${version.version_name}`);
            }
          });
        }
      });
      
      this.availableModels = available;
    },

    // 保存模型配置
    async saveModelConfig(modelName, config) {
      try {
        this.setModelLoading(true);
        this.setModelError(null);
        
        // 调用后端API保存配置
        await apiService.post(`/api/models/${modelName}`, {
          custom_name: config.customName,
          api_key: config.apiKey,
          api_base_url: config.apiBaseUrl,
          version_name: config.versionName,
          streaming_config: config.streamingConfig
        });
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        return true;
      } catch (error) {
        this.setModelError('保存模型配置失败');
        console.error('保存模型配置失败:', error);
        throw error;
      } finally {
        this.setModelLoading(false);
      }
    },

    // 删除模型配置
    async deleteModelConfig(modelName) {
      try {
        this.setModelLoading(true);
        this.setModelError(null);
        
        // 调用后端API删除配置
        await apiService.delete(`/api/models/${modelName}`);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        // 显示成功通知
        notifyUtils.showSuccess(`已删除${modelName}的配置`);
        
        return true;
      } catch (error) {
        this.setModelError('删除模型配置失败');
        console.error('删除模型配置失败:', error);
        notifyUtils.showError('删除失败: ' + (error.message || '未知错误'));
        throw error;
      } finally {
        this.setModelLoading(false);
      }
    },

    // 切换模型启用状态
    async toggleModelEnabled(modelName, enabled) {
      try {
        this.setModelLoading(true);
        this.setModelError(null);
        
        // 调用后端API更新启用状态
        await apiService.post(`/api/models/${modelName}/enabled`, {
          enabled: enabled
        });
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        return true;
      } catch (error) {
        this.setModelError('更新模型启用状态失败');
        console.error('更新模型启用状态失败:', error);
        throw error;
      } finally {
        this.setModelLoading(false);
      }
    },

    // 添加模型版本
    async addModelVersion(modelName, versionConfig) {
      try {
        this.setModelLoading(true);
        this.setModelError(null);
        
        // 构建请求数据
        const modelConfig = {
          custom_name: versionConfig.customName,
          api_key: versionConfig.apiKey,
          api_base_url: versionConfig.apiBaseUrl,
          version_name: versionConfig.versionName,
          streaming_config: versionConfig.streamingConfig
        };
        
        console.log('发送的API请求数据:', JSON.stringify(modelConfig));
        
        // 调用后端API保存配置
        await apiService.post(`/api/models/${modelName}`, modelConfig);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        return true;
      } catch (error) {
        this.setModelError('添加模型版本失败');
        console.error('添加模型版本失败:', error);
        throw error;
      } finally {
        this.setModelLoading(false);
      }
    },

    // 编辑模型版本
    async updateModelVersion(modelName, versionName, versionConfig) {
      try {
        this.setModelLoading(true);
        this.setModelError(null);
        
        // 构建请求数据
        const requestData = {
          custom_name: versionConfig.customName,
          api_key: versionConfig.apiKey,
          api_base_url: versionConfig.apiBaseUrl,
          version_name: versionConfig.versionName,
          streaming_config: versionConfig.streamingConfig
        };
        
        // 调用API保存配置
        await apiService.post(`/api/models/${modelName}`, requestData);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        return true;
      } catch (error) {
        this.setModelError('更新模型版本失败');
        console.error('更新模型版本失败:', error);
        throw error;
      } finally {
        this.setModelLoading(false);
      }
    },

    // 删除模型版本
    async deleteModelVersion(modelName, versionName) {
      try {
        this.setModelLoading(true);
        this.setModelError(null);
        
        // 调用后端API删除模型版本
        await apiService.delete(`/api/models/${modelName}/versions/${versionName}`);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        // 查找模型和版本信息用于通知
        const model = this.models.find(m => m.name === modelName);
        const version = model?.versions?.find(v => v.version_name === versionName);
        
        // 显示成功通知
        notifyUtils.showSuccess(`已删除${modelName}的版本 ${version?.custom_name || versionName}`);
        
        return true;
      } catch (error) {
        this.setModelError('删除模型版本失败');
        console.error('删除模型版本失败:', error);
        notifyUtils.showError('删除失败: ' + (error.message || '未知错误'));
        throw error;
      } finally {
        this.setModelLoading(false);
      }
    },

    // 重置模型设置为默认值
    resetModelSettings() {
      this.modelParams = {
        temperature: 0.7,
        max_tokens: 2000,
        top_p: 1.0,
        top_k: 50,
        frequency_penalty: 0.0,
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
  },
});
