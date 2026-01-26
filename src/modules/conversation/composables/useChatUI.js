import { ref, computed } from 'vue';

/**
 * 聊天UI状态管理组合函数，封装聊天相关的UI状态和方法
 * @returns {Object} 包含聊天UI相关的状态和方法
 */
export function useChatUI() {
  // UI状态管理
  const messageInput = ref('');
  const activeView = ref('grid'); // 视图模式：'grid'为对话视图，'list'为图谱视图
  const searchQuery = ref('');
  
  // 设置消息输入内容
  const setMessageInput = (value) => {
    messageInput.value = value;
  };
  
  // 清空消息输入
  const clearMessageInput = () => {
    messageInput.value = '';
  };
  
  // 切换视图模式
  const toggleView = () => {
    activeView.value = activeView.value === 'grid' ? 'list' : 'grid';
  };
  
  // 设置视图模式
  const setActiveView = (view) => {
    activeView.value = view;
  };
  
  // 设置搜索关键词
  const setSearchQuery = (query) => {
    searchQuery.value = query;
  };
  
  // 清空搜索关键词
  const clearSearchQuery = () => {
    searchQuery.value = '';
  };
  
  return {
    // 状态
    messageInput,
    activeView,
    searchQuery,
    
    // 方法
    setMessageInput,
    clearMessageInput,
    toggleView,
    setActiveView,
    setSearchQuery,
    clearSearchQuery
  };
}
