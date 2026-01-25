import { ref, reactive } from 'vue';
import { mcpApi } from '../api/mcpApi.js';
import { useNotifications } from '../../../composables/useNotifications.js';
import logger from '../../../shared/utils/logger.js';

/**
 * MCP工具执行组合函数，用于处理工具调用和执行逻辑
 * @returns {Object} 包含工具执行功能的对象
 */
export function useToolExecution() {
  const { showSystemNotification } = useNotifications();

  // 响应式状态
  const isExecuting = ref(false);
  const executionResult = ref(null);
  const executionError = ref(null);
  const executionHistory = ref([]);
  const executionProgress = ref(0);

  // 工具执行上下文
  const executionContext = reactive({
    currentToolId: null,
    currentParameters: {},
    executionId: null,
    startTime: null,
    endTime: null
  });

  /**
   * 执行工具调用
   * @param {string} toolId - 工具ID
   * @param {Object} parameters - 工具参数
   * @returns {Promise<Object>} 执行结果
   */
  const executeTool = async (toolId, parameters = {}) => {
    try {
      isExecuting.value = true;
      executionError.value = null;
      executionProgress.value = 0;
      executionResult.value = null;
      
      // 设置执行上下文
      executionContext.currentToolId = toolId;
      executionContext.currentParameters = parameters;
      executionContext.executionId = `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      executionContext.startTime = new Date();
      
      logger.info('开始执行工具', {
        toolId,
        executionId: executionContext.executionId,
        parameters
      });
      
      // 模拟执行进度
      const progressInterval = setInterval(() => {
        if (executionProgress.value < 90) {
          executionProgress.value += Math.random() * 10;
        }
      }, 200);
      
      // 调用工具API
      const response = await mcpApi.callTool(toolId, parameters);
      executionResult.value = response.data;
      
      // 完成执行
      clearInterval(progressInterval);
      executionProgress.value = 100;
      executionContext.endTime = new Date();
      
      showSystemNotification('工具执行成功', 'success');
      logger.info('工具执行成功', {
        toolId,
        executionId: executionContext.executionId,
        resultId: response.data?.id
      });
      
      // 保存到执行历史
      addToExecutionHistory({
        id: executionContext.executionId,
        toolId,
        parameters,
        result: response.data,
        status: 'success',
        startTime: executionContext.startTime,
        endTime: executionContext.endTime
      });
      
      return response;
    } catch (err) {
      executionError.value = err.message || '工具执行失败';
      executionProgress.value = 0;
      executionContext.endTime = new Date();
      
      showSystemNotification(executionError.value, 'error');
      logger.error('工具执行失败:', {
        toolId,
        executionId: executionContext.executionId,
        error: err
      });
      
      // 保存到执行历史
      addToExecutionHistory({
        id: executionContext.executionId,
        toolId,
        parameters,
        error: executionError.value,
        status: 'error',
        startTime: executionContext.startTime,
        endTime: executionContext.endTime
      });
      
      throw err;
    } finally {
      isExecuting.value = false;
    }
  };

  /**
   * 取消工具执行
   * @returns {Promise<void>}
   */
  const cancelExecution = async () => {
    try {
      logger.info('取消工具执行', {
        toolId: executionContext.currentToolId,
        executionId: executionContext.executionId
      });
      
      // 这里可以添加实际的取消逻辑，如果API支持的话
      // await mcpApi.cancelToolExecution(executionContext.executionId);
      
      showSystemNotification('工具执行已取消', 'warning');
      executionContext.endTime = new Date();
      
      // 保存到执行历史
      addToExecutionHistory({
        id: executionContext.executionId,
        toolId: executionContext.currentToolId,
        parameters: executionContext.currentParameters,
        status: 'cancelled',
        startTime: executionContext.startTime,
        endTime: executionContext.endTime
      });
    } catch (err) {
      logger.error('取消工具执行失败:', err);
      showSystemNotification('取消执行失败', 'error');
      throw err;
    } finally {
      isExecuting.value = false;
      executionProgress.value = 0;
    }
  };

  /**
   * 加载执行历史
   * @param {Object} options - 查询选项
   * @returns {Promise<Array>} 执行历史
   */
  const loadExecutionHistory = async (options = {}) => {
    try {
      isExecuting.value = true;
      executionError.value = null;
      
      const response = await mcpApi.getToolCallHistory(options);
      executionHistory.value = response.data || [];
      logger.info('成功加载执行历史', { historyCount: executionHistory.value.length });
      return executionHistory.value;
    } catch (err) {
      executionError.value = err.message || '加载执行历史失败';
      logger.error('加载执行历史失败:', err);
      showSystemNotification(executionError.value, 'error');
      throw err;
    } finally {
      isExecuting.value = false;
    }
  };

  /**
   * 将执行记录添加到历史
   * @param {Object} executionRecord - 执行记录
   */
  const addToExecutionHistory = (executionRecord) => {
    executionHistory.value.unshift(executionRecord);
    // 限制历史记录数量
    if (executionHistory.value.length > 50) {
      executionHistory.value = executionHistory.value.slice(0, 50);
    }
  };

  /**
   * 清除执行结果
   */
  const clearExecutionResult = () => {
    executionResult.value = null;
    executionError.value = null;
    executionProgress.value = 0;
    executionContext.currentToolId = null;
    executionContext.currentParameters = {};
    executionContext.executionId = null;
    executionContext.startTime = null;
    executionContext.endTime = null;
  };

  return {
    // 状态
    isExecuting,
    executionResult,
    executionError,
    executionHistory,
    executionProgress,
    executionContext,
    
    // 方法
    executeTool,
    cancelExecution,
    loadExecutionHistory,
    clearExecutionResult
  };
}