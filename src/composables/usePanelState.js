import { ref, computed } from 'vue';
import { useUiStore } from '../store/uiStore.js';

/**
 * 面板状态管理组合函数
 * 用于管理面板的展开/折叠、切换等状态和操作
 */
export function usePanelState() {
  const uiStore = useUiStore();
  
  // 局部面板状态
  const isPanelExpanded = ref(false);
  
  // 计算属性：当前激活的面板
  const currentPanel = computed(() => uiStore.activePanel);
  
  // 计算属性：当前激活的内容
  const currentContent = computed(() => uiStore.activeContent);
  
  // 计算属性：左侧导航栏可见性
  const isLeftNavVisible = computed(() => uiStore.leftNavVisible);
  
  // 计算属性：右侧面板可见性
  const isRightPanelVisible = computed(() => uiStore.rightPanelVisible);
  
  // 计算属性：左侧导航栏宽度
  const leftNavWidth = computed(() => uiStore.leftNavWidth);
  
  // 计算属性：右侧面板宽度
  const rightPanelWidth = computed(() => uiStore.rightPanelWidth);
  
  // 方法：切换面板展开状态
  const togglePanelExpanded = () => {
    isPanelExpanded.value = !isPanelExpanded.value;
  };
  
  // 方法：切换到指定面板
  const switchPanel = (panel) => {
    uiStore.setActivePanel(panel);
  };
  
  // 方法：切换到指定内容
  const switchContent = (content) => {
    uiStore.setActiveContent(content);
  };
  
  // 方法：切换左侧导航栏可见性
  const toggleLeftNav = () => {
    uiStore.toggleLeftNav();
  };
  
  // 方法：切换右侧面板可见性
  const toggleRightPanel = () => {
    uiStore.toggleRightPanel();
  };
  
  // 方法：设置左侧导航栏宽度
  const setLeftNavWidth = (width) => {
    uiStore.setLeftNavWidth(width);
  };
  
  // 方法：设置右侧面板宽度
  const setRightPanelWidth = (width) => {
    uiStore.setRightNavWidth(width);
  };
  
  // 方法：检查是否为指定面板
  const isPanelActive = (panel) => {
    return uiStore.activePanel === panel;
  };
  
  // 方法：检查是否为指定内容
  const isContentActive = (content) => {
    return uiStore.activeContent === content;
  };
  
  return {
    // 状态
    isPanelExpanded,
    currentPanel,
    currentContent,
    isLeftNavVisible,
    isRightPanelVisible,
    leftNavWidth,
    rightPanelWidth,
    
    // 方法
    togglePanelExpanded,
    switchPanel,
    switchContent,
    toggleLeftNav,
    toggleRightPanel,
    setLeftNavWidth,
    setRightPanelWidth,
    isPanelActive,
    isContentActive,
  };
}
