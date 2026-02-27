import { useRouter } from 'vue-router';
import { useUiStore } from '../store/uiStore';
import { useChatStore } from '../store/chatStore';
import { ROUTES, ACTIVE_CONTENT } from '../router/constants.js';
import { apiService } from '../services/apiService.js';

export function useNavigation() {
  const router = useRouter();
  const uiStore = useUiStore();
  const chatStore = useChatStore();

  // 通用导航函数
  const navigateTo = (path, content) => {
    router.push(path);
    uiStore.setActiveContent(content);
  };

  // 导航到首页
  const navigateToHome = () => navigateTo(ROUTES.HOME, ACTIVE_CONTENT.HOME);

  // 导航到聊天
  const navigateToChat = (chatId) => {
    router.push(`/chat/${chatId}`);
    uiStore.setActiveContent(ACTIVE_CONTENT.CHAT);
  };

  // 导航到设置
  const navigateToSettings = () => navigateTo(ROUTES.SETTING, ACTIVE_CONTENT.SETTINGS);

  // 导航到文件管理器
  const navigateToFileManager = () => navigateTo(ROUTES.FILE, ACTIVE_CONTENT.FILE_MANAGER);

  // 导航到RAG管理
  const navigateToRagManagement = () => navigateTo(ROUTES.RAG, ACTIVE_CONTENT.RAG_MANAGEMENT);

  // 导航到MCP管理
  const navigateToMcpManagement = () => navigateTo(ROUTES.MCP, ACTIVE_CONTENT.MCP_MANAGEMENT);

  // 导航到上下文可视化
  const navigateToContextVisualization = () => navigateTo(ROUTES.CONTEXT, ACTIVE_CONTENT.CONTEXT_VISUALIZATION);

  // 创建新对话并导航
  const createAndNavigateToNewChat = async (model) => {
    const newChat = chatStore.createNewChat(model);
    if (newChat) {
      navigateToChat(newChat.id);
      return newChat;
    }
    return null;
  };

  // 处理路由变化逻辑
  const handleRouteChange = async (newRoute, router) => {
    // 处理设置页面路由
    if (newRoute.path === ROUTES.SETTING) {
      // 进入设置页面时，保存当前面板状态并隐藏左右侧边栏
      uiStore.previousPanel = uiStore.activePanel;
      uiStore.previousRightPanelVisible = uiStore.rightPanelVisible;
      uiStore.activePanel = 'settings';
      uiStore.rightPanelVisible = false;
      console.log('进入设置页面，隐藏左右侧边栏');
    } else {
      // 离开设置页面时，恢复右侧面板可见性和之前的面板状态
      if (uiStore.activePanel === 'settings') {
        uiStore.activePanel = uiStore.previousPanel || 'history';
        uiStore.rightPanelVisible = uiStore.previousRightPanelVisible;
        console.log('离开设置页面，恢复右侧面板可见性和之前的面板状态');
      }
    }
    
    // 处理 /chat/:uuid 路由
    if (newRoute.name === 'Chat') {
      const uuid = newRoute.params.uuid;
      console.log('路由切换到聊天对话:', uuid);
      
      // 确保对话历史已加载
      try {
        // 首先尝试选择对话
        let success = chatStore.selectChat(uuid);
        
        // 检查对话是否存在且消息是否为空
        const currentChat = chatStore.currentChat;
        const hasEmptyMessages = currentChat && (!currentChat.messages || currentChat.messages.length === 0);
        
        // 如果找不到对话，或者对话存在但消息为空
        if (!success || hasEmptyMessages) {
          console.log('对话未找到或消息为空，从后端获取完整对话:', uuid);
          try {
            // 从后端获取完整的对话数据
            const chatData = await apiService.chat.getChat(uuid);
            if (chatData && chatData.chat) {
              // 检查对话是否已存在于本地
              const existingChatIndex = chatStore.chats.findIndex(c => c.id === uuid);
              
              // 如果对话不存在于本地，添加到本地状态
              if (!success && existingChatIndex === -1) {
                chatStore.chats.unshift(chatData.chat);
                success = chatStore.selectChat(uuid);
              } else if (existingChatIndex !== -1) {
                // 如果对话存在于本地，更新消息
                chatStore.chats[existingChatIndex].messages = chatData.chat.messages || [];
                // 强制更新currentChatId，确保计算属性重新计算
                chatStore.currentChatId = uuid;
                success = true;
              }
            }
          } catch (error) {
            console.error('从后端获取对话失败:', error);
            // 如果从后端获取失败，尝试加载整个对话历史
            if (!success) {
              console.log('从后端获取对话失败，尝试加载对话历史:', uuid);
              await chatStore.loadChatHistory();
              success = chatStore.selectChat(uuid);
            }
          }
        }
        
        if (!success) {
          // 对话不存在，切换到首页
          console.error('对话不存在:', uuid);
          router.push(ROUTES.HOME);
        } else {
          // 对话存在，设置activeContent为chat
          uiStore.setActiveContent(ACTIVE_CONTENT.CHAT);
        }
      } catch (error) {
        console.error('加载对话失败:', error);
        // 加载失败时，切换到首页
        router.push(ROUTES.HOME);
      }
    } else if (newRoute.meta && newRoute.meta.activeContent) {
      // 使用路由的meta字段设置activeContent
      uiStore.setActiveContent(newRoute.meta.activeContent);
      console.log('路由切换到:', newRoute.meta.activeContent);
    }
  };

  // 处理状态驱动路由逻辑
  const handleStateDrivenRouting = (newChatId, currentPath, router) => {
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
  };

  return {
    navigateTo,
    navigateToHome,
    navigateToChat,
    navigateToSettings,
    navigateToFileManager,
    navigateToRagManagement,
    navigateToMcpManagement,
    navigateToContextVisualization,
    createAndNavigateToNewChat,
    handleRouteChange,
    handleStateDrivenRouting
  };
}
