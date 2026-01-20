import { ref } from 'vue';

/**
 * 生成唯一ID
 * @param {string} prefix - ID前缀
 * @returns {string} 唯一ID
 */
export const generateId = (prefix = 'id') => {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * 本地存储工具类
 */
export class StorageManager {
  /**
   * 从本地存储获取数据
   * @param {string} key - 存储键名
   * @param {any} defaultValue - 默认值
   * @returns {any} 存储的数据或默认值
   */
  static getItem(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error(`Error reading from localStorage key: ${key}`, error);
      return defaultValue;
    }
  }

  /**
   * 保存数据到本地存储
   * @param {string} key - 存储键名
   * @param {any} value - 要存储的值
   * @returns {boolean} 是否保存成功
   */
  static setItem(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error(`Error saving to localStorage key: ${key}`, error);
      return false;
    }
  }

  /**
   * 从本地存储删除数据
   * @param {string} key - 存储键名
   * @returns {boolean} 是否删除成功
   */
  static removeItem(key) {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error(`Error removing from localStorage key: ${key}`, error);
      return false;
    }
  }

  /**
   * 清空所有本地存储
   * @returns {boolean} 是否清空成功
   */
  static clear() {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error('Error clearing localStorage', error);
      return false;
    }
  }
}

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
 * 格式化日期时间
 * @param {Date|string|number} date - 日期对象或时间戳
 * @param {string} format - 格式化字符串
 * @returns {string} 格式化后的日期时间字符串
 */
export const formatDateTime = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!date) return '';
  const d = new Date(date);

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
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
 * 创建可持久化的ref
 * @param {string} key - 存储键名
 * @param {any} defaultValue - 默认值
 * @returns {Object} 可持久化的ref对象
 */
export const createPersistedRef = (key, defaultValue) => {
  const value = ref(StorageManager.getItem(key, defaultValue));

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
 * 格式化时间（相对时间）
 * @param {number|string} timestamp - 时间戳
 * @returns {string} 格式化后的时间字符串
 */
export const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  // 计算分钟、小时、天的差值
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  // 根据差值返回不同的时间格式
  if (minutes < 1) {
    return '刚刚';
  } else if (minutes < 60) {
    return `${minutes}分钟前`;
  } else if (hours < 24) {
    return `${hours}小时前`;
  } else if (days < 7) {
    return `${days}天前`;
  } else {
    // 超过一周显示具体日期
    return formatDateTime(date, 'YYYY-MM-DD');
  }
};

/**
 * 格式化日期（用于聊天列表等）
 * @param {number|string} timestamp - 时间戳
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  const now = new Date();
  
  // 如果是今天，显示时间
  if (date.toDateString() === now.toDateString()) {
    return formatDateTime(date, 'HH:mm');
  }
  
  // 如果是昨天，显示"昨天 HH:mm"
  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) {
    return `昨天 ${formatDateTime(date, 'HH:mm')}`;
  }
  
  // 如果是今年，显示"MM-DD HH:mm"
  if (date.getFullYear() === now.getFullYear()) {
    return formatDateTime(date, 'MM-DD HH:mm');
  }
  
  // 其他情况显示完整日期"YYYY-MM-DD HH:mm"
  return formatDateTime(date, 'YYYY-MM-DD HH:mm');
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
    console.error('复制失败:', error);
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
