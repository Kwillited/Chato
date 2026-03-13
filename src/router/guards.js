import { routeGuardService } from '../services/routeGuardService.js';
import { useChatStore } from '../store/chatStore.js';
import { ROUTES } from './constants.js';

export function setupRouteGuards(router) {
  // 全局前置守卫
  router.beforeEach(async (to, from, next) => {
    // 处理聊天路由
    if (to.name === 'Chat') {
      const chatId = to.params.uuid;
      const chatStore = useChatStore();
      
      try {
        const success = await routeGuardService.validateChatExists(chatId, chatStore);
        if (success) {
          next();
        } else {
          next(ROUTES.HOME);
        }
      } catch (error) {
        console.error('路由守卫验证失败:', error);
        next(ROUTES.HOME);
      }
    } else {
      next();
    }
  });
}
