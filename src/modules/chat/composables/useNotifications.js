import { computed } from 'vue';
import { useSettingsStore } from '../../../app/store/settingsStore.js';
import { showNotification } from '../../../shared/utils/notificationUtils.js';
import logger from '../../../shared/utils/logger.js';

/**
 * 通知管理组合函数，统一处理通知相关逻辑
 * @returns {Object} 包含通知配置和方法的对象
 */
export function useNotifications() {
  const settingsStore = useSettingsStore();

  // 计算属性
  const notificationConfig = computed(() => {
    return settingsStore.currentNotificationsConfig || {};
  });

  const isNewMessageNotificationEnabled = computed(() => {
    return notificationConfig.value.newMessage || false;
  });

  const isSystemNotificationEnabled = computed(() => {
    return notificationConfig.value.system || false;
  });

  const displayTimeSetting = computed(() => {
    return notificationConfig.value.displayTime || '5秒';
  });

  /**
   * 显示新消息通知
   * @param {string} message - 消息内容
   * @param {string} [type='success'] - 消息类型
   * @param {number} [displayTimeMs=3000] - 显示时间（毫秒）
   */
  const showNewMessageNotification = (message, type = 'success', displayTimeMs = 3000) => {
    if (!isNewMessageNotificationEnabled.value) {
      logger.debug('新消息通知已禁用，跳过显示');
      return;
    }
    showNotification(message, type, displayTimeMs, true);
  };

  /**
   * 显示系统通知
   * @param {string} message - 消息内容
   * @param {string} [type='success'] - 消息类型
   * @param {number} [displayTimeMs=3000] - 显示时间（毫秒）
   */
  const showSystemNotification = (message, type = 'success', displayTimeMs = 3000) => {
    if (!isSystemNotificationEnabled.value) {
      logger.debug('系统通知已禁用，跳过显示');
      return;
    }
    showNotification(message, type, displayTimeMs, false);
  };

  /**
   * 根据通知类型显示通知
   * @param {string} message - 消息内容
   * @param {string} type - 消息类型
   * @param {boolean} isNewMessage - 是否为新消息通知
   * @param {number} [displayTimeMs=3000] - 显示时间（毫秒）
   */
  const showNotificationByType = (message, type, isNewMessage, displayTimeMs = 3000) => {
    if (isNewMessage) {
      showNewMessageNotification(message, type, displayTimeMs);
    } else {
      showSystemNotification(message, type, displayTimeMs);
    }
  };

  return {
    // 计算属性
    notificationConfig,
    isNewMessageNotificationEnabled,
    isSystemNotificationEnabled,
    displayTimeSetting,
    
    // 方法
    showNewMessageNotification,
    showSystemNotification,
    showNotificationByType,
    showNotification
  };
}