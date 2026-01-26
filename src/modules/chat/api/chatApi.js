// 对话API服务，处理与聊天相关的所有API请求
import { apiService } from '../../../shared/api/apiService.js';
import logger from '../../../shared/utils/logger.js';

/**
 * 聊天API服务
 */
export const chatApi = {
  /**
   * 发送消息
   * @param {Object} message - 消息对象
   * @param {Object} options - 发送选项
   * @returns {Promise<Object>} 响应结果
   */
  async sendMessage(message, options = {}) {
    try {
      logger.info('发送聊天消息', { message: message.content.substring(0, 50) });
      return await apiService.post('/chat', { message, options });
    } catch (error) {
      logger.error('发送消息失败', { error });
      throw error;
    }
  },

  /**
   * 获取聊天历史
   * @param {string} chatId - 聊天ID
   * @returns {Promise<Object>} 聊天历史
   */
  async getChatHistory(chatId) {
    try {
      logger.info('获取聊天历史', { chatId });
      return await apiService.get(`/chat/${chatId}/history`);
    } catch (error) {
      logger.error('获取聊天历史失败', { chatId, error });
      throw error;
    }
  },

  /**
   * 创建新聊天
   * @returns {Promise<Object>} 新聊天信息
   */
  async createChat() {
    try {
      logger.info('创建新聊天');
      return await apiService.post('/chat');
    } catch (error) {
      logger.error('创建聊天失败', { error });
      throw error;
    }
  },

  /**
   * 删除聊天
   * @param {string} chatId - 聊天ID
   * @returns {Promise<Object>} 删除结果
   */
  async deleteChat(chatId) {
    try {
      logger.info('删除聊天', { chatId });
      return await apiService.delete(`/chat/${chatId}`);
    } catch (error) {
      logger.error('删除聊天失败', { chatId, error });
      throw error;
    }
  }
};