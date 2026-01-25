import { ref, computed } from 'vue';
import { graphApi } from '../api/graphApi.js';
import logger from '../../../shared/utils/logger.js';

/**
 * 知识图谱布局组合函数，用于处理图谱布局和可视化配置
 * @returns {Object} 包含图谱布局功能的对象
 */
export function useGraphLayout() {
  // 响应式状态
  const layoutType = ref('force-directed');
  const isCalculatingLayout = ref(false);
  const layoutOptions = ref({
    force: {
      gravity: 0.1,
      linkDistance: 100,
      charge: -300
    },
    hierarchical: {
      direction: 'TB',
      spacing: 150
    },
    circular: {
      radius: 300
    }
  });
  const zoomLevel = ref(1);
  const panPosition = ref({ x: 0, y: 0 });
  const isDragging = ref(false);
  const dragStart = ref({ x: 0, y: 0 });

  // 布局类型选项
  const availableLayouts = [
    { value: 'force-directed', label: '力导向布局' },
    { value: 'hierarchical', label: '层次布局' },
    { value: 'circular', label: '环形布局' },
    { value: 'grid', label: '网格布局' }
  ];

  // 计算属性
  const currentLayoutOptions = computed(() => {
    return layoutOptions.value[layoutType.value] || {};
  });

  /**
   * 计算图谱布局
   * @param {Object} graphData - 图谱数据
   * @returns {Promise<Object>} 布局结果
   */
  const calculateLayout = async (graphData) => {
    try {
      isCalculatingLayout.value = true;
      
      logger.info('开始计算图谱布局', { layoutType: layoutType.value });
      
      // 如果没有数据，直接返回
      if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        logger.info('图谱数据为空，跳过布局计算');
        return graphData;
      }
      
      // 调用API计算布局
      const response = await graphApi.getGraphLayout(graphData, layoutType.value);
      
      logger.info('布局计算完成', { layoutType: layoutType.value, nodeCount: response.data.nodes.length });
      return response.data;
    } catch (error) {
      logger.error('计算布局失败:', error);
      throw error;
    } finally {
      isCalculatingLayout.value = false;
    }
  };

  /**
   * 切换布局类型
   * @param {string} type - 布局类型
   * @returns {Promise<Object|null>} 新的布局结果
   */
  const switchLayout = async (type, graphData) => {
    layoutType.value = type;
    logger.info('切换布局类型', { newLayoutType: type });
    
    if (graphData && graphData.nodes.length > 0) {
      return await calculateLayout(graphData);
    }
    return null;
  };

  /**
   * 更新布局选项
   * @param {Object} options - 布局选项
   */
  const updateLayoutOptions = (options) => {
    layoutOptions.value[layoutType.value] = { 
      ...layoutOptions.value[layoutType.value], 
      ...options 
    };
    logger.info('更新布局选项', { layoutType: layoutType.value, options });
  };

  /**
   * 重置布局选项到默认值
   */
  const resetLayoutOptions = () => {
    layoutOptions.value = {
      force: {
        gravity: 0.1,
        linkDistance: 100,
        charge: -300
      },
      hierarchical: {
        direction: 'TB',
        spacing: 150
      },
      circular: {
        radius: 300
      }
    };
    logger.info('重置布局选项');
  };

  /**
   * 设置缩放级别
   * @param {number} level - 缩放级别
   */
  const setZoomLevel = (level) => {
    zoomLevel.value = Math.max(0.1, Math.min(3, level));
    logger.info('设置缩放级别', { zoomLevel: zoomLevel.value });
  };

  /**
   * 缩放操作
   * @param {number} delta - 缩放增量
   */
  const zoom = (delta) => {
    const newLevel = zoomLevel.value + delta * 0.1;
    setZoomLevel(newLevel);
  };

  /**
   * 设置平移位置
   * @param {Object} position - 平移位置
   */
  const setPanPosition = (position) => {
    panPosition.value = position;
    logger.info('设置平移位置', { position });
  };

  /**
   * 平移操作
   * @param {Object} delta - 平移增量
   */
  const pan = (delta) => {
    panPosition.value = {
      x: panPosition.value.x + delta.x,
      y: panPosition.value.y + delta.y
    };
    logger.info('平移操作', { delta });
  };

  /**
   * 开始拖拽
   * @param {Object} position - 拖拽起始位置
   */
  const startDrag = (position) => {
    isDragging.value = true;
    dragStart.value = position;
    logger.info('开始拖拽', { position });
  };

  /**
   * 拖拽中
   * @param {Object} position - 当前位置
   */
  const drag = (position) => {
    if (isDragging.value) {
      const delta = {
        x: position.x - dragStart.value.x,
        y: position.y - dragStart.value.y
      };
      pan(delta);
      dragStart.value = position;
    }
  };

  /**
   * 结束拖拽
   */
  const endDrag = () => {
    isDragging.value = false;
    logger.info('结束拖拽');
  };

  /**
   * 重置视图
   */
  const resetView = () => {
    zoomLevel.value = 1;
    panPosition.value = { x: 0, y: 0 };
    logger.info('重置视图');
  };

  return {
    // 状态
    layoutType,
    isCalculatingLayout,
    layoutOptions,
    zoomLevel,
    panPosition,
    isDragging,
    dragStart,
    availableLayouts,
    
    // 计算属性
    currentLayoutOptions,
    
    // 方法
    calculateLayout,
    switchLayout,
    updateLayoutOptions,
    resetLayoutOptions,
    setZoomLevel,
    zoom,
    setPanPosition,
    pan,
    startDrag,
    drag,
    endDrag,
    resetView
  };
}