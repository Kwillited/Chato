import { ref, computed, watch } from 'vue';
import { useChatStore as usePiniaChatStore } from '../../../app/store/chatStore.js';
import logger from '../../../shared/utils/logger.js';

/**
 * chatStore的统一访问入口组合函数
 * 封装所有对chatStore的直接访问，提供更友好的API接口
 * @returns {Object} 包含chatStore相关的状态和方法
 */
export function useChatStore() {
  // 获取原始的chatStore实例
  const chatStore = usePiniaChatStore();
  
  // 响应式状态映射
  const chats = computed(() => chatStore.chats || []);
  const currentChatId = computed({
    get: () => chatStore.currentChatId,
    set: (value) => chatStore.selectChat(value)
  });
  const isLoading = computed({
    get: () => chatStore.isLoading,
    set: (value) => chatStore.setLoading(value)
  });
  const error = computed(() => chatStore.error);
  
  // 计算属性映射
  const currentChat = computed(() => chatStore.currentChat);
  const currentChatMessages = computed(() => chatStore.currentChatMessages);
  const chatHistory = computed(() => chatStore.chatHistory);
  const standardizedModels = computed(() => chatStore.standardizedModels);
  
  // 对话管理方法
  const createNewChat = async (model) => {
    try {
      return await chatStore.createNewChat(model);
    } catch (err) {
      logger.error('创建新对话失败:', err);
      throw err;
    }
  };
  
  const selectChat = async (chatId) => {
    try {
      return await chatStore.selectChat(chatId);
    } catch (err) {
      logger.error('选择对话失败:', err);
      throw err;
    }
  };
  
  const sendMessage = async (content, model, deepThinking = false, webSearchEnabled = false, files = []) => {
    try {
      return await chatStore.sendMessage(content, model, deepThinking, webSearchEnabled, files);
    } catch (err) {
      logger.error('发送消息失败:', err);
      throw err;
    }
  };
  
  const deleteChat = async (chatId) => {
    try {
      return await chatStore.deleteChat(chatId);
    } catch (err) {
      logger.error('删除对话失败:', err);
      throw err;
    }
  };
  
  const clearAllChats = async () => {
    try {
      return await chatStore.clearAllChats();
    } catch (err) {
      logger.error('清空所有对话失败:', err);
      throw err;
    }
  };
  
  const loadChatHistory = async (manualRetry = false) => {
    try {
      return await chatStore.loadChatHistory(manualRetry);
    } catch (err) {
      logger.error('加载对话历史失败:', err);
      throw err;
    }
  };
  
  const togglePinChat = async (chatId) => {
    try {
      return await chatStore.togglePinChat(chatId);
    } catch (err) {
      logger.error('切换对话置顶状态失败:', err);
      throw err;
    }
  };
  
  const renameChat = async (chatId, newTitle) => {
    try {
      return await chatStore.renameChat(chatId, newTitle);
    } catch (err) {
      logger.error('重命名对话失败:', err);
      throw err;
    }
  };
  
  const resetUnreadStatus = () => {
    chatStore.resetUnreadStatus();
  };
  
  const batchDeleteChats = async (chatIds) => {
    try {
      return await chatStore.batchDeleteChats(chatIds);
    } catch (err) {
      logger.error('批量删除对话失败:', err);
      throw err;
    }
  };
  
  const cancelStreaming = () => {
    chatStore.cancelStreaming();
  };
  
  const exportChatHistory = (chatId) => {
    return chatStore.exportChatHistory(chatId);
  };
  
  const getCurrentChatTitle = () => {
    return chatStore.getCurrentChatTitle();
  };
  
  const getModelAdapter = () => {
    return chatStore.getModelAdapter();
  };
  
  const getMessageAdapter = () => {
    return chatStore.getMessageAdapter();
  };
  
  return {
    // 响应式状态
    chats,
    currentChatId,
    isLoading,
    error,
    
    // 计算属性
    currentChat,
    currentChatMessages,
    chatHistory,
    standardizedModels,
    
    // 方法
    createNewChat,
    selectChat,
    sendMessage,
    deleteChat,
    clearAllChats,
    loadChatHistory,
    togglePinChat,
    renameChat,
    resetUnreadStatus,
    batchDeleteChats,
    cancelStreaming,
    exportChatHistory,
    getCurrentChatTitle,
    getModelAdapter,
    getMessageAdapter,
    
    // 原始chatStore实例（仅在必要时使用）
    rawStore: chatStore
  };
}