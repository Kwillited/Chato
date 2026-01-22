import { useChatStore } from '../store/chatStore.js';
import { useSettingsStore } from '../store/settingsStore.js';

/**
 * 聊天头部组件的组合式函数，封装共享逻辑
 * @returns {Object} 包含聊天头部相关的状态和方法
 */
export function useChatHeader() {
  // 初始化stores
  const chatStore = useChatStore();
  const settingsStore = useSettingsStore();

  /**
   * 切换侧边菜单可见性
   */
  const handleSideMenuToggle = () => {
    settingsStore.toggleLeftNav();
  };

  /**
   * 处理新对话点击事件
   */
  const handleNewChat = () => {
    // 取消当前会话的激活状态
    chatStore.currentChatId = null;
    
    // 清除所有对话的未读标记
    chatStore.resetUnreadStatus();
    
    // 切换到发送消息视图
    settingsStore.setActiveContent('sendMessage');
  };

  /**
   * 从历史对话中选择对话
   * @param {string} chatId - 对话ID
   */
  const handleSelectHistoryChat = (chatId) => {
    // 选择对话
    chatStore.selectChat(chatId);
    
    // 切换到聊天视图
    settingsStore.setActiveContent('chat');
  };

  /**
   * 获取当前对话标题
   * @returns {string} 对话标题
   */
  const getCurrentChatTitle = () => {
    return chatStore.currentChat?.title || '当前无对话';
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
    chatHistory: chatStore.chatHistory,
    currentChatId: chatStore.currentChatId,
    currentChatMessages: chatStore.currentChatMessages
  };
}