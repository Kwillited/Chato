import { useSettingsStore } from '../../app/store/settingsStore.js';
import logger from './logger.js';

/**
 * 创建并显示通知元素
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型（success或error）
 * @param {number} displayTime - 显示时间（毫秒）
 */
function createNotificationElement(message, type, displayTime) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-y-0 opacity-100`;
    
    // 根据类型设置样式
    if (type === 'success') {
        notification.classList.add('bg-green-100', 'text-green-800', 'border', 'border-green-200');
    } else {
        notification.classList.add('bg-red-100', 'text-red-800', 'border', 'border-red-200');
    }

    notification.textContent = message;
    document.body.appendChild(notification);
    
    // 时间后自动消失
    setTimeout(() => {
        notification.classList.add('translate-y-full', 'opacity-0');
        setTimeout(() => notification.remove(), 300);
    }, displayTime);
}

/**
 * 显示通知消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型（success或error）
 * @param {number} displayTimeMs - 可选的显示时间（毫秒），默认3秒
 * @param {boolean} isNewMessage - 是否为新消息通知
 */
export function showNotification(message, type, displayTimeMs = 3000, isNewMessage = false) {
    try {
        // 获取设置
        const settingsStore = useSettingsStore();
        const notificationsConfig = settingsStore.currentNotificationsConfig;
            
        // 检查通知是否应该显示
        if (isNewMessage && !notificationsConfig.newMessage) {
            return; // 如果是新消息但用户禁用了新消息通知，则不显示
        }
        
        // 如果是系统通知但用户禁用了系统通知，则不显示
        if (!isNewMessage && !notificationsConfig.system) {
            return;
        }
        
        // 根据设置获取显示时间
        const timeSetting = notificationsConfig.displayTime || '5秒';
        let actualDisplayTime = displayTimeMs;
        
        switch (timeSetting) {
            case '2秒':
                actualDisplayTime = 2000;
                break;
            case '5秒':
                actualDisplayTime = 5000;
                break;
            case '10秒':
                actualDisplayTime = 10000;
                break;
            default:
                actualDisplayTime = displayTimeMs;
        }
        
        // 创建通知元素
        createNotificationElement(message, type, actualDisplayTime);
        
        // 如果启用了声音，播放提示音
        if (notificationsConfig.sound) {
            // 这里可以添加声音播放逻辑
            // const audio = new Audio('/path/to/notification-sound.mp3');
            // audio.play().catch(err => logger.error('播放通知声音失败:', err));
        }
        
        return true;
    } catch (error) {
        logger.error('显示通知失败:', error);
        
        // 如果获取设置失败，使用默认行为显示通知
        try {
            createNotificationElement(message, type, displayTimeMs);
        } catch (innerError) {
            logger.error('使用默认设置显示通知也失败:', innerError);
        }
        
        return false;
    }
}