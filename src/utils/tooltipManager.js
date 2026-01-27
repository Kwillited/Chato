// 全局 tooltip 管理器，使用 singleton 模式
const tooltipManager = {
  // 全局 tooltip 元素
  tooltipElement: null,
  
  // 初始化 tooltip 元素
  init() {
    if (!this.tooltipElement) {
      // 创建 tooltip 元素
      this.tooltipElement = document.createElement('div');
      this.tooltipElement.className = 'fixed z-50 bg-black/80 text-white px-2 py-1 rounded text-xs shadow-lg custom-tooltip';
      this.tooltipElement.style.display = 'none';
      this.tooltipElement.style.pointerEvents = 'none';
      
      // 添加到 body
      document.body.appendChild(this.tooltipElement);
    }
  },
  
  // 显示 tooltip
  show(options) {
    this.init();
    
    const {
      content,
      position = { top: 0, left: 0 },
      placement = 'bottom'
    } = options;
    
    if (!content) return;
    
    // 更新内容
    this.tooltipElement.textContent = content;
    
    // 更新位置
    this.tooltipElement.style.top = `${position.top}px`;
    this.tooltipElement.style.left = `${position.left}px`;
    
    // 显示 tooltip
    this.tooltipElement.style.display = 'block';
  },
  
  // 隐藏 tooltip
  hide() {
    if (this.tooltipElement) {
      this.tooltipElement.style.display = 'none';
    }
  },
  
  // 销毁 tooltip 元素
  destroy() {
    if (this.tooltipElement && this.tooltipElement.parentNode) {
      this.tooltipElement.parentNode.removeChild(this.tooltipElement);
      this.tooltipElement = null;
    }
  }
};

export default tooltipManager;