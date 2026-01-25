// 导出对话模块的公共API

// 组合函数
export * from './composables/useChatBubble';
export * from './composables/useChatHeader';
export * from './composables/useChatManagement';
export * from './composables/useChatMessages';
export * from './composables/useNotifications';

// API服务
export { chatApi } from './api/chatApi';

// 类型定义
export { ChatMessageType } from './types/index';