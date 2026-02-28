class IconService {
  constructor() {
    this.iconCache = new Map();
  }

  /**
   * 从模型名称中提取供应商名称
   * @param {string} modelName - 模型名称
   * @returns {string} 供应商名称
   */
  extractVendor(modelName) {
    if (!modelName) return 'default';
    
    // 分割模型名称，提取供应商部分
    const parts = modelName.split('-');
    if (parts.length > 0) {
      return parts[0].trim();
    }
    
    // 如果没有 " - " 分隔符，尝试其他常见分隔符
    const altParts = modelName.split(':');
    if (altParts.length > 0) {
      return altParts[0].trim();
    }
    
    // 尝试空格分隔
    const spaceParts = modelName.split(' ');
    if (spaceParts.length > 0) {
      return spaceParts[0].trim();
    }
    
    return modelName;
  }

  /**
   * 生成模型图标 URL
   * @param {string} modelName - 模型名称
   * @returns {string} 图标 URL
   */
  getIconUrl(modelName) {
    const vendor = this.extractVendor(modelName);
    const iconFileName = `${vendor.replace(/\s+/g, '_')}.svg`;
    const iconUrl = `/api/models/icons/${iconFileName}`;
    
    // 预加载图标
    this.preloadIcon(iconUrl);
    
    return iconUrl;
  }

  /**
   * 为模型列表添加图标 URL
   * @param {Array} models - 模型列表
   * @returns {Array} 添加了图标 URL 的模型列表
   */
  addIconUrls(models) {
    return models.map(model => {
      const iconUrl = this.getIconUrl(model.name);
      this.preloadIcon(iconUrl);
      return {
        ...model,
        icon_url: iconUrl
      };
    });
  }

  /**
   * 预加载图标
   * @param {string} iconUrl - 图标 URL
   */
  preloadIcon(iconUrl) {
    if (!this.iconCache.has(iconUrl)) {
      const img = new Image();
      img.src = iconUrl;
      this.iconCache.set(iconUrl, true);
    }
  }

  /**
   * 预加载多个图标
   * @param {Array} modelNames - 模型名称数组
   */
  preloadIcons(modelNames) {
    modelNames.forEach(modelName => {
      const iconUrl = this.getIconUrl(modelName);
      this.preloadIcon(iconUrl);
    });
  }
}

// 导出单例
export default new IconService();