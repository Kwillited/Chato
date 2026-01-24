import logger from './logger.js';

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
      logger.error(`Error reading from localStorage key: ${key}`, error);
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
      logger.error(`Error saving to localStorage key: ${key}`, error);
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
      logger.error(`Error removing from localStorage key: ${key}`, error);
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
      logger.error('Error clearing localStorage', error);
      return false;
    }
  }
}
