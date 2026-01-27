/**
 * 生成唯一ID
 * @param {string} prefix - ID前缀
 * @returns {string} 唯一ID
 */
export const generateId = (prefix = 'id') => {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
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
