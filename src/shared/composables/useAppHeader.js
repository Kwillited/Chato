// 应用头部组合式函数
import { computed } from 'vue';
import { useSettingsStore } from '../../app/store/settingsStore.js';
import { useNavigation } from './useNavigation.js';

/**
 * 应用头部组合式函数，用于动态管理不同页面的头部组件
 * @returns {Object} 头部管理相关的状态和方法
 */
export function useAppHeader() {
  const settingsStore = useSettingsStore();
  const { navigateToChat } = useNavigation();
  
  // 根据当前路由自动选择合适的头部组件
  const activeHeaderComponent = computed(() => {
    const currentRoute = window.location.pathname;
    
    // 根据不同的路由路径返回对应的头部组件名称
    if (currentRoute === '/settings') {
      return 'settings-header';
    } else if (currentRoute === '/chat' || currentRoute === '/') {
      return 'chat-header';
    }
    return 'chat-header';
  });
  
  // 动态加载头部组件的配置
  const headerConfig = computed(() => {
    const activeComponent = activeHeaderComponent.value;
    
    return {
      component: activeComponent,
      props: getHeaderProps(activeComponent),
      events: {
        // 通用事件处理
        toggleSideMenu: () => {
          settingsStore.toggleLeftNav();
        },
        newChat: () => {
          console.log('New chat requested');
        },
        selectHistoryChat: (chatId) => {
          console.log('Select chat:', chatId);
        },
        back: navigateToChat,
        tabChange: (tabValue) => {
          settingsStore.setActiveTab(tabValue);
        }
      }
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
  
  return {
    activeHeaderComponent,
    headerConfig
  };
}