// 事件总线服务 - 用于组件间通信
// 注意：EventBus 类已移动到 utils/eventBus.js
import eventBus, { EVENT_TYPES } from '../utils/eventBus';

export { eventBus, EVENT_TYPES };
export default eventBus;
