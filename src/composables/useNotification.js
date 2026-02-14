import { useSettingsStore } from '../store/settingsStore.js';
import { showNotification as showNotificationUtil } from '../utils/notificationUtils.js';

/**
 * 通知管理组合式函数
 * 统一管理通知相关功能
 * @returns {Object} 通知相关函数
 */
export function useNotification() {
  const settingsStore = useSettingsStore();

  /**
   * 显示成功通知
   * @param {string} message - 通知消息
   * @param {number} displayTime - 显示时间（毫秒）
   * @returns {boolean} 是否显示成功
   */
  const showSuccess = (message, displayTime = 3000) => {
    return showNotificationUtil(message, 'success', displayTime);
  };

  /**
   * 显示错误通知
   * @param {string} message - 通知消息
   * @param {number} displayTime - 显示时间（毫秒）
   * @returns {boolean} 是否显示成功
   */
  const showError = (message, displayTime = 3000) => {
    return showNotificationUtil(message, 'error', displayTime);
  };

  /**
   * 显示新消息通知
   * @param {string} message - 通知消息
   * @param {number} displayTime - 显示时间（毫秒）
   * @returns {boolean} 是否显示成功
   */
  const showNewMessageNotification = (message, displayTime = 3000) => {
    return showNotificationUtil(message, 'success', displayTime, true);
  };

  /**
   * 播放通知声音
   */
  const playNotificationSound = () => {
    try {
      const notificationsConfig = settingsStore.currentNotificationsConfig;
      
      // 检查是否启用了通知声音，并且在浏览器环境中
      if (notificationsConfig && notificationsConfig.sound && typeof window !== 'undefined' && typeof window.Audio !== 'undefined') {
        // 使用项目中已有的通知音频文件
        const audio = new window.Audio('/src/assets/notice.mp3');
        // 播放声音，并捕获可能的错误
        audio.play().catch(err => {
          console.warn('播放通知声音失败:', err);
        });
      }
    } catch (error) {
      console.error('处理通知声音时出错:', error);
    }
  };

  /**
   * 显示通知并播放声音（用于新消息）
   * @param {string} message - 通知消息
   * @param {number} displayTime - 显示时间（毫秒）
   * @returns {boolean} 是否显示成功
   */
  const showNotificationWithSound = (message, displayTime = 3000) => {
    const result = showNewMessageNotification(message, displayTime);
    playNotificationSound();
    return result;
  };

  return {
    showSuccess,
    showError,
    showNewMessageNotification,
    playNotificationSound,
    showNotificationWithSound
  };
}
