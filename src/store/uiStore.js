import { defineStore } from 'pinia';
import { errorUtils, loadingUtils } from '../utils/storeUtils.js';

/**
 * UI 状态管理 Store
 * 负责管理所有与用户界面相关的状态，如面板可见性、激活状态、输入框内容等
 * 与业务逻辑分离，专注于 UI 层面的状态管理
 */
export const useUiStore = defineStore('ui', {
  /**
   * 状态定义
   * 包含所有 UI 相关的状态属性
   */
  
  /**
   * 持久化配置
   * 启用状态持久化，确保刷新页面后状态不丢失
   */
  persist: true,
  state: () => ({
    // 面板视图状态
    activePanel: 'history', // 当前激活的面板
    activeContent: 'home', // 当前激活的内容视图
    activeSection: 'general', // 当前激活的设置部分
    previousContent: 'home', // 之前的内容视图，用于返回功能
    previousPanel: 'history', // 之前的面板，用于MCP面板切换返回

    // 左侧导航栏状态
    leftNavVisible: false, // 左侧导航栏是否可见
    leftNavWidth: '200px', // 左侧导航栏宽度

    // 右侧面板状态
    rightPanelVisible: false, // 右侧面板是否可见
    rightPanelWidth: '200px', // 右侧面板宽度

    // 全局加载状态
    isLoading: false, // 是否处于加载状态

    // UI 错误状态
    uiError: null, // UI 相关的错误信息

    // 从 chatStore 迁移的 UI 状态
    messageInput: '', // 消息输入框内容
    searchQuery: '', // 搜索关键词
    activeView: 'chat', // 视图模式：'chat'为对话视图，'Graph'为图谱视图

    // 功能按钮状态
    isDeepThinking: false, // 深度思考模式
    isWebSearchEnabled: false, // 联网搜索模式
    isAgentEnabled: false, // 智能体模式
  }),

  /**
   * Getters 定义
   * 用于获取和计算衍生状态
   */
  getters: {
    /**
     * 获取当前面板状态
     * @returns {Object} 当前面板状态对象
     */
    currentPanelState: (state) => ({
      activePanel: state.activePanel,
      activeContent: state.activeContent,
      activeSection: state.activeSection,
    }),

    /**
     * 获取导航栏状态
     * @returns {Object} 导航栏状态对象
     */
    navState: (state) => ({
      leftNavVisible: state.leftNavVisible,
      leftNavWidth: state.leftNavWidth,
      rightPanelVisible: state.rightPanelVisible,
      rightPanelWidth: state.rightPanelWidth,
    }),

    /**
     * 获取加载状态
     * @returns {boolean} 是否处于加载状态
     */
    loadingState: (state) => state.isLoading,

    /**
     * 获取 UI 错误
     * @returns {string|null} UI 错误信息
     */
    currentUiError: (state) => state.uiError,
  },

  /**
   * Actions 定义
   * 用于修改状态的方法
   */
  actions: {
    /**
     * 切换设置面板
     * @param {string} panel - 面板名称
     */
    setActivePanel(panel) {
      this.activePanel = panel;
    },

    /**
     * 切换设置部分
     * @param {string} section - 部分名称
     */
    setActiveSection(section) {
      this.activeSection = section;
    },

    /**
     * 设置右侧面板可见性
     * @param {boolean} visible - 是否可见
     */
    setRightPanelVisible(visible) {
      this.rightPanelVisible = visible;
    },

    /**
     * 切换右侧面板可见性
     */
    toggleRightPanel() {
      this.rightPanelVisible = !this.rightPanelVisible;
    },

    /**
     * 切换左侧导航栏可见性
     */
    toggleLeftNav() {
      this.leftNavVisible = !this.leftNavVisible;
    },

    /**
     * 设置当前激活的内容视图
     * @param {string} content - 内容视图名称
     */
    setActiveContent(content) {
      this.activeContent = content;
    },

    /**
     * 设置左侧导航栏宽度
     * @param {string} width - 宽度值
     */
    setLeftNavWidth(width) {
      this.leftNavWidth = width;
    },

    /**
     * 设置右侧面板宽度
     * @param {string} width - 宽度值
     */
    setRightNavWidth(width) {
      this.rightPanelWidth = width;
    },

    /**
     * 设置全局加载状态
     * @param {boolean} loading - 是否处于加载状态
     */
    setLoading(loading) {
      this.isLoading = loading;
    },

    /**
     * 设置 UI 错误
     * @param {string} error - 错误信息
     */
    setUiError(error) {
      this.uiError = error;
      if (error) {
        console.error('UI 错误:', error);
      }
    },

    /**
     * 清除 UI 错误
     */
    clearUiError() {
      this.uiError = null;
    },

    /**
     * 重置 UI 状态
     * 将所有 UI 状态恢复到默认值
     */
    resetUiState() {
      this.activePanel = 'history';
      this.activeContent = 'home';
      this.activeSection = 'general';
      this.leftNavVisible = false;
      this.rightPanelVisible = false;
      this.uiError = null;
    },

    /**
     * 初始化 UI 状态
     * 可以在这里添加初始化逻辑，如从本地存储加载 UI 状态
     */
    initUiState() {
      // 可以在这里添加初始化逻辑，如从本地存储加载 UI 状态
    },

    /**
     * 从 chatStore 迁移的方法
     * 更新消息输入框内容
     * @param {string} content - 消息内容
     */
    updateMessageInput(content) {
      this.messageInput = content;
    },

    /**
     * 从 chatStore 迁移的方法
     * 设置搜索关键词
     * @param {string} query - 搜索关键词
     */
    setSearchQuery(query) {
      this.searchQuery = query;
    },

    /**
     * 从 chatStore 迁移的方法
     * 设置视图模式
     * @param {string} view - 视图模式：'chat'或'Graph'
     */
    setActiveView(view) {
      this.activeView = view;
    },

    /**
     * 切换深度思考模式
     */
    toggleDeepThinking() {
      this.isDeepThinking = !this.isDeepThinking;
    },

    /**
     * 切换联网搜索模式
     */
    toggleWebSearch() {
      this.isWebSearchEnabled = !this.isWebSearchEnabled;
    },

    /**
     * 切换智能体模式
     */
    toggleAgent() {
      this.isAgentEnabled = !this.isAgentEnabled;
    },

    /**
     * 设置深度思考模式
     * @param {boolean} value - 是否启用
     */
    setDeepThinking(value) {
      this.isDeepThinking = value;
    },

    /**
     * 设置联网搜索模式
     * @param {boolean} value - 是否启用
     */
    setWebSearch(value) {
      this.isWebSearchEnabled = value;
    },

    /**
     * 设置智能体模式
     * @param {boolean} value - 是否启用
     */
    setAgent(value) {
      this.isAgentEnabled = value;
    },
  },
});
