import { defineStore } from 'pinia';
import { StorageManager, mergeSettings } from './utils';
import { apiService } from '../services/apiService.js';


// 存储键名常量
const STORAGE_KEYS = {
  SETTINGS: 'userSettings',
  LAST_USED: 'lastUsedSettings',
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

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // 当前激活的设置面板
    activePanel: 'history',
    // 当前激活的内容视图
    activeContent: 'sendMessage',
    // 当前激活的设置部分
    activeSection: 'general',

    // 全局加载状态
    isLoading: false,

    // 左侧导航栏可见性
    leftNavVisible: false,
    // 左侧导航栏宽度
    leftNavWidth: '200px',

    // 右侧面板可见性
    rightPanelVisible: false,
    // 右侧面板宽度
    rightPanelWidth: '200px',

    // RAG相关设置
    ragConfig: {
      enabled: false,
      chunk_size: 1000,
      chunk_overlap: 100,
      k: 4,
      retrievalMode: 'vector',
      topK: 3,
      scoreThreshold: 0.7,
      embedderModel: 'qwen3-embedding-0.6b',
      vectorDbPath: '', // 留空，让后端使用标准用户数据目录
      vectorDbType: 'chroma',
      knowledgeBasePath: '', // 留空，让后端使用标准用户数据目录
      selectedFolders: [], // 新增：指定的文件夹ID列表，用于限制RAG检索范围
      selectedKnowledgeBases: [], // 新增：指定的知识库ID列表，用于限制RAG检索范围
    },

    // MCP相关设置
    mcpConfig: {
      enabled: false,
      serverAddress: '',
      serverPort: 8080,
      timeout: 30,
    },

    // 通知相关设置
    notificationsConfig: {
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
  }),

  getters: {
    // 获取当前RAG配置
    currentRagConfig: (state) => state.ragConfig,

    // 获取当前系统设置
    currentSystemSettings: (state) => state.systemSettings,

    // 获取当前MCP配置
    currentMcpConfig: (state) => state.mcpConfig,

    // 获取当前通知配置
    currentNotificationsConfig: (state) => state.notificationsConfig,
  },

  actions: {
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



    // 切换RAG功能
    toggleRag(enabled) {
      this.ragConfig.enabled = enabled;
      this.saveSettings();
    },

    // 更新RAG配置
    updateRagConfig(config) {
      this.ragConfig = { ...this.ragConfig, ...config };
      this.saveSettings();
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

      this.ragConfig = {
        enabled: false,
        chunk_size: 1000,
        chunk_overlap: 100,
        k: 4,
        retrievalMode: 'vector',
        topK: 3,
        scoreThreshold: 0.7,
        embedderModel: 'qwen3-embedding-0.6b',
        vectorDbPath: '', // 留空，让后端使用标准用户数据目录
        vectorDbType: 'chroma',
        knowledgeBasePath: '', // 留空，让后端使用标准用户数据目录
      };

      this.mcpConfig = {
        enabled: false,
        serverAddress: '',
        serverPort: 8080,
        timeout: 30,
      };

      this.notificationsConfig = {
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
        
        // 加载基本设置
        const systemSettings = await apiService.get('/api/settings/basic');
        if (systemSettings) {
          this.systemSettings = { ...this.systemSettings, ...systemSettings };
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

        // 确保activePanel和ragConfig.enabled状态一致
        if (this.ragConfig.enabled && this.activePanel !== 'rag') {
          this.activePanel = 'rag';
        } else if (!this.ragConfig.enabled && this.activePanel === 'rag') {
          this.activePanel = 'history';
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

        // 确保activePanel和ragConfig.enabled状态一致
        if (this.ragConfig.enabled && this.activePanel !== 'rag') {
          this.activePanel = 'rag';
        } else if (!this.ragConfig.enabled && this.activePanel === 'rag') {
          this.activePanel = 'history';
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
      // 注意：模型相关设置现在由modelSettingStore单独管理和加载

      if (savedSettings.ragConfig && typeof savedSettings.ragConfig === 'object') {
        this.ragConfig = mergeSettings(this.ragConfig, savedSettings.ragConfig);
      }

      if (savedSettings.mcpConfig && typeof savedSettings.mcpConfig === 'object') {
        this.mcpConfig = mergeSettings(this.mcpConfig, savedSettings.mcpConfig);
      }

      if (savedSettings.notificationsConfig && typeof savedSettings.notificationsConfig === 'object') {
        this.notificationsConfig = mergeSettings(this.notificationsConfig, savedSettings.notificationsConfig);
      }

      if (savedSettings.systemSettings && typeof savedSettings.systemSettings === 'object') {
        this.systemSettings = mergeSettings(this.systemSettings, savedSettings.systemSettings);
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
        
        // 保存基本设置
        await apiService.post('/api/settings/basic', this.systemSettings);
      } catch (error) {
        console.error('保存设置到后端失败:', error);
      }
    },

    // 保存设置的核心功能
    async _saveSettingsCore() {
      try {
        // 注意：模型设置现在由modelSettingStore单独管理和保存
        
        const settingsToSave = {
          ragConfig: this.ragConfig,
          mcpConfig: this.mcpConfig,
          notificationsConfig: this.notificationsConfig,
          systemSettings: this.systemSettings,
          activeSection: this.activeSection,
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
  },
});
