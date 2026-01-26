import { ref, computed, watch } from 'vue';
import { useChatStore } from '../../../app/store/chatStore.js';
import { useNotifications } from './useNotifications.js';
import { useMessageSending } from './useMessageSending.js';
import logger from '../../../shared/utils/logger.js';

/**
 * 聊天消息管理组合函数，统一处理聊天消息相关逻辑
 * @returns {Object} 包含聊天消息管理功能的对象
 */
export function useChatMessages() {
  const chatStore = useChatStore();
  const { showNewMessageNotification } = useNotifications();
  const { sendMessage: sendMessageCore, isSending, sendProgress, messageError } = useMessageSending();

  // 响应式状态
  const messages = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // 计算属性
  const currentChatMessages = computed(() => {
    return chatStore.currentChatMessages || [];
  });

  const lastMessage = computed(() => {
    const msgs = currentChatMessages.value;
    return msgs.length > 0 ? msgs[msgs.length - 1] : null;
  });

  const isLastMessageTyping = computed(() => {
    const lastMsg = lastMessage.value;
    return lastMsg ? lastMsg.isTyping || false : false;
  });

  /**
   * 发送消息
   * @param {string} content - 消息内容
   * @param {string} [modelId] - 模型ID
   * @param {boolean} [deepThinking=false] - 是否启用深度思考
   * @param {boolean} [webSearchEnabled=false] - 是否启用网络搜索
   * @param {Array} [files=[]] - 上传的文件列表
   * @returns {Promise<Object>} 发送结果
   */
  const sendMessage = async (content, modelId, deepThinking = false, webSearchEnabled = false, files = []) => {
    try {
      isLoading.value = true;
      error.value = null;

      // 使用消息发送核心方法
      const result = await sendMessageCore(content, modelId, deepThinking, webSearchEnabled, files);
      return result;
    } catch (err) {
      error.value = err.message || '发送消息失败';
      logger.error('发送消息失败:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 取消正在发送的消息
   */
  const cancelMessage = () => {
    chatStore.cancelMessage();
  };

  /**
   * 编辑消息
   * @param {string} messageId - 消息ID
   * @param {string} newContent - 新的消息内容
   * @returns {Promise<boolean>} 编辑结果
   */
  const editMessage = async (messageId, newContent) => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await chatStore.editMessage(messageId, newContent);
      return result;
    } catch (err) {
      error.value = err.message || '编辑消息失败';
      logger.error('编辑消息失败:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 删除消息
   * @param {string} messageId - 消息ID
   * @returns {Promise<boolean>} 删除结果
   */
  const deleteMessage = async (messageId) => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await chatStore.deleteMessage(messageId);
      return result;
    } catch (err) {
      error.value = err.message || '删除消息失败';
      logger.error('删除消息失败:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 重新生成消息
   * @param {string} messageId - 消息ID
   * @returns {Promise<boolean>} 重新生成结果
   */
  const regenerateMessage = async (messageId) => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await chatStore.regenerateMessage(messageId);
      return result;
    } catch (err) {
      error.value = err.message || '重新生成消息失败';
      logger.error('重新生成消息失败:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 清空聊天消息
   * @returns {Promise<boolean>} 清空结果
   */
  const clearMessages = async () => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await chatStore.clearMessages();
      return result;
    } catch (err) {
      error.value = err.message || '清空消息失败';
      logger.error('清空消息失败:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 处理新消息
   * @param {Object} message - 新消息
   */
  const handleNewMessage = (message) => {
    // 显示新消息通知
    if (message.role === 'ai') {
      showNewMessageNotification('收到新消息');
    }
  };

  // 监听消息变化
  watch(
    () => chatStore.currentChatMessages,
    (newMessages, oldMessages) => {
      messages.value = newMessages;
      
      // 检测新消息
      if (newMessages.length > oldMessages?.length) {
        const newMessage = newMessages[newMessages.length - 1];
        if (newMessage && newMessage.role === 'ai') {
          handleNewMessage(newMessage);
        }
      }
    },
    { deep: true }
  );

  return {
    // 响应式状态
    messages,
    isLoading,
    error,
    
    // 计算属性
    currentChatMessages,
    lastMessage,
    isLastMessageTyping,
    
    // 方法
    sendMessage,
    cancelMessage,
    editMessage,
    deleteMessage,
    regenerateMessage,
    clearMessages,
    handleNewMessage
  };
}
