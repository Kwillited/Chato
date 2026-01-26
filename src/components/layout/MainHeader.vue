<template>
  <div class="main-header border-b border-gray-200 dark:border-dark-700 flex items-center justify-between transition-all duration-300 px-4 py-2 bg-[#F8FAFC] dark:bg-dark-primary">
    <!-- 左侧：操作按钮 -->
    <div class="flex gap-2">
      <!-- 返回按钮（仅在设置、RAG、MCP等非对话界面显示） -->
      <ActionButton 
        v-if="isSettingsOrRagOrMcpView"
        icon="arrow-left"
        title="返回对话"
        @click="handleBackToChat"
      />
      <!-- 非设置界面显示的按钮 -->
      <template v-else>
        <!-- 隐藏左侧面板按钮 -->
        <ActionButton 
          icon="bars"
          title="隐藏左侧面板"
          @click="handleSideMenuToggle"
        />
        <!-- 新增会话按钮 -->
        <ActionButton 
          id="newChat"
          icon="comment-dots"
          title="新对话"
          @click="handleNewChat"
        />
      </template>
    </div>
    
    <!-- 中间：标题绝对居中 -->
    <div class="absolute left-1/2 transform -translate-x-1/2 flex items-center">
      <h2 class="text-lg font-bold text-gray-800 dark:text-white">{{ currentTitle }}</h2>
    </div>
    
    <!-- 右侧：历史对话按钮（带下拉菜单） -->
    <div class="relative hover-scale">
      <ActionButton 
        id="historyChat"
        icon="clock-rotate-left"
        title="历史对话"
        @click.stop="toggleHistoryMenu"
      />
      
      <!-- 历史对话下拉菜单 -->
      <div 
        v-if="showHistoryMenu"
        class="absolute top-full mt-2 right-0 w-64 rounded-lg shadow-lg border z-50 dropdown-content flex flex-col py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700 max-h-96 overflow-y-auto"
      >
        <!-- 下拉菜单标题 -->
        <div class="px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-dark-700">
          历史对话
        </div>
        
        <!-- 历史对话列表 -->
        <div v-if="chatStore.chats.length > 0" class="py-2">
          <button 
            v-for="chat in chatStore.chatHistory" 
            :key="chat.id"
            class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-dark-700 text-gray-700 dark:text-gray-300 transition-colors duration-200 flex items-start gap-2"
            @click="selectChatFromHistory(chat.id)"
          >
            <i class="fa-solid fa-comments text-xs mt-1 flex-shrink-0 text-gray-400 dark:text-gray-500"></i>
            <div class="flex-1 min-w-0 flex items-center justify-between">
              <div class="font-medium truncate">{{ chat.title }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 truncate ml-2 whitespace-nowrap">
                {{ formatDate(chat.updatedAt) }}
              </div>
            </div>
          </button>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="px-4 py-4 text-center text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-2">
          <i class="fa-solid fa-inbox text-xl"></i>
          暂无历史对话
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { formatDate } from '../../store/utils.js';
import ActionButton from '../common/ActionButton.vue';

// 初始化stores
const settingsStore = useSettingsStore();
const chatStore = useChatStore();

// 历史对话菜单状态
const showHistoryMenu = ref(false);

// 处理隐藏左侧面板按钮点击
const handleSideMenuToggle = () => {
  settingsStore.toggleLeftNav();
};

// 处理新对话按钮点击
const handleNewChat = () => {
  settingsStore.setActiveContent('sendMessage');
};

// 切换历史对话下拉菜单显示状态
const toggleHistoryMenu = () => {
  showHistoryMenu.value = !showHistoryMenu.value;
};

// 从历史对话下拉菜单中选择对话
const selectChatFromHistory = (chatId) => {
  // 关闭下拉菜单
  showHistoryMenu.value = false;
  
  // 选择对话
  chatStore.selectChat(chatId);
  
  // 如果当前内容不是聊天视图，切换到聊天视图
  settingsStore.setActiveContent('chat');
};

// 点击外部区域关闭菜单
const closeMenusOnClickOutside = (event) => {
  const menuButtons = document.querySelectorAll('.relative.hover-scale');
  
  let clickedInsideMenu = false;
  menuButtons.forEach(button => {
    if (button.contains(event.target)) {
      clickedInsideMenu = true;
    }
  });
  
  if (!clickedInsideMenu) {
    showHistoryMenu.value = false;
  }
};

// 添加点击外部事件监听

onMounted(() => {
  document.addEventListener('click', closeMenusOnClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', closeMenusOnClickOutside);
});

// 根据当前面板和内容获取标题
const getHeaderTitle = computed(() => {
  const { activePanel, activeContent } = settingsStore;
  
  // 根据activePanel获取标题
  switch (activePanel) {
    case 'history':
      return '历史会话';
    case 'settings':
      return '系统设置';
    case 'rag':
      return '文件管理';
    case 'mcp':
      return 'MCP服务';
    default:
      // 根据activeContent获取标题
      switch (activeContent) {
        case 'chat':
          return '对话';
        case 'sendMessage':
          return '新对话';
        case 'settings':
          return '系统设置';
        case 'aiSettings':
          return 'AI配置';
        case 'ragManagement':
          return '知识库管理';
        case 'contextVisualization':
          return '上下文可视化';
        default:
          return 'ChaTo';
      }
  }
});

// 当前对话标题
const currentTitle = computed(() => {
  // 如果是设置、RAG或MCP界面，使用getHeaderTitle
  if (isSettingsOrRagOrMcpView.value) {
    return getHeaderTitle.value;
  }
  // 否则使用当前对话标题
  return chatStore.currentChat?.title || '当前无对话';
});

// 判断是否为设置、RAG或MCP界面
const isSettingsOrRagOrMcpView = computed(() => {
  const { activePanel, activeContent } = settingsStore;
  return activePanel === 'settings' || activePanel === 'rag' || activePanel === 'mcp' || activeContent === 'settings';
});

// 处理返回对话
const handleBackToChat = () => {
  settingsStore.setActiveContent('chat');
  settingsStore.setActivePanel('history');
};


</script>

<style scoped>
.main-header {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 10;
  margin-top: 2rem; /* 为TopNav留出空间，2rem = 8px * 4 */
}
</style>