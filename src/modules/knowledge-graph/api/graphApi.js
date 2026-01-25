// 知识图谱API服务，处理图谱查询、节点管理等功能
import { apiService } from '../../../shared/api/apiService.js';
import logger from '../../../shared/utils/logger.js';

/**
 * 知识图谱API服务
 */
export const graphApi = {
  /**
   * 查询知识图谱节点和边
   * @param {Object} query - 查询条件
   * @returns {Promise<Object>} 查询结果
   */
  async queryGraph(query = {}) {
    try {
      logger.info('查询知识图谱', { query });
      return await apiService.post('/graph/query', query);
    } catch (error) {
      logger.error('查询图谱失败', { query, error });
      throw error;
    }
  },

  /**
   * 获取单个节点详情
   * @param {string} nodeId - 节点ID
   * @returns {Promise<Object>} 节点详情
   */
  async getNodeDetails(nodeId) {
    try {
      logger.info('获取节点详情', { nodeId });
      return await apiService.get(`/graph/nodes/${nodeId}`);
    } catch (error) {
      logger.error('获取节点详情失败', { nodeId, error });
      throw error;
    }
  },

  /**
   * 获取节点的关联节点
   * @param {string} nodeId - 节点ID
   * @param {Object} options - 查询选项
   * @returns {Promise<Object>} 关联节点列表
   */
  async getNodeNeighbors(nodeId, options = {}) {
    try {
      logger.info('获取节点关联节点', { nodeId, options });
      return await apiService.get(`/graph/nodes/${nodeId}/neighbors`, { params: options });
    } catch (error) {
      logger.error('获取关联节点失败', { nodeId, options, error });
      throw error;
    }
  },

  /**
   * 搜索图谱节点
   * @param {string} keyword - 搜索关键词
   * @param {Object} options - 搜索选项
   * @returns {Promise<Object>} 搜索结果
   */
  async searchNodes(keyword, options = {}) {
    try {
      logger.info('搜索图谱节点', { keyword, options });
      return await apiService.get('/graph/search', { params: { keyword, ...options } });
    } catch (error) {
      logger.error('搜索节点失败', { keyword, options, error });
      throw error;
    }
  },

  /**
   * 获取图谱统计信息
   * @returns {Promise<Object>} 图谱统计数据
   */
  async getGraphStats() {
    try {
      logger.info('获取图谱统计信息');
      return await apiService.get('/graph/stats');
    } catch (error) {
      logger.error('获取图谱统计信息失败', { error });
      throw error;
    }
  },

  /**
   * 获取图谱布局
   * @param {Object} graphData - 图谱数据
   * @param {string} layoutType - 布局类型
   * @returns {Promise<Object>} 布局结果
   */
  async getGraphLayout(graphData, layoutType = 'force-directed') {
    try {
      logger.info('获取图谱布局', { layoutType });
      return await apiService.post('/graph/layout', { graphData, layoutType });
    } catch (error) {
      logger.error('获取图谱布局失败', { layoutType, error });
      throw error;
    }
  }
};