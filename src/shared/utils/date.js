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
 * 将显示时间字符串转换为毫秒
 * @param {string} displayTime - 显示时间字符串（如'2秒'）
 * @returns {number} 毫秒数
 */
export const convertDisplayTimeToMs = (displayTime) => {
  const timeMap = {
    '2秒': 2000,
    '5秒': 5000,
    '10秒': 10000
  };
  return timeMap[displayTime] || 3000; // 默认3秒
};
