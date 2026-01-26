// 事件总线服务 - 用于组件间通信
class EventBus {
  constructor() {
    // 存储事件监听器的映射
    this.listeners = new Map();
  }

  /**
   * 注册事件监听器
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   * @param {Object} [context=null] - 回调函数的上下文
   * @returns {Function} - 取消监听的函数
   */
  on(event, callback, context = null) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }

    // 保存回调函数和上下文
    const listener = { callback, context };
    this.listeners.get(event).add(listener);

    // 返回取消监听的函数
    return () => this.off(event, callback);
  }

  /**
   * 移除事件监听器
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   */
  off(event, callback) {
    if (!this.listeners.has(event)) {
      return;
    }

    const eventListeners = this.listeners.get(event);
    for (const listener of eventListeners) {
      if (listener.callback === callback) {
        eventListeners.delete(listener);
        break;
      }
    }

    // 如果没有监听器了，移除该事件
    if (eventListeners.size === 0) {
      this.listeners.delete(event);
    }
  }

  /**
   * 触发事件
   * @param {string} event - 事件名称
   * @param {*} data - 事件数据
   */
  emit(event, data = null) {
    if (!this.listeners.has(event)) {
      return;
    }

    // 复制监听器集合，防止在回调中修改集合导致问题
    const eventListeners = new Set(this.listeners.get(event));

    for (const { callback, context } of eventListeners) {
      try {
        callback.call(context, data);
      } catch (error) {
        console.error(`Error in event listener for "${event}":`, error);
      }
    }
  }

  /**
   * 注册一次性事件监听器
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   * @param {Object} [context=null] - 回调函数的上下文
   */
  once(event, callback, context = null) {
    const onceCallback = (data) => {
      this.off(event, onceCallback);
      callback.call(context, data);
    };

    this.on(event, onceCallback, context);
    return () => this.off(event, onceCallback);
  }

  /**
   * 清除所有事件监听器
   * @param {string} [event=null] - 可选的事件名称，如果提供则只清除该事件的监听器
   */
  clear(event = null) {
    if (event) {
      this.listeners.delete(event);
    } else {
      this.listeners.clear();
    }
  }

  /**
   * 获取指定事件的监听器数量
   * @param {string} event - 事件名称
   * @returns {number} - 监听器数量
   */
  listenerCount(event) {
    return this.listeners.has(event) ? this.listeners.get(event).size : 0;
  }

  /**
   * 获取所有已注册的事件名称
   * @returns {Array<string>} - 事件名称数组
   */
  getEvents() {
    return Array.from(this.listeners.keys());
  }
}

// 创建事件总线实例
export const eventBus = new EventBus();

// 导出事件类型常量，便于在应用中统一使用
export const EVENT_TYPES = {
  // 对话相关事件
  CHAT_SELECT: 'chat-select',
  NEW_CHAT_CLICKED: 'new-chat-clicked',
  SEND_MESSAGE: 'send-message',
  FILE_UPLOAD: 'file-upload',

  // 导航相关事件
  BACK_TO_CHAT: 'back-to-chat',
  SYSTEM_SETTINGS_CLICK: 'system-settings-click',
  RAG_TOOL_CLICKED: 'rag-tool-clicked',
  MCP_SERVICE_CLICKED: 'mcp-service-clicked',

  // 设置相关事件
  SETTINGS_SECTION_CHANGE: 'settings-section-change',
  MODEL_PARAMS_SAVE: 'model-params-save',
  MODEL_PARAM_CHANGE: 'model-param-change',
  BACK_TO_CHAT_FROM_PARAMS: 'back-to-chat-from-params',
  MODEL_SELECT: 'model-select',
};

export default eventBus;
