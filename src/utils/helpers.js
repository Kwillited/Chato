import logger from './logger.js';

/**
 * 生成唯一ID
 * @param {string} prefix - ID前缀
 * @returns {string} 唯一ID
 */
export const generateId = (prefix = 'id') => {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function} 节流后的函数
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * 分组数据
 * @param {Array} array - 要分组的数组
 * @param {Function|string} key - 分组键或分组函数
 * @returns {Object} 分组后的数据
 */
export const groupBy = (array, key) => {
  return array.reduce((result, item) => {
    const groupKey = typeof key === 'function' ? key(item) : item[key];
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {});
};

/**
 * 深拷贝对象
 * @param {any} obj - 要拷贝的对象
 * @returns {any} 拷贝后的对象
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map((item) => deepClone(item));

  const clonedObj = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      clonedObj[key] = deepClone(obj[key]);
    }
  }
  return clonedObj;
};

/**
 * 合并设置对象
 * @param {Object} defaultSettings - 默认设置
 * @param {Object} userSettings - 用户设置
 * @returns {Object} 合并后的设置
 */
export const mergeSettings = (defaultSettings, userSettings) => {
  if (!userSettings || typeof userSettings !== 'object') {
    return { ...defaultSettings };
  }

  const merged = { ...defaultSettings };

  for (const key in userSettings) {
    if (Object.prototype.hasOwnProperty.call(userSettings, key)) {
      const userValue = userSettings[key];
      const defaultValue = merged[key];

      // 如果两个值都是对象且不是数组，递归合并
      if (
        typeof userValue === 'object' &&
        userValue !== null &&
        typeof defaultValue === 'object' &&
        defaultValue !== null &&
        !Array.isArray(userValue) &&
        !Array.isArray(defaultValue)
      ) {
        merged[key] = mergeSettings(defaultValue, userValue);
      } else {
        // 否则直接覆盖
        merged[key] = userValue;
      }
    }
  }

  return merged;
};

/**
 * 验证对象是否为空
 * @param {Object} obj - 要验证的对象
 * @returns {boolean} 是否为空对象
 */
export const isEmptyObject = (obj) => {
  if (obj === null || typeof obj !== 'object') return true;
  return Object.keys(obj).length === 0;
};

/**
 * 验证数组是否为空
 * @param {Array} arr - 要验证的数组
 * @returns {boolean} 是否为空数组
 */
export const isEmptyArray = (arr) => {
  return !Array.isArray(arr) || arr.length === 0;
};

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise<boolean>} 是否复制成功
 */
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    logger.error('复制失败:', error);
    return false;
  }
};

/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * 获取文件图标
 * @param {string} fileName - 文件名
 * @returns {string} 文件图标类名
 */
export const getFileIcon = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase();
  
  const iconMap = {
    txt: 'fa-file-lines',
    pdf: 'fa-file-pdf',
    doc: 'fa-file-word',
    docx: 'fa-file-word',
    md: 'fa-file-lines',
    jpg: 'fa-file-image',
    jpeg: 'fa-file-image',
    png: 'fa-file-image',
    gif: 'fa-file-image',
    csv: 'fa-file-excel',
    xlsx: 'fa-file-excel',
    pptx: 'fa-file-powerpoint'
  };
  
  return iconMap[extension] || 'fa-file';
};

/**
 * 获取文件扩展名
 * @param {string} fileName - 文件名
 * @returns {string} 文件扩展名（带点号）
 */
export const getFileExtension = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase();
  return `.${extension}`;
};

/**
 * 从消息内容中提取思考标签内容
 * @param {string} content - 消息内容
 * @returns {string} 思考标签内容
 */
export const extractThinkingContent = (content) => {
  if (!content) return '';
  
  // 正则表达式模式
  const THINKING_TAG_CONTENT = /<think>([\s\S]*?)<\/think>/;
  
  const match = content.match(THINKING_TAG_CONTENT);
  return match ? match[1] : '';
};



/**
 * 正则表达式常量，避免重复创建
 */
export const REGEX_PATTERNS = {
  THINKING_TAG: /<think>[\s\S]*?<\/think>/g,
  THINKING_TAG_CONTENT: /<think>([\s\S]*?)<\/think>/,
  MARKDOWN_CODE_BLOCK: /```([\s\S]*?)```/g,
  MARKDOWN_INLINE_CODE: /`([^`]+)`/g,
  MARKDOWN_BOLD: /\*\*([\s\S]*?)\*\*/g,
  MARKDOWN_ITALIC: /\*([\s\S]*?)\*/g,
  MARKDOWN_LINK: /\[([^\]]+)\]\(([^\)]+)\)/g,
  MARKDOWN_IMAGE: /!\[([^\]]*)\]\(([^\)]+)\)/g,
  MARKDOWN_HEADING: /^(#{1,6})\s+([\s\S]+)$/gm,
  MARKDOWN_LIST: /^(\s*)([-*+]|\d+\.)\s+([\s\S]+)$/gm,
  MARKDOWN_QUOTE: /^>\s+([\s\S]+)$/gm,
  MARKDOWN_HORIZONTAL_RULE: /^(\*\*\*|---|___)$/gm
};

/**
 * 创建可持久化的ref
 * @param {string} key - 存储键名
 * @param {any} defaultValue - 默认值
 * @returns {Object} 可持久化的ref对象
 */
export const createPersistedRef = (key, defaultValue) => {
  // 避免循环依赖，直接实现防抖逻辑
  const { ref } = require('vue');
  const { StorageManager } = require('./storage.js');
  
  const value = ref(StorageManager.getItem(key, defaultValue));

  // 内部实现防抖逻辑，避免循环依赖
  let timeout;
  const debounce = (func, wait) => {
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  };

  // 监听值变化并保存到本地存储
  const saveToStorage = debounce((newValue) => {
    StorageManager.setItem(key, newValue);
  }, 300);

  value.value = StorageManager.getItem(key, defaultValue);

  // 创建一个包装器，重写value的setter
  return {
    get value() {
      return value.value;
    },
    set value(newValue) {
      value.value = newValue;
      saveToStorage(newValue);
    },
  };
};

/**
 * 格式化消息内容（支持Markdown和思考标签）
 * @param {string} content - 原始消息内容
 * @param {Object} options - 格式化选项
 * @param {boolean} [options.stripThinkingTag=true] - 是否移除思考标签
 * @param {boolean} [options.enableMarkdown=true] - 是否启用Markdown格式化
 * @returns {string} 格式化后的消息内容
 */
export const formatMessageContent = (content, options = {}) => {
  if (!content) return '';
  
  const { 
    stripThinkingTag = true, 
    enableMarkdown = true 
  } = options;
  
  let formattedContent = content;
  
  // 移除思考标签（如果需要）
  if (stripThinkingTag) {
    formattedContent = formattedContent.replace(REGEX_PATTERNS.THINKING_TAG, '');
  }
  
  // 如果启用了Markdown格式化，使用marked库进行转换
  if (enableMarkdown) {
    try {
      // 动态导入marked库，减少直接依赖
      const { marked } = require('../plugins/markdown.js');
      return marked.parse(formattedContent);
    } catch (error) {
      logger.error('Markdown解析错误:', error);
      // 解析失败时，返回原始内容（移除思考标签后）
      return formattedContent.replace(/\n/g, '<br>');
    }
  }
  
  // 不启用Markdown时，只处理换行
  return formattedContent.replace(/\n/g, '<br>');
};
