// MCP工具API服务，处理工具发现、调用等功能
import { apiService } from '../../../shared/api/apiService.js';
import logger from '../../../shared/utils/logger.js';

/**
 * MCP工具API服务
 */
export const mcpApi = {
  /**
   * 获取可用的MCP工具列表
   * @returns {Promise<Object>} 工具列表
   */
  async getTools() {
    try {
      logger.info('获取MCP工具列表');
      return await apiService.get('/mcp/tools');
    } catch (error) {
      logger.error('获取工具列表失败', { error });
      throw error;
    }
  },

  /**
   * 调用指定的MCP工具
   * @param {string} toolId - 工具ID
   * @param {Object} parameters - 工具参数
   * @returns {Promise<Object>} 调用结果
   */
  async callTool(toolId, parameters) {
    try {
      logger.info('调用MCP工具', { toolId });
      return await apiService.post(`/mcp/tools/${toolId}/call`, parameters);
    } catch (error) {
      logger.error('调用工具失败', { toolId, error });
      throw error;
    }
  },

  /**
   * 上传MCP工具
   * @param {File} file - 工具文件
   * @returns {Promise<Object>} 上传结果
   */
  async uploadTool(file) {
    try {
      logger.info('上传MCP工具', { filename: file.name });
      const formData = new FormData();
      formData.append('toolFile', file);
      return await apiService.post('/mcp/tools/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    } catch (error) {
      logger.error('上传工具失败', { filename: file.name, error });
      throw error;
    }
  },

  /**
   * 删除指定的MCP工具
   * @param {string} toolId - 工具ID
   * @returns {Promise<Object>} 删除结果
   */
  async deleteTool(toolId) {
    try {
      logger.info('删除MCP工具', { toolId });
      return await apiService.delete(`/mcp/tools/${toolId}`);
    } catch (error) {
      logger.error('删除工具失败', { toolId, error });
      throw error;
    }
  },

  /**
   * 获取工具调用历史
   * @param {Object} options - 查询选项
   * @returns {Promise<Object>} 调用历史
   */
  async getToolCallHistory(options = {}) {
    try {
      logger.info('获取工具调用历史', { options });
      return await apiService.get('/mcp/history', { params: options });
    } catch (error) {
      logger.error('获取调用历史失败', { options, error });
      throw error;
    }
  }
};