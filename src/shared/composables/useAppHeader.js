// 应用头部组合式函数
import { computed } from 'vue';
import { useSettingsStore } from '../../app/store/settingsStore.js';

/**
 * 应用头部组合式函数，用于动态管理不同页面的头部组件
 * @returns {Object} 头部管理相关的状态和方法
 */
export function useAppHeader() {
  const settingsStore = useSettingsStore();
  
  // 根据当前激活的内容自动选择合适的头部组件
  const activeHeaderComponent = computed(() => {
    const activeContent = settingsStore.activeContent;
    
    // 根据不同的内容类型返回对应的头部组件名称
    switch (activeContent) {
      case 'settings':
        return 'settings-header';
      case 'chat':
      case 'sendMessage':
      default:
        return 'chat-header';
    }
  });
  
  // 动态加载头部组件的配置
  const headerConfig = computed(() => {
    const activeComponent = activeHeaderComponent.value;
    
    return {
      component: activeComponent,
      props: getHeaderProps(activeComponent),
      events: getHeaderEvents(activeComponent)
    };
  });
  
  // 根据组件类型获取对应的 props
  function getHeaderProps(componentName) {
    const baseProps = {
      title: getHeaderTitle(componentName)
    };
    
    // 根据不同组件添加特定 props
    switch (componentName) {
      case 'chat-header':
        return {
          ...baseProps,
          chatHistory: settingsStore.chatHistory || []
        };
      case 'settings-header':
        return {
          ...baseProps,
          activeTab: settingsStore.activeTab || 'basic',
          showBackButton: true
        };
      default:
        return baseProps;
    }
  }
  
  // 根据组件类型获取对应的事件
  function getHeaderEvents(componentName) {
    return {
      // 通用事件处理
      'toggleSideMenu': handleToggleSideMenu,
      'newChat': handleNewChat,
      'selectHistoryChat': handleSelectHistoryChat,
      'back': handleBack,
      'tabChange': handleTabChange
    };
  }
  
  // 根据组件类型获取头部标题
  function getHeaderTitle(componentName) {
    switch (componentName) {
      case 'chat-header':
        return 'AI Chat';
      case 'settings-header':
        return 'ChaTo Setting & Configuration';
      default:
        return 'AI Chat';
    }
  }
  
  // 切换侧边菜单
  function handleToggleSideMenu() {
    settingsStore.toggleLeftNav();
  }
  
  // 新建对话
  function handleNewChat() {
    // 调用聊天相关的组合式函数
    // 这里可以通过事件总线或直接调用 store 方法
    console.log('New chat requested');
  }
  
  // 选择历史对话
  function handleSelectHistoryChat(chatId) {
    // 调用聊天相关的组合式函数
    console.log('Select chat:', chatId);
  }
  
  // 返回按钮处理
  function handleBack() {
    settingsStore.setActiveContent('chat');
  }
  
  // 标签切换处理
  function handleTabChange(tabValue) {
    settingsStore.setActiveTab(tabValue);
  }
  
  return {
    activeHeaderComponent,
    headerConfig,
    handleToggleSideMenu,
    handleNewChat,
    handleSelectHistoryChat,
    handleBack,
    handleTabChange
  };
}