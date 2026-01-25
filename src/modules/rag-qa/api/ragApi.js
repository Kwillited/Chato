// RAG增强模块API服务，处理知识库管理和文件操作
import { apiService } from '../../../shared/api/apiService.js';
import logger from '../../../shared/utils/logger.js';

/**
 * RAG API服务
 */
export const ragApi = {
  /**
   * 获取知识库列表
   * @returns {Promise<Object>} 知识库列表
   */
  async getKnowledgeBases() {
    try {
      logger.info('获取知识库列表');
      return await apiService.get('/rag/knowledge-bases');
    } catch (error) {
      logger.error('获取知识库列表失败', { error });
      throw error;
    }
  },

  /**
   * 创建知识库
   * @param {Object} knowledgeBase - 知识库信息
   * @returns {Promise<Object>} 创建结果
   */
  async createKnowledgeBase(knowledgeBase) {
    try {
      logger.info('创建知识库', { name: knowledgeBase.name });
      return await apiService.post('/rag/knowledge-bases', knowledgeBase);
    } catch (error) {
      logger.error('创建知识库失败', { error });
      throw error;
    }
  },

  /**
   * 删除知识库
   * @param {string} knowledgeBaseId - 知识库ID
   * @returns {Promise<Object>} 删除结果
   */
  async deleteKnowledgeBase(knowledgeBaseId) {
    try {
      logger.info('删除知识库', { knowledgeBaseId });
      return await apiService.delete(`/rag/knowledge-bases/${knowledgeBaseId}`);
    } catch (error) {
      logger.error('删除知识库失败', { knowledgeBaseId, error });
      throw error;
    }
  },

  /**
   * 上传文件到知识库
   * @param {File} file - 文件对象
   * @param {string} knowledgeBaseId - 知识库ID
   * @returns {Promise<Object>} 上传结果
   */
  async uploadFile(file, knowledgeBaseId) {
    try {
      logger.info('上传文件到知识库', { filename: file.name, knowledgeBaseId });
      const formData = new FormData();
      formData.append('file', file);
      return await apiService.post(`/rag/knowledge-bases/${knowledgeBaseId}/files`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    } catch (error) {
      logger.error('上传文件失败', { filename: file.name, error });
      throw error;
    }
  },

  /**
   * 获取知识库中的文件列表
   * @param {string} knowledgeBaseId - 知识库ID
   * @returns {Promise<Object>} 文件列表
   */
  async getFiles(knowledgeBaseId) {
    try {
      logger.info('获取知识库文件列表', { knowledgeBaseId });
      return await apiService.get(`/rag/knowledge-bases/${knowledgeBaseId}/files`);
    } catch (error) {
      logger.error('获取文件列表失败', { knowledgeBaseId, error });
      throw error;
    }
  },

  /**
   * 删除知识库中的文件
   * @param {string} knowledgeBaseId - 知识库ID
   * @param {string} fileId - 文件ID
   * @returns {Promise<Object>} 删除结果
   */
  async deleteFile(knowledgeBaseId, fileId) {
    try {
      logger.info('删除知识库文件', { knowledgeBaseId, fileId });
      return await apiService.delete(`/rag/knowledge-bases/${knowledgeBaseId}/files/${fileId}`);
    } catch (error) {
      logger.error('删除文件失败', { knowledgeBaseId, fileId, error });
      throw error;
    }
  }
};