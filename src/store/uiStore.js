import { defineStore } from 'pinia';

/**
 * UI 状态管理 Store
 * 负责管理所有与用户界面相关的状态，如面板可见性、激活状态等
 */
export const useUiStore = defineStore('ui', {
  state: () => ({
    // 面板视图状态
    activePanel: 'history',
    activeContent: 'sendMessage',
    activeSection: 'general',

    // 左侧导航栏状态
    leftNavVisible: false,
    leftNavWidth: '200px',

    // 右侧面板状态
    rightPanelVisible: false,
    rightPanelWidth: '200px',

    // 全局加载状态
    isLoading: false,

    // UI 错误状态
    uiError: null,
  }),

  getters: {
    // 获取当前面板状态
    currentPanelState: (state) => ({
      activePanel: state.activePanel,
      activeContent: state.activeContent,
      activeSection: state.activeSection,
    }),

    // 获取导航栏状态
    navState: (state) => ({
      leftNavVisible: state.leftNavVisible,
      leftNavWidth: state.leftNavWidth,
      rightPanelVisible: state.rightPanelVisible,
      rightPanelWidth: state.rightPanelWidth,
    }),

    // 获取加载状态
    loadingState: (state) => state.isLoading,

    // 获取 UI 错误
    currentUiError: (state) => state.uiError,
  },

  actions: {
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

    // 设置 UI 错误
    setUiError(error) {
      this.uiError = error;
      if (error) {
        console.error('UI 错误:', error);
      }
    },

    // 清除 UI 错误
    clearUiError() {
      this.uiError = null;
    },

    // 重置 UI 状态
    resetUiState() {
      this.activePanel = 'history';
      this.activeContent = 'sendMessage';
      this.activeSection = 'general';
      this.leftNavVisible = false;
      this.rightPanelVisible = false;
      this.uiError = null;
    },

    // 初始化 UI 状态
    initUiState() {
      // 可以在这里添加初始化逻辑，如从本地存储加载 UI 状态
    },
  },
});
