import { defineStore } from 'pinia';
import { StorageManager, mergeSettings } from './utils';
import { apiService } from '../services/apiService.js';
import eventBus, { Events } from '../services/eventBus.js';
import { showNotification } from '../services/notificationUtils.js';
import { useBaseStore } from './baseStore';

// 获取基础Store功能
const baseStore = useBaseStore();


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

// 定义向量配置的类型描述
/**
 * @typedef {Object} VectorConfig
 * @property {boolean} enabled - 是否启用向量功能
 * @property {Object} retrieval - 检索配置
 * @property {string} retrieval.mode - 检索模式（vector/keyword/hybrid）
 * @property {number} retrieval.topK - 检索数量
 * @property {number} retrieval.threshold - 相关性阈值
 * @property {string} retrieval.similarityType - 相似度计算方式
 * @property {Object} embedding - 嵌入模型配置
 * @property {string} embedding.model - 嵌入模型名称
 * @property {number} embedding.chunkSize - 分块大小
 * @property {number} embedding.chunkOverlap - 重叠大小
 * @property {Object} storage - 向量存储配置
 * @property {string} storage.type - 存储类型
 * @property {string} storage.path - 存储路径
 * @property {string} storage.knowledgeBasePath - 知识库路径
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

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // 基础状态
    ...baseStore.state(),
    
    // 当前激活的设置面板
    activePanel: 'history',
    // 当前激活的内容视图
    activeContent: 'sendMessage',
    // 当前激活的设置部分
    activeSection: 'general',

    // 左侧导航栏可见性
    leftNavVisible: false,
    // 左侧导航栏宽度
    leftNavWidth: '200px',

    // 右侧面板可见性
    rightPanelVisible: false,
    // 右侧面板宽度
    rightPanelWidth: '200px',

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

    // 向量配置（从vectorStore迁移）
    vectorConfig: {
      enabled: false,
      retrieval: {
        mode: 'vector',
        topK: 3,
        threshold: 0.7,
        similarityType: 'cosine'
      },
      embedding: {
        model: 'qwen3-embedding-0.6b',
        chunkSize: 1000,
        chunkOverlap: 100
      },
      storage: {
        type: 'chroma',
        path: '',
        knowledgeBasePath: ''
      }
    },

    // 系统设置
    systemSettings: {
      darkMode: false,
      fontSize: 16,
      fontFamily: 'Inter, system-ui, sans-serif',
      language: 'zh-CN',
      autoScroll: true,
      showTimestamps: true,
      // 知识图谱样式设置
      graphLayout: 'force',
      graphNodeSize: 40,
      showGraphNodeLabels: true,
      graphAnimations: true,
      confirmDelete: true,
      streamingEnabled: true,  // 启用流式输出
      chatStyleDocument: false,  // 使用文档样式
      defaultModel: '',  // 默认模型
      viewMode: 'grid',  // 文件视图模式：'grid' 或 'list'
    },
    
    // 模型相关设置（从modelSettingStore合并）
    availableModels: [],
    models: [], // 存储所有模型配置
    modelParams: {
      temperature: 0.7,
      max_tokens: 2000,
      top_p: 1.0,
      top_k: 50,
      frequency_penalty: 0.0,
    },
  }),

  getters: {
    // 基础getters
    ...baseStore.getters,
    
    // 获取当前向量配置
    currentVectorConfig: (state) => state.vectorConfig,

    // 获取当前系统设置
    currentSystemSettings: (state) => state.systemSettings,

    // 获取当前MCP配置
    currentMcpConfig: (state) => state.mcpConfig,

    // 获取当前通知配置
    currentNotificationsConfig: (state) => state.notificationsConfig,
    
    // 模型相关getters（从modelSettingStore合并）
    currentModelParams: (state) => state.modelParams,
    availableModelList: (state) => state.availableModels,
    allModels: (state) => state.models,
    configuredModels: (state) => state.models.filter(model => model.configured),
    unconfiguredModels: (state) => {
      // 确保返回所有未配置的模型，如果模型没有configured字段，默认为未配置
      return state.models.filter(model => model.configured !== true);
    },
  },

  actions: {
    // 基础actions
    ...baseStore.actions,
    
    // 初始化设置监听 - 移除$subscribe，避免TypeError
    initSettingsWatch() {
      // 简化实现：移除$subscribe调用，避免TypeError
      // 设置保存和应用通过组件内的watch和@change事件处理
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
    
    // 切换设置面板
    setActivePanel(panel) {
      this.activePanel = panel;
    },

    // 切换设置部分
    setActiveSection(section) {
      this.activeSection = section;
    },

    // 设置右侧面板可见性
    setRightPanelVisible(visible) {
      this.rightPanelVisible = visible;
    },

    // 切换右侧面板可见性
    toggleRightPanel() {
      this.rightPanelVisible = !this.rightPanelVisible;
    },

    // 切换左侧导航栏可见性
    toggleLeftNav() {
      this.leftNavVisible = !this.leftNavVisible;
    },

    // 设置当前激活的内容视图
    setActiveContent(content) {
      this.activeContent = content;
    },

    // 设置左侧导航栏宽度
    setLeftNavWidth(width) {
      this.leftNavWidth = width;
    },

    // 设置右侧面板宽度
    setRightNavWidth(width) {
      this.rightPanelWidth = width;
    },

    // 设置全局加载状态
    setLoading(loading) {
      this.isLoading = loading;
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
      
      // 发布系统设置更新事件
      eventBus.emit(Events.SETTINGS_UPDATED, { systemSettings: this.systemSettings });
    },

    // 更新向量配置
    updateVectorConfig(config) {
      this.vectorConfig = { ...this.vectorConfig, ...config };
      this.saveSettings();
      
      // 发布RAG配置更改事件
      eventBus.emit(Events.RAG_CONFIG_CHANGED, this.vectorConfig);
    },

    // 更新向量检索配置
    updateVectorRetrievalConfig(retrievalConfig) {
      this.vectorConfig.retrieval = { ...this.vectorConfig.retrieval, ...retrievalConfig };
      this.saveSettings();
      
      // 发布RAG配置更改事件
      eventBus.emit(Events.RAG_CONFIG_CHANGED, this.vectorConfig);
    },

    // 更新向量嵌入配置
    updateVectorEmbeddingConfig(embeddingConfig) {
      this.vectorConfig.embedding = { ...this.vectorConfig.embedding, ...embeddingConfig };
      this.saveSettings();
      
      // 发布RAG配置更改事件
      eventBus.emit(Events.RAG_CONFIG_CHANGED, this.vectorConfig);
    },

    // 更新向量存储配置
    updateVectorStorageConfig(storageConfig) {
      this.vectorConfig.storage = { ...this.vectorConfig.storage, ...storageConfig };
      this.saveSettings();
      
      // 发布RAG配置更改事件
      eventBus.emit(Events.RAG_CONFIG_CHANGED, this.vectorConfig);
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

      this.vectorConfig = {
        enabled: false,
        retrieval: {
          mode: 'vector',
          topK: 3,
          threshold: 0.7,
          similarityType: 'cosine'
        },
        embedding: {
          model: 'qwen3-embedding-0.6b',
          chunkSize: 1000,
          chunkOverlap: 100
        },
        storage: {
          type: 'chroma',
          path: '',
          knowledgeBasePath: ''
        }
      };

      this.systemSettings = {
        darkMode: false,
        fontSize: 16,
        fontFamily: 'Inter, system-ui, sans-serif',
        language: 'zh-CN',
        autoScroll: true,
        showTimestamps: true,
        confirmDelete: true,
        streamingEnabled: true,  // 启用流式输出
        chatStyleDocument: false,  // 使用文档样式
        viewMode: 'grid',  // 默认使用网格视图
      };

      this.applyDarkMode();
      this.saveSettings();
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
      } catch (error) {
        console.error('从后端加载设置失败:', error);
      }
    },

    // 仅从存储中加载设置，不请求API
    async loadSettingsFromStorageOnly() {
      try {
        this.setLoading(true);
        
        // 只从localStorage加载设置，不请求API
        const savedSettings = StorageManager.getItem(STORAGE_KEYS.SETTINGS);
        if (savedSettings) {
          this.mergeSavedSettings(savedSettings);
        }

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
      } finally {
        this.setLoading(false);
      }
    },

    // 从存储中加载设置（包含API请求）
    async loadSettings() {
      try {
        this.setLoading(true);
        
        // 先从localStorage加载设置
        const savedSettings = StorageManager.getItem(STORAGE_KEYS.SETTINGS);
        if (savedSettings) {
          this.mergeSavedSettings(savedSettings);
        }
        
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
      } finally {
        this.setLoading(false);
      }
    },



    // 合并保存的设置
    mergeSavedSettings(savedSettings) {
      // 合并向量配置
      if (savedSettings.vectorConfig && typeof savedSettings.vectorConfig === 'object') {
        this.vectorConfig = mergeSettings(this.vectorConfig, savedSettings.vectorConfig);
      }

      // 合并MCP配置
      if (savedSettings.mcpConfig && typeof savedSettings.mcpConfig === 'object') {
        this.mcpConfig = mergeSettings(this.mcpConfig, savedSettings.mcpConfig);
      }

      // 合并通知配置
      if (savedSettings.notificationsConfig && typeof savedSettings.notificationsConfig === 'object') {
        this.notificationsConfig = mergeSettings(this.notificationsConfig, savedSettings.notificationsConfig);
      }

      // 合并系统设置
      if (savedSettings.systemSettings && typeof savedSettings.systemSettings === 'object') {
        this.systemSettings = mergeSettings(this.systemSettings, savedSettings.systemSettings);
      }
      
      // 合并模型设置
      if (savedSettings.modelParams && typeof savedSettings.modelParams === 'object') {
        this.modelParams = mergeSettings(this.modelParams, savedSettings.modelParams);
      }

      // 恢复上次选择的设置部分
      if (savedSettings.activeSection) {
        this.activeSection = savedSettings.activeSection;
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
        
        // 保存向量配置
        await apiService.post('/api/settings/vector', this.vectorConfig);
        
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
        // 保存所有需要跨会话持久化的设置
        const settingsToSave = {
          vectorConfig: this.vectorConfig,
          mcpConfig: this.mcpConfig,
          notificationsConfig: this.notificationsConfig,
          systemSettings: this.systemSettings,
          modelParams: this.modelParams, // 保存模型参数
          leftNavWidth: this.leftNavWidth, // 保存导航栏宽度设置
          rightPanelWidth: this.rightPanelWidth, // 保存右侧面板宽度设置
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
    
    // 模型管理相关actions（从modelSettingStore合并）
    
    // 选择模型（仅同步到本地存储，主要通过settingsStore管理）
    selectModel(model) {
      if (this.availableModels.includes(model)) {
        // 注意：selectedModel已移至settingsStore管理
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
        this.setLoading(true);
        this.clearError();
        
        // 从后端加载模型列表
        const response = await apiService.models.getModels();
        // 确保models是数组，API响应已经被标准化，模型列表在response.data中
        this.models = Array.isArray(response.data?.models) ? response.data.models : [];
        
        // 更新可用模型列表
        this.updateAvailableModels();
        
        // 通知事件总线，模型列表已更新
        eventBus.emit(Events.MODEL_UPDATED, { models: this.models });
      } catch (error) {
        this.setError('加载模型列表失败');
        console.error('加载模型列表失败:', error);
      } finally {
        this.setLoading(false);
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
        this.setLoading(true);
        this.clearError();
        
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
        eventBus.emit(Events.MODEL_UPDATED, { models: this.models });
        
        return true;
      } catch (error) {
        this.setError('保存模型配置失败');
        console.error('保存模型配置失败:', error);
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 删除模型配置
    async deleteModelConfig(modelName) {
      try {
        this.setLoading(true);
        this.clearError();
        
        // 调用后端API删除配置
        await apiService.delete(`/api/models/${modelName}`);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit(Events.MODEL_UPDATED, { models: this.models });
        
        // 显示成功通知
        showNotification(`已删除${modelName}的配置`, 'success');
        
        return true;
      } catch (error) {
        this.setError('删除模型配置失败');
        console.error('删除模型配置失败:', error);
        showNotification('删除失败: ' + (error.message || '未知错误'), 'error');
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 切换模型启用状态
    async toggleModelEnabled(modelName, enabled) {
      try {
        this.setLoading(true);
        this.clearError();
        
        // 调用后端API更新启用状态
        await apiService.post(`/api/models/${modelName}/enabled`, {
          enabled: enabled
        });
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit(Events.MODEL_UPDATED, { models: this.models });
        
        return true;
      } catch (error) {
        this.setError('更新模型启用状态失败');
        console.error('更新模型启用状态失败:', error);
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 添加模型版本
    async addModelVersion(modelName, versionConfig) {
      try {
        this.setLoading(true);
        this.clearError();
        
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
        eventBus.emit(Events.MODEL_UPDATED, { models: this.models });
        
        return true;
      } catch (error) {
        this.setError('添加模型版本失败');
        console.error('添加模型版本失败:', error);
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 编辑模型版本
    async updateModelVersion(modelName, versionName, versionConfig) {
      try {
        this.setLoading(true);
        this.clearError();
        
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
        eventBus.emit(Events.MODEL_UPDATED, { models: this.models });
        
        return true;
      } catch (error) {
        this.setError('更新模型版本失败');
        console.error('更新模型版本失败:', error);
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 删除模型版本
    async deleteModelVersion(modelName, versionName) {
      try {
        this.setLoading(true);
        this.clearError();
        
        // 调用后端API删除模型版本
        await apiService.delete(`/api/models/${modelName}/versions/${versionName}`);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit(Events.MODEL_UPDATED, { models: this.models });
        
        // 查找模型和版本信息用于通知
        const model = this.models.find(m => m.name === modelName);
        const version = model?.versions?.find(v => v.version_name === versionName);
        
        // 显示成功通知
        showNotification(`已删除${modelName}的版本 ${version?.custom_name || versionName}`, 'success');
        
        return true;
      } catch (error) {
        this.setError('删除模型版本失败');
        console.error('删除模型版本失败:', error);
        showNotification('删除失败: ' + (error.message || '未知错误'), 'error');
        throw error;
      } finally {
        this.setLoading(false);
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
      this.error = null;
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

      // 注意：selectedModel已移至settingsStore管理
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
