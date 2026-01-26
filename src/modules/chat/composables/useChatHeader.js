import { useChatStore } from '../../../app/store/chatStore.js';
import { useSettingsStore } from '../../../app/store/settingsStore.js';
import { useChatManagement } from './useChatManagement.js';
import { useNavigation } from '../../../shared/composables/useNavigation.js';
import { useAppUI } from '../../../shared/composables/useAppUI.js';

/**
 * 聊天头部组件的组合式函数，封装共享逻辑
 * @returns {Object} 包含聊天头部相关的状态和方法
 */
export function useChatHeader() {
  // 初始化stores
  const chatStore = useChatStore();
  const settingsStore = useSettingsStore();
  
  // 使用导航组合函数
  const { navigateToHome } = useNavigation();
  
  // 使用应用UI组合函数
  const { toggleLeftNav } = useAppUI();
  
  // 使用对话管理组合函数
  const { createNewChat, selectChat, getCurrentChatTitle, chatHistory, currentChatId, currentChat } = useChatManagement();

  /**
   * 切换侧边菜单可见性
   */
  const handleSideMenuToggle = () => {
    console.log('handleSideMenuToggle called');
    // 切换左侧导航栏可见性
    toggleLeftNav();
  };

  /**
   * 处理新对话点击事件 - 直接跳转到首页
   */
  const handleNewChat = () => {
    // 直接跳转到根目录（首页），不创建新对话
    navigateToHome();
  };

  /**
   * 从历史对话中选择对话
   * @param {string} chatId - 对话ID
   */
  const handleSelectHistoryChat = async (chatId) => {
    try {
      await selectChat(chatId);
      // 切换到聊天视图 - 路由管理下不需要手动切换
    } catch (error) {
      console.error('选择对话失败:', error);
    }
  };

  return {
    // stores
    chatStore,
    settingsStore,
    
    // 方法
    handleSideMenuToggle,
    handleNewChat,
    handleSelectHistoryChat,
    getCurrentChatTitle,
    
    // 可访问的store属性
    chatHistory,
    currentChatId,
    currentChatMessages: chatStore.currentChatMessages
  };
}