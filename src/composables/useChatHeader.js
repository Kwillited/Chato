import { useChatStore } from '../store/chatStore.js';
import { useSettingsStore } from '../store/settingsStore.js';
import { useChatManagement } from './useChatManagement.js';

/**
 * 聊天头部组件的组合式函数，封装共享逻辑
 * @returns {Object} 包含聊天头部相关的状态和方法
 */
export function useChatHeader() {
  // 初始化stores
  const chatStore = useChatStore();
  const settingsStore = useSettingsStore();
  
  // 使用对话管理组合函数
  const { createNewChat, selectChat, getCurrentChatTitle, chatHistory, currentChatId, currentChat } = useChatManagement();

  /**
   * 切换侧边菜单可见性
   */
  const handleSideMenuToggle = () => {
    settingsStore.toggleLeftNav();
  };

  /**
   * 处理新对话点击事件
   */
  const handleNewChat = async () => {
    try {
      await createNewChat();
      // 切换到发送消息视图
      settingsStore.setActiveContent('sendMessage');
    } catch (error) {
      console.error('创建新对话失败:', error);
    }
  };

  /**
   * 从历史对话中选择对话
   * @param {string} chatId - 对话ID
   */
  const handleSelectHistoryChat = async (chatId) => {
    try {
      await selectChat(chatId);
      // 切换到聊天视图
      settingsStore.setActiveContent('chat');
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