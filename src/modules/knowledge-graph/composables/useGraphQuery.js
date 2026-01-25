import { ref, computed } from 'vue';
import { graphApi } from '../api/graphApi.js';
import { showNotification } from '../../../shared/utils/notificationUtils.js';
import logger from '../../../shared/utils/logger.js';

/**
 * 知识图谱查询组合函数，用于处理图谱查询和节点管理
 * @returns {Object} 包含图谱查询功能的对象
 */
export function useGraphQuery() {
  // 响应式状态
  const graphData = ref({ nodes: [], links: [] });
  const isLoading = ref(false);
  const error = ref(null);
  const searchKeyword = ref('');
  const selectedNode = ref(null);
  const graphStats = ref(null);

  // 计算属性
  const nodeCount = computed(() => graphData.value.nodes.length);
  const linkCount = computed(() => graphData.value.links.length);

  /**
   * 查询知识图谱
   * @param {Object} query - 查询条件
   * @returns {Promise<Object>} 查询结果
   */
  const queryGraph = async (query = {}) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await graphApi.queryGraph(query);
      graphData.value = response.data || { nodes: [], links: [] };
      logger.info('成功查询知识图谱', { nodeCount: nodeCount.value, linkCount: linkCount.value });
      return graphData.value;
    } catch (err) {
      error.value = err.message || '查询图谱失败';
      logger.error('查询图谱失败:', err);
      showNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 获取节点详情
   * @param {string} nodeId - 节点ID
   * @returns {Promise<Object>} 节点详情
   */
  const getNodeDetails = async (nodeId) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await graphApi.getNodeDetails(nodeId);
      selectedNode.value = response.data;
      logger.info('成功获取节点详情', { nodeId });
      return selectedNode.value;
    } catch (err) {
      error.value = err.message || '获取节点详情失败';
      logger.error('获取节点详情失败:', err);
      showNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 获取节点的关联节点
   * @param {string} nodeId - 节点ID
   * @param {Object} options - 查询选项
   * @returns {Promise<Object>} 关联节点列表
   */
  const getNodeNeighbors = async (nodeId, options = {}) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await graphApi.getNodeNeighbors(nodeId, options);
      logger.info('成功获取关联节点', { nodeId, neighborCount: response.data?.nodes?.length });
      return response.data;
    } catch (err) {
      error.value = err.message || '获取关联节点失败';
      logger.error('获取关联节点失败:', err);
      showNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 搜索图谱节点
   * @param {string} keyword - 搜索关键词
   * @param {Object} options - 搜索选项
   * @returns {Promise<Object>} 搜索结果
   */
  const searchNodes = async (keyword, options = {}) => {
    try {
      isLoading.value = true;
      error.value = null;
      searchKeyword.value = keyword;
      
      const response = await graphApi.searchNodes(keyword, options);
      logger.info('成功搜索节点', { keyword, resultCount: response.data?.nodes?.length });
      return response.data;
    } catch (err) {
      error.value = err.message || '搜索节点失败';
      logger.error('搜索节点失败:', err);
      showNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 获取图谱统计信息
   * @returns {Promise<Object>} 统计信息
   */
  const loadGraphStats = async () => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await graphApi.getGraphStats();
      graphStats.value = response.data;
      logger.info('成功加载图谱统计信息', { stats: graphStats.value });
      return graphStats.value;
    } catch (err) {
      error.value = err.message || '加载统计信息失败';
      logger.error('加载统计信息失败:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 选择节点
   * @param {Object} node - 节点对象
   */
  const selectNode = (node) => {
    selectedNode.value = node;
    logger.info('选择节点', { nodeId: node.id, nodeName: node.name });
  };

  /**
   * 清除选择的节点
   */
  const clearSelectedNode = () => {
    selectedNode.value = null;
    logger.info('清除选择节点');
  };

  /**
   * 重置图谱数据
   */
  const resetGraph = () => {
    graphData.value = { nodes: [], links: [] };
    selectedNode.value = null;
    searchKeyword.value = '';
    error.value = null;
    logger.info('重置图谱数据');
  };

  return {
    // 状态
    graphData,
    isLoading,
    error,
    searchKeyword,
    selectedNode,
    graphStats,
    
    // 计算属性
    nodeCount,
    linkCount,
    
    // 方法
    queryGraph,
    getNodeDetails,
    getNodeNeighbors,
    searchNodes,
    loadGraphStats,
    selectNode,
    clearSelectedNode,
    resetGraph
  };
}