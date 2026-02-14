import { useRouter } from 'vue-router';
import { useUiStore } from '../store/uiStore';
import { useChatStore } from '../store/chatStore';

export function useNavigation() {
  const router = useRouter();
  const uiStore = useUiStore();
  const chatStore = useChatStore();

  // 导航到首页
  const navigateToHome = () => {
    router.push('/');
    uiStore.setActiveContent('home');
  };

  // 导航到聊天
  const navigateToChat = (chatId) => {
    router.push(`/chat/${chatId}`);
    uiStore.setActiveContent('chat');
  };

  // 导航到设置
  const navigateToSettings = () => {
    router.push('/setting');
    uiStore.setActiveContent('settings');
  };

  // 导航到文件管理器
  const navigateToFileManager = () => {
    router.push('/file');
    uiStore.setActiveContent('fileManager');
  };

  // 导航到RAG管理
  const navigateToRagManagement = () => {
    router.push('/rag');
    uiStore.setActiveContent('ragManagement');
  };

  // 导航到MCP管理
  const navigateToMcpManagement = () => {
    router.push('/mcp');
    uiStore.setActiveContent('mcpManagement');
  };

  // 导航到上下文可视化
  const navigateToContextVisualization = () => {
    router.push('/context');
    uiStore.setActiveContent('contextVisualization');
  };

  // 创建新对话并导航
  const createAndNavigateToNewChat = async (model) => {
    const newChat = chatStore.createNewChat(model);
    if (newChat) {
      navigateToChat(newChat.id);
      return newChat;
    }
    return null;
  };

  return {
    navigateToHome,
    navigateToChat,
    navigateToSettings,
    navigateToFileManager,
    navigateToRagManagement,
    navigateToMcpManagement,
    navigateToContextVisualization,
    createAndNavigateToNewChat
  };
}
