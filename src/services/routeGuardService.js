import { apiService } from './apiService.js';

export const routeGuardService = {
  // 验证对话是否存在并获取数据
  async validateChatExists(chatId, chatStore) {
    try {
      // 首先尝试从本地状态获取
      let success = chatStore.selectChat(chatId);
      const currentChat = chatStore.currentChat;
      const hasEmptyMessages = currentChat && (!currentChat.messages || currentChat.messages.length === 0);
      
      if (!success || hasEmptyMessages) {
        // 从后端获取完整的对话数据
        const chatData = await apiService.chat.getChat(chatId);
        if (chatData && chatData.chat) {
          // 检查对话是否已存在于本地
          const existingChatIndex = chatStore.chats.findIndex(c => c.id === chatId);
          
          // 如果对话不存在于本地，添加到本地状态
          if (!success && existingChatIndex === -1) {
            chatStore.chats.unshift(chatData.chat);
            success = chatStore.selectChat(chatId);
          } else if (existingChatIndex !== -1) {
            // 如果对话存在于本地，更新消息
            chatStore.chats[existingChatIndex].messages = chatData.chat.messages || [];
            // 强制更新currentChatId，确保计算属性重新计算
            chatStore.currentChatId = chatId;
            success = true;
          }
        }
      }
      return success;
    } catch (error) {
      console.error('验证对话失败:', error);
      return false;
    }
  }
};
