import { ROUTES } from '../router/constants.js';

export const stateRouterService = {
  // 处理状态驱动的路由更新
  updateRouteFromState(newChatId, currentPath, router) {
    console.log('currentChatId变化:', newChatId);
    
    if (newChatId) {
      // 有对话ID，确保路由是对应的聊天路径
      const expectedPath = `/chat/${newChatId}`;
      if (currentPath !== expectedPath && !currentPath.includes('/setting')) {
        console.log('更新路由到对话:', expectedPath);
        router.push(expectedPath);
      }
    } else if (!currentPath.includes('/setting')) {
      // 没有对话ID且不在设置页面，确保路由是根路径
      if (currentPath !== ROUTES.HOME) {
        console.log('更新路由到首页:', ROUTES.HOME);
        router.push(ROUTES.HOME);
      }
    }
  }
};
