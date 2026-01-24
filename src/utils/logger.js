/**
 * 统一日志工具
 * 支持不同级别的日志记录：debug, info, warn, error
 * 可配置日志级别，控制哪些日志会被输出
 */

// 日志级别枚举
const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

// 默认日志级别
let currentLogLevel = LOG_LEVELS.INFO;

// 日志配置
const logConfig = {
  // 是否显示时间戳
  showTimestamp: true,
  // 是否显示日志级别
  showLevel: true,
  // 是否显示文件名和行号
  showLocation: false
};

/**
 * 获取调用者的位置信息（文件名和行号）
 * @returns {string} 位置信息
 */
function getCallerInfo() {
  if (!logConfig.showLocation) return '';
  
  try {
    const stack = new Error().stack;
    if (stack) {
      const lines = stack.split('\n');
      // 找到调用logger的位置，通常是第3或4行
      const callerLine = lines[4] || lines[3];
      if (callerLine) {
        // 提取文件名和行号
        const match = callerLine.match(/at\s+(?:.*\()?(.*):(\d+):(\d+)/);
        if (match) {
          const [, file, line] = match;
          const fileName = file.split('/').pop();
          return ` [${fileName}:${line}]`;
        }
      }
    }
  } catch (error) {
    // 忽略获取位置信息时的错误
  }
  return '';
}

/**
 * 生成日志前缀
 * @param {string} level - 日志级别
 * @returns {string} 日志前缀
 */
function getLogPrefix(level) {
  const parts = [];
  
  if (logConfig.showTimestamp) {
    const timestamp = new Date().toISOString();
    parts.push(`[${timestamp}]`);
  }
  
  if (logConfig.showLevel) {
    parts.push(`[${level.toUpperCase()}]`);
  }
  
  const callerInfo = getCallerInfo();
  if (callerInfo) {
    parts.push(callerInfo);
  }
  
  return parts.length > 0 ? `${parts.join(' ')} ` : '';
}

/**
 * 日志工具类
 */
export const logger = {
  /**
   * 设置日志级别
   * @param {string|number} level - 日志级别，可以是字符串('debug', 'info', 'warn', 'error')或数字(0-3)
   */
  setLevel(level) {
    if (typeof level === 'string') {
      const levelName = level.toUpperCase();
      if (LOG_LEVELS[levelName] !== undefined) {
        currentLogLevel = LOG_LEVELS[levelName];
      }
    } else if (typeof level === 'number' && level >= 0 && level <= 3) {
      currentLogLevel = level;
    }
  },
  
  /**
   * 获取当前日志级别
   * @returns {number} 当前日志级别
   */
  getLevel() {
    return currentLogLevel;
  },
  
  /**
   * 设置日志配置
   * @param {Object} config - 日志配置
   */
  setConfig(config) {
    logConfig.showTimestamp = config.showTimestamp !== false;
    logConfig.showLevel = config.showLevel !== false;
    logConfig.showLocation = config.showLocation === true;
  },
  
  /**
   * 获取当前日志配置
   * @returns {Object} 当前日志配置
   */
  getConfig() {
    return { ...logConfig };
  },
  
  /**
   * Debug级别日志
   * @param {string} message - 日志消息
   * @param {...any} args - 额外的日志参数
   */
  debug(message, ...args) {
    if (currentLogLevel <= LOG_LEVELS.DEBUG) {
      console.debug(`${getLogPrefix('debug')}${message}`, ...args);
    }
  },
  
  /**
   * Info级别日志
   * @param {string} message - 日志消息
   * @param {...any} args - 额外的日志参数
   */
  info(message, ...args) {
    if (currentLogLevel <= LOG_LEVELS.INFO) {
      console.info(`${getLogPrefix('info')}${message}`, ...args);
    }
  },
  
  /**
   * Warn级别日志
   * @param {string} message - 日志消息
   * @param {...any} args - 额外的日志参数
   */
  warn(message, ...args) {
    if (currentLogLevel <= LOG_LEVELS.WARN) {
      console.warn(`${getLogPrefix('warn')}${message}`, ...args);
    }
  },
  
  /**
   * Error级别日志
   * @param {string} message - 日志消息
   * @param {...any} args - 额外的日志参数
   */
  error(message, ...args) {
    if (currentLogLevel <= LOG_LEVELS.ERROR) {
      console.error(`${getLogPrefix('error')}${message}`, ...args);
    }
  },
  
  /**
   * 日志断言
   * @param {boolean} condition - 断言条件
   * @param {string} message - 断言失败时的消息
   */
  assert(condition, message) {
    if (!condition) {
      this.error(`Assertion failed: ${message}`);
      console.assert(condition, message);
    }
  },
  
  /**
   * 分组日志开始
   * @param {string} label - 分组标签
   */
  group(label) {
    console.group(`${getLogPrefix('info')}${label}`);
  },
  
  /**
   * 分组日志结束
   */
  groupEnd() {
    console.groupEnd();
  }
};

export default logger;