import mitt from 'mitt';

// 创建事件总线实例
const eventBus = mitt();

// 定义事件类型常量
export const Events = {
  // 聊天相关事件
  CHAT_CREATED: 'chat:created',
  CHAT_DELETED: 'chat:deleted',
  CHAT_SELECTED: 'chat:selected',
  MESSAGE_SENT: 'message:sent',
  MESSAGE_RECEIVED: 'message:received',
  MESSAGE_UPDATED: 'message:updated',
  MESSAGE_ERROR: 'message:error',
  CHAT_HISTORY_LOADED: 'chat:historyLoaded',
  
  // 文件相关事件
  FILE_UPLOADED: 'file:uploaded',
  FILE_DELETED: 'file:deleted',
  FOLDER_CREATED: 'folder:created',
  
  // 模型相关事件
  MODEL_UPDATED: 'model:updated',
  MODEL_CONFIG_CHANGED: 'model:configChanged',
  
  // 应用状态相关事件
  APP_INITIALIZED: 'app:initialized',
  APP_ERROR: 'app:error',
  APP_LOADING: 'app:loading',
  APP_LOADING_COMPLETE: 'app:loadingComplete',
  
  // RAG相关事件
  RAG_CONFIG_CHANGED: 'rag:configChanged',
  DOCUMENT_PROCESSED: 'document:processed',
  
  // 系统设置相关事件
  SETTINGS_UPDATED: 'settings:updated',
  
  // 通知相关事件
  NOTIFICATION: 'notification',
  
  // 模态框相关事件
  MODAL_OPEN: 'modal:open',
  MODAL_CLOSE: 'modal:close'
};

// 导出事件总线实例
export default eventBus;