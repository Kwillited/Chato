import { ref, computed, watch } from 'vue';
import { useChatStore } from '../store/chatStore.js';
import { useNotifications } from './useNotifications.js';
import logger from '../utils/logger.js';

/**
 * 对话管理组合函数，统一处理对话相关逻辑
 * @returns {Object} 包含对话管理功能的对象
 */
export function useChatManagement() {
  const chatStore = useChatStore();
  const { showSystemNotification } = useNotifications();

  // 响应式状态
  const currentChatId = ref(null);
  const searchQuery = ref('');
  const isLoading = ref(false);
  const error = ref(null);

  // 计算属性
  const chats = computed(() => chatStore.chatHistory || []);
  const currentChat = computed(() => chatStore.currentChat || null);
  const chatHistory = computed(() => chatStore.chatHistory || []);

  const filteredChats = computed(() => {
    if (!searchQuery.value.trim()) {
      return chats.value;
    }
    
    const query = searchQuery.value.toLowerCase().trim();
    return chats.value.filter(chat => {
      const title = (chat.title || '').toLowerCase();
      const firstMessage = (chat.messages?.[0]?.content || '').toLowerCase();
      return title.includes(query) || firstMessage.includes(query);
    });
  });

  const chatCount = computed(() => chats.value.length);

  /**
   * 创建新对话
   * @returns {Promise<string>} 新对话ID
   */
  const createNewChat = async () => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await chatStore.handleNewChat();
      currentChatId.value = chatStore.currentChatId;
      showSystemNotification('新对话已创建', 'success');
      return result;
    } catch (err) {
      error.value = err.message || '创建新对话失败';
      logger.error('创建新对话失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 选择对话
   * @param {string} chatId - 对话ID
   * @returns {Promise<boolean>} 选择结果
   */
  const selectChat = async (chatId) => {
    try {
      isLoading.value = true;
      error.value = null;

      await chatStore.handleSelectHistoryChat(chatId);
      currentChatId.value = chatId;
      return true;
    } catch (err) {
      error.value = err.message || '选择对话失败';
      logger.error('选择对话失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 删除对话
   * @param {string} chatId - 对话ID
   * @returns {Promise<boolean>} 删除结果
   */
  const deleteChat = async (chatId) => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await chatStore.deleteChat(chatId);
      showSystemNotification('对话已删除', 'success');
      
      // 如果删除的是当前对话，切换到其他对话或创建新对话
      if (currentChatId.value === chatId) {
        currentChatId.value = null;
      }
      
      return result;
    } catch (err) {
      error.value = err.message || '删除对话失败';
      logger.error('删除对话失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 批量删除对话
   * @param {Array<string>} chatIds - 对话ID数组
   * @returns {Promise<boolean>} 删除结果
   */
  const deleteMultipleChats = async (chatIds) => {
    try {
      isLoading.value = true;
      error.value = null;

      let deletedCount = 0;
      for (const chatId of chatIds) {
        try {
          await chatStore.deleteChat(chatId);
          deletedCount++;
          
          // 如果删除的是当前对话，切换到其他对话或创建新对话
          if (currentChatId.value === chatId) {
            currentChatId.value = null;
          }
        } catch (err) {
          logger.error(`删除对话 ${chatId} 失败:`, err);
        }
      }
      
      showSystemNotification(`成功删除 ${deletedCount} 个对话`, 'success');
      return true;
    } catch (err) {
      error.value = err.message || '批量删除对话失败';
      logger.error('批量删除对话失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 重命名对话
   * @param {string} chatId - 对话ID
   * @param {string} newTitle - 新标题
   * @returns {Promise<boolean>} 重命名结果
   */
  const renameChat = async (chatId, newTitle) => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await chatStore.renameChat(chatId, newTitle);
      showSystemNotification('对话已重命名', 'success');
      return result;
    } catch (err) {
      error.value = err.message || '重命名对话失败';
      logger.error('重命名对话失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 获取当前对话标题
   * @returns {string} 对话标题
   */
  const getCurrentChatTitle = () => {
    return chatStore.getCurrentChatTitle();
  };

  /**
   * 搜索对话
   * @param {string} query - 搜索关键词
   */
  const searchChats = (query) => {
    searchQuery.value = query;
  };

  // 监听当前对话ID变化
  watch(
    () => chatStore.currentChatId,
    (newChatId) => {
      currentChatId.value = newChatId;
    }
  );

  // 初始化当前对话ID
  if (chatStore.currentChatId) {
    currentChatId.value = chatStore.currentChatId;
  }

  return {
    // 响应式状态
    currentChatId,
    searchQuery,
    isLoading,
    error,
    
    // 计算属性
    chats,
    currentChat,
    chatHistory,
    filteredChats,
    chatCount,
    
    // 方法
    createNewChat,
    selectChat,
    deleteChat,
    deleteMultipleChats,
    renameChat,
    getCurrentChatTitle,
    searchChats
  };
}
