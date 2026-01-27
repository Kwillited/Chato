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
