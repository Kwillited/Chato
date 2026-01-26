import { ref, computed, provide, inject } from 'vue';

// 创建一个唯一的注入键
const APP_UI_INJECT_KEY = Symbol('appUI');

/**
 * 应用UI状态组合式函数
 * 集中管理应用的UI状态，如导航栏可见性、面板宽度等
 * 使用provide/inject模式确保所有组件共享同一个状态实例
 * @returns {Object} 包含UI状态和操作方法的对象
 */
export function useAppUI() {
  // 尝试从父组件注入appUI状态
  const existingAppUI = inject(APP_UI_INJECT_KEY, null);

  // 如果已经存在appUI状态，直接返回
  if (existingAppUI) {
    return existingAppUI;
  }

  // 如果不存在，创建新的appUI状态
  // UI状态 - 导航栏
  const leftNavVisible = ref(false);
  const leftNavWidth = ref('200px');

  // UI状态 - 侧边栏类型
  const activeSidebar = ref('message'); // message, folder, mcp

  // UI状态 - 面板
  const rightPanelVisible = ref(false);
  const rightPanelWidth = ref('200px');

  // UI状态 - 设置页面选项卡
  const activeTab = ref('basic');

  // 计算属性
  const isLeftNavOpen = computed(() => leftNavVisible.value);
  const isRightPanelOpen = computed(() => rightPanelVisible.value);

  // 方法 - 导航栏控制
  const toggleLeftNav = () => {
    leftNavVisible.value = !leftNavVisible.value;
  };

  const setLeftNavVisible = (visible) => {
    leftNavVisible.value = visible;
  };

  const setLeftNavWidth = (width) => {
    leftNavWidth.value = width;
  };

  // 方法 - 面板控制
  const toggleRightPanel = () => {
    rightPanelVisible.value = !rightPanelVisible.value;
  };

  const setRightPanelVisible = (visible) => {
    rightPanelVisible.value = visible;
  };

  const setRightPanelWidth = (width) => {
    rightPanelWidth.value = width;
  };

  // 方法 - 侧边栏类型控制
  const setActiveSidebar = (sidebarType) => {
    activeSidebar.value = sidebarType;
  };

  // 方法 - 设置页面选项卡控制
  const setActiveTab = (tab) => {
    activeTab.value = tab;
  };

  const resetActiveTab = () => {
    activeTab.value = 'basic';
  };

  // 构建appUI状态对象
  const appUI = {
    // 状态 - 导航栏
    leftNavVisible,
    leftNavWidth,
    isLeftNavOpen,

    // 状态 - 侧边栏类型
    activeSidebar,

    // 状态 - 面板
    rightPanelVisible,
    rightPanelWidth,
    isRightPanelOpen,

    // 状态 - 设置页面选项卡
    activeTab,

    // 方法 - 导航栏控制
    toggleLeftNav,
    setLeftNavVisible,
    setLeftNavWidth,

    // 方法 - 侧边栏类型控制
    setActiveSidebar,

    // 方法 - 面板控制
    toggleRightPanel,
    setRightPanelVisible,
    setRightPanelWidth,

    // 方法 - 设置页面选项卡控制
    setActiveTab,
    resetActiveTab
  };

  // 提供appUI状态给子组件
  provide(APP_UI_INJECT_KEY, appUI);

  return appUI;
}
