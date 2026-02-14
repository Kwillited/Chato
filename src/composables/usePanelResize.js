import { ref } from 'vue';

/**
 * 面板调整组合式函数
 * 提供面板大小调整的功能
 * @param {Function} leftNavVisible - 左侧导航栏可见性（计算属性）
 * @param {Function} rightPanelVisible - 右侧面板可见性（计算属性）
 * @param {Object} uiStore - UI状态存储
 * @param {Function} updateTitlePosition - 更新标题位置的回调函数
 * @returns {Object} 面板调整相关函数
 */
export function usePanelResize(leftNavVisible, rightPanelVisible, uiStore, updateTitlePosition) {
  // 调整状态
  const isResizing = ref(false);
  let startX = 0;
  let startWidth = 0;
  let resizeType = '';
  let resizeRequestId = null;

  /**
   * 初始化调整
   * @param {Event} e - 鼠标事件
   * @param {string} type - 调整类型：'left' 或 'right'
   */
  const initResize = (e, type) => {
    // 如果面板不可见，不允许调整大小
    if ((type === 'right' && !rightPanelVisible.value) || 
        (type === 'left' && !leftNavVisible.value)) {
      return;
    }
    
    isResizing.value = true;
    resizeType = type;
    startX = e.clientX;
    
    const panelElement = type === 'left' ? document.getElementById('panelContainer') : document.getElementById('rightPanel');
    startWidth = panelElement ? panelElement.offsetWidth : 0;
    
    // 禁用过渡效果以便在拖动时立即响应
    if (panelElement) {
      panelElement.style.transition = 'none';
    }
    
    // 添加调整大小的临时样式
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    const mainContent = document.getElementById('mainContent');
    if (mainContent) {
      mainContent.style.pointerEvents = 'none';
    }
    
    const resizer = document.getElementById(type === 'left' ? 'LeftResizer' : 'RightResizer');
    if (resizer) {
      resizer.classList.add('resizing');
    }
    
    // 添加事件监听器
    document.addEventListener('mousemove', resizePanel);
    document.addEventListener('mouseup', stopResize);
    document.addEventListener('mouseleave', stopResize);
    
    // 阻止默认行为和事件冒泡
    e.preventDefault();
    e.stopPropagation();
  };

  /**
   * 调整面板大小
   * @param {Event} e - 鼠标事件
   */
  const resizePanel = (e) => {
    if (!isResizing.value) return;
    
    // 取消上一个动画帧请求
    if (resizeRequestId) {
      cancelAnimationFrame(resizeRequestId);
    }
    
    // 使用requestAnimationFrame优化动画性能
    resizeRequestId = requestAnimationFrame(() => {
      // 获取元素
      const leftPanel = document.getElementById('panelContainer');
      const rightPanel = document.getElementById('rightPanel');
      const mainLayoutContainer = document.getElementById('mainLayoutContainer');
      
      if (!leftPanel || !rightPanel || !mainLayoutContainer) return;
      
      // 计算宽度变化，右侧面板调整方向相反
      const isRightPanel = resizeType === 'right';
      const widthChange = isRightPanel ? (startX - e.clientX) : (e.clientX - startX);
      let newWidth = startWidth + widthChange;
      
      // 设置最小和最大宽度限制
      const minWidth = 200; // 最小宽度为200px
      const panelMaxWidth = 370; // 所有面板的最大宽度为370px
      const mainContentMinWidth = 300; // 主内容区最小宽度
      
      // 获取当前所有面板的宽度
      const leftPanelWidth = leftNavVisible.value ? leftPanel.offsetWidth : 0;
      const rightPanelWidth = rightPanelVisible.value ? rightPanel.offsetWidth : 0;
      
      // 计算可用总宽度
      const availableWidth = mainLayoutContainer.offsetWidth;
      
      // 计算最大宽度：可用总宽度 - 主内容区最小宽度 - 另一侧面板宽度
      let maxWidth;
      if (!isRightPanel) {
        // 左侧面板最大宽度：取计算值和固定最大值中的较小值
        const calculatedMaxWidth = availableWidth - mainContentMinWidth - rightPanelWidth;
        maxWidth = Math.min(panelMaxWidth, calculatedMaxWidth);
      } else {
        // 右侧面板最大宽度：取计算值和固定最大值中的较小值
        const calculatedMaxWidth = availableWidth - mainContentMinWidth - leftPanelWidth;
        maxWidth = Math.min(panelMaxWidth, calculatedMaxWidth);
      }
      
      // 确保最大宽度不小于最小宽度
      maxWidth = Math.max(minWidth, maxWidth);
      
      // 限制新宽度在合理范围内
      newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
      
      // 更新面板宽度
      const panelElement = isRightPanel ? rightPanel : leftPanel;
      panelElement.style.width = `${newWidth}px`;
      
      // 更新store中的宽度
      if (isRightPanel) {
        uiStore.setRightNavWidth(`${newWidth}px`);
      } else {
        uiStore.setLeftNavWidth(`${newWidth}px`);
      }
    });
  };

  /**
   * 停止调整
   */
  const stopResize = () => {
    if (!isResizing.value) return;
    
    isResizing.value = false;
    
    // 重新启用过渡效果
    const leftPanel = document.getElementById('panelContainer');
    const rightPanel = document.getElementById('rightPanel');
    if (leftPanel) {
      leftPanel.style.transition = 'width 0.2s ease-out';
    }
    if (rightPanel) {
      rightPanel.style.transition = 'width 0.2s ease-out';
    }
    
    // 移除临时样式
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
    const mainContent = document.getElementById('mainContent');
    if (mainContent) {
      mainContent.style.pointerEvents = '';
    }
    
    // 移除resizing类
    const leftResizer = document.getElementById('LeftResizer');
    const rightResizer = document.getElementById('RightResizer');
    if (leftResizer) {
      leftResizer.classList.remove('resizing');
    }
    if (rightResizer) {
      rightResizer.classList.remove('resizing');
    }
    
    // 移除事件监听器
    document.removeEventListener('mousemove', resizePanel);
    document.removeEventListener('mouseup', stopResize);
    document.removeEventListener('mouseleave', stopResize);
    
    // 取消最后一个动画帧请求
    if (resizeRequestId) {
      cancelAnimationFrame(resizeRequestId);
      resizeRequestId = null;
    }
    
    // 更新标题位置
    if (updateTitlePosition) {
      updateTitlePosition();
    }
  };

  // 暴露开始调整函数
  const startLeftResize = (e) => initResize(e, 'left');
  const startRightResize = (e) => initResize(e, 'right');

  return {
    isResizing,
    startLeftResize,
    startRightResize
  };
}
