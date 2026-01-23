<template>
  <!-- 新增的顶部导航栏容器 -->
  <div 
    id="appTopNav" 
    class="z-40 absolute top-8 left-0 right-0 h-10 flex items-center bg-light dark:bg-dark-primary border-b border-gray-200 dark:border-dark-700 transition-all duration-300"
  >
    <!-- 始终显示的左侧功能按钮组 -->
    <div class="flex items-center gap-2 ml-4 z-50">
      <!-- 隐藏左侧面板按钮 -->
      <button
        class="h-7 w-7 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-blue-400 transition-colors duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-dark-700"
        @click="toggleSideMenu"
        title="隐藏左侧面板"
      >
        <i class="fa-solid fa-bars text-sm"></i>
      </button>
      
      <!-- 新增会话按钮 -->
      <button
        id="newChat"
        class="h-7 w-7 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-blue-400 transition-colors duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-dark-700"
        @click="handleNewChat"
        title="新对话"
      >
        <i class="fa-solid fa-comment-dots text-sm"></i>
      </button>
    </div>
    
    <!-- 左侧面板对应的导航栏部分 -->
    <div 
      class="h-full flex items-center justify-start transition-all duration-300 bg-light dark:bg-dark-primary"
      :style="{
        width: settingsStore.leftNavVisible ? settingsStore.leftNavWidth : '0px',
        overflow: 'hidden',
        paddingLeft: settingsStore.leftNavVisible ? '16px' : '0px',
        paddingRight: settingsStore.leftNavVisible ? '16px' : '0px',
        visibility: settingsStore.leftNavVisible ? 'visible' : 'hidden'
      }"
    >
      <!-- 历史会话操作按钮已迁移到设置页面 -->
    </div>
    
    <!-- 主内容区域对应的导航栏部分 -->
    <div 
      class="h-full flex-1 flex items-center px-4 transition-all duration-300 bg-light dark:bg-dark-primary"
    >
      <!-- 中间标题区域 - 绝对定位居中 -->
      <div 
        class="absolute left-1/2 transform -translate-x-1/2"
        :style="{
          // 根据左右面板状态调整偏移量
          left: `calc(50% + ${settingsStore.leftNavVisible ? `(${settingsStore.leftNavWidth} / 2)` : '0px'} - ${settingsStore.rightPanelVisible ? `(${settingsStore.rightPanelWidth} / 2)` : '0px'})`
        }"
        v-if="settingsStore.activeContent !== 'sendMessage'"
      >
        <h2 class="text-lg font-bold text-dark dark:text-white">{{ currentTitle }}</h2>
      </div>
    </div>
    
    <!-- 右侧面板对应的导航栏部分 -->
    <div 
      class="h-full flex items-center justify-end transition-all duration-300 bg-light dark:bg-dark-primary"
      :style="{
        paddingLeft: '16px',
        paddingRight: '16px'
      }"
    >
      <!-- 历史对话按钮（带下拉菜单） -->
      <div class="relative">
        <button
          id="historyChat"
          class="h-7 w-7 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-blue-400 transition-colors duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-dark-700"
          @click.stop="toggleHistoryMenu"
          title="历史对话"
        >
          <i class="fa-solid fa-clock-rotate-left text-sm"></i>
        </button>
        
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
          <div v-if="chatHistory.length > 0" class="py-2">
            <button 
              v-for="chat in chatHistory" 
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { showNotification } from '../../services/notificationUtils.js';
import { formatDate } from '../../store/utils.js';
import { useDropdownMenu } from '../../composables/useDropdownMenu.js';
import eventBus, { Events } from '../../services/eventBus.js';

// 初始化stores
const settingsStore = useSettingsStore();
const chatStore = useChatStore();

// --- 顶部导航栏功能状态管理 ---
const userMenuContainer = ref(null);
const showUserMenu = ref(false);

// 当前标题（根据当前视图动态变化）
const currentTitle = computed(() => {
  switch (settingsStore.activeContent) {
    case 'chat':
      return chatStore.currentChat?.title || '聊天';
    case 'settings':
      return '系统设置';
    case 'ragManagement':
      return '知识库';
    case 'sendMessage':
      return '新对话';
    default:
      return settingsStore.activeContent.charAt(0).toUpperCase() + settingsStore.activeContent.slice(1);
  }
});

// 历史对话相关状态
const chatHistory = computed(() => chatStore.chats);
const { 
  isMenuOpen: showHistoryMenu, 
  toggleMenu: toggleHistoryMenu,
  handleMenuItemClick 
} = useDropdownMenu();

// --- 顶部导航栏功能函数 ---
// 切换侧边菜单
const toggleSideMenu = () => {
  settingsStore.toggleLeftNav();
};

// 新对话
const handleNewChat = async () => {
  try {
    await chatStore.createNewChat();
    settingsStore.setActiveContent('sendMessage');
  } catch (error) {
    console.error('创建新对话失败:', error);
    showNotification('创建新对话失败，请稍后重试', 'error');
  }
};



// 选择历史对话
const selectChatFromHistory = handleMenuItemClick((chatId) => {
  chatStore.selectChat(chatId);
  settingsStore.setActiveContent('chat');
});

// --- 原有业务逻辑保持不变 ---
const toggleViewPanel = () => settingsStore.toggleRightPanel();
const handleSystemSettingsClick = () => {
  settingsStore.setActivePanel('settings');
  settingsStore.setActiveContent('settings');
};
const handleToggleTheme = () => settingsStore.toggleDarkMode();

const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value; };
const closeUserMenu = () => { showUserMenu.value = false; };
const handleSwitchAccount = () => {
  closeUserMenu();
  console.log('切换账户');
};
const handleLogout = () => {
  closeUserMenu();
  showNotification('退出账号功能待实现', 'info');
};

const handleClickOutside = (event) => {
  if (showUserMenu.value && userMenuContainer.value) {
    if (!userMenuContainer.value.contains(event.target)) {
      closeUserMenu();
    }
  }
};

// 生命周期钩子
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  
  // 监听对话选择事件，更新当前标题
  eventBus.on(Events.CHAT_SELECTED, () => {
    // 对话选择后，标题会通过计算属性自动更新
  });
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  eventBus.off(Events.CHAT_SELECTED);
});
</script>

<style scoped>
/* 样式保持不变 */
.dropdown-menu {
  transform-origin: top right;
  animation: fadeInDown 0.2s ease-out;
}
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>