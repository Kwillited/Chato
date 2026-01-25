import { ref, computed } from 'vue';
import { mcpApi } from '../api/mcpApi.js';
import { useNotifications } from '../../../composables/useNotifications.js';
import logger from '../../../shared/utils/logger.js';

/**
 * MCP工具箱组合函数，用于管理工具列表和工具操作
 * @returns {Object} 包含工具箱功能的对象
 */
export function useToolBox() {
  const { showSystemNotification } = useNotifications();

  // 响应式状态
  const tools = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const searchQuery = ref('');

  // 计算属性
  const filteredTools = computed(() => {
    if (!searchQuery.value) return tools.value;
    return tools.value.filter(tool => 
      tool.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      tool.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  });

  /**
   * 加载工具列表
   * @returns {Promise<Array>} 工具列表
   */
  const loadTools = async () => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await mcpApi.getTools();
      tools.value = response.data || [];
      logger.info('成功加载MCP工具列表', { toolCount: tools.value.length });
      return tools.value;
    } catch (err) {
      error.value = err.message || '加载工具列表失败';
      logger.error('加载工具列表失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 上传工具
   * @param {File} file - 工具文件
   * @returns {Promise<Object>} 上传结果
   */
  const uploadTool = async (file) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await mcpApi.uploadTool(file);
      showSystemNotification(`工具上传成功: ${file.name}`, 'success');
      logger.info('工具上传成功', { filename: file.name, toolId: response.data?.id });
      
      // 重新加载工具列表
      await loadTools();
      return response;
    } catch (err) {
      error.value = err.message || '上传工具失败';
      logger.error('上传工具失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 删除工具
   * @param {string} toolId - 工具ID
   * @returns {Promise<Object>} 删除结果
   */
  const deleteTool = async (toolId) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await mcpApi.deleteTool(toolId);
      showSystemNotification('工具删除成功', 'success');
      logger.info('工具删除成功', { toolId });
      
      // 重新加载工具列表
      await loadTools();
      return response;
    } catch (err) {
      error.value = err.message || '删除工具失败';
      logger.error('删除工具失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 搜索工具
   * @param {string} query - 搜索关键词
   */
  const searchTools = (query) => {
    searchQuery.value = query;
    logger.info('搜索工具', { query });
  };

  return {
    // 状态
    tools,
    isLoading,
    error,
    searchQuery,
    
    // 计算属性
    filteredTools,
    
    // 方法
    loadTools,
    uploadTool,
    deleteTool,
    searchTools
  };
}