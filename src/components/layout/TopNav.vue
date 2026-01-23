<template>
  <!-- 添加 v-if 确保安全，或者保留结构 -->
  <div 
    id="topNav" 
    class="z-50 absolute top-0 left-0 right-0 h-8 flex items-center px-4 bg-light dark:bg-dark-primary transition-all duration-300 select-none" 
    data-tauri-drag-region
  >
    <!-- 1. 窗口控制区域 -->
    <div class="flex items-center gap-6">
      <!-- 只有在 Tauri 环境下才显示红绿灯按钮 -->
      <div class="flex gap-2.5" v-if="isTauriEnv">
        <button class="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 active:bg-red-700 transition-colors duration-200 focus:outline-none" @click="handleClose" title="关闭"></button>
        <button class="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 active:bg-yellow-700 transition-colors duration-200 focus:outline-none" @click="handleMinimize" title="最小化"></button>
        <button class="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 active:bg-green-700 transition-colors duration-200 focus:outline-none" @click="handleMaximize" title="最大化"></button>
      </div>
      <!-- 如果是 Web 环境，显示一个替代的标题或者留空 -->
      <div v-else class="text-xs text-gray-400 font-mono">
        Web Mode
      </div>
    </div>
    
    <!-- 2. 右侧功能按钮区 (已迁移到聊天输入框) -->
    <div class="hidden"></div>
  </div>
  
  <!-- 新增的顶部导航栏容器 -->
  <div 
    id="appTopNav" 
    class="z-40 absolute top-8 left-0 right-0 h-10 flex items-center bg-light dark:bg-dark-primary border-b border-gray-200 dark:border-dark-700 transition-all duration-300"
  >
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
      <!-- 历史会话操作按钮 -->
      <div class="flex gap-2">
        <!-- 导出所有对话按钮 -->
        <button
          id="exportAllBtn"
          class="h-7 w-7 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-blue-400 transition-colors duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-dark-700"
          @click="exportAllChats"
          title="导出所有对话"
        >
          <i class="fa-solid fa-download text-sm"></i>
        </button>
        <!-- 删除所有对话按钮 -->
        <button
          id="deleteAllBtn"
          class="h-7 w-7 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-red-500 dark:hover:text-red-400 transition-colors duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-dark-700"
          @click="deleteAllChats"
          title="删除所有对话"
        >
          <i class="fa-solid fa-trash-can text-sm"></i>
        </button>
      </div>
    </div>
    
    <!-- 主内容区域对应的导航栏部分 -->
    <div 
      class="h-full flex-1 flex items-center justify-between px-4 transition-all duration-300 bg-light dark:bg-dark-primary"
    >
      <!-- 左侧功能按钮组 -->
      <div class="flex items-center gap-2">
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
      
      <!-- 中间标题区域 -->
      <div class="flex items-center justify-center">
        <h2 class="text-lg font-bold text-dark dark:text-white">{{ currentTitle }}</h2>
      </div>
      
      <!-- 右侧功能按钮组 -->
      <div class="flex items-center gap-2">
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
    
    <!-- 右侧面板对应的导航栏部分 -->
    <div 
      class="h-full flex items-center justify-end transition-all duration-300 bg-light dark:bg-dark-primary"
      :style="{
        width: settingsStore.rightPanelVisible ? settingsStore.rightPanelWidth : '0px',
        overflow: 'hidden',
        paddingLeft: settingsStore.rightPanelVisible ? '16px' : '0px',
        paddingRight: settingsStore.rightPanelVisible ? '16px' : '0px',
        visibility: settingsStore.rightPanelVisible ? 'visible' : 'hidden'
      }"
    >
      <!-- 上下文工程操作按钮 -->
      <div class="flex gap-2">
        <!-- 切换视图按钮 -->
        <button
          class="h-7 w-7 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-blue-400 transition-colors duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-dark-700"
          @click="toggleView"
          title="切换到视图"
        >
          <i class="fa-solid fa-sitemap text-sm"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { getCurrentWindow } from '@tauri-apps/api/window';
import { showNotification } from '../../services/notificationUtils.js';
import { Tooltip, Button } from '../library/index.js';
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

// --- 核心修复：环境检测 ---
// 检测 window.__TAURI_INTERNALS__ 是否存在，判断是否在 Tauri 容器中
const isTauriEnv = computed(() => {
  return !!window.__TAURI_INTERNALS__;
});

// 安全的获取 Window 实例
// 如果不在 Tauri 环境，返回 null，避免报错
const getAppWindow = () => {
  if (isTauriEnv.value) {
    try {
      return getCurrentWindow();
    } catch (e) {
      console.warn('获取 Tauri 窗口失败:', e);
      return null;
    }
  }
  return null;
};

// 窗口控制逻辑 - 添加空值检查
const handleMinimize = () => {
  const win = getAppWindow();
  win?.minimize(); // 使用可选链操作符 ?.
};

const handleMaximize = () => {
  const win = getAppWindow();
  win?.toggleMaximize();
};

const handleClose = () => {
  // 导航栏的关闭按钮，根据当前视图执行不同操作
  if (settingsStore.activeContent === 'settings') {
    settingsStore.setActiveContent('chat');
  } else if (settingsStore.activeContent === 'ragManagement') {
    settingsStore.setActiveContent('chat');
  } else {
    // 其他情况下，关闭当前对话
    if (chatStore.currentChatId) {
      chatStore.deleteChat(chatStore.currentChatId);
    }
  }
};

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

// 切换视图
const toggleView = () => {
  // 根据当前视图切换到另一个视图
  if (settingsStore.activeContent === 'chat') {
    settingsStore.setActiveContent('contextVisualization');
  } else {
    settingsStore.setActiveContent('chat');
  }
};

// 选择历史对话
const selectChatFromHistory = handleMenuItemClick((chatId) => {
  chatStore.selectChat(chatId);
  settingsStore.setActiveContent('chat');
});

// 导出所有对话
const exportAllChats = () => {
  showNotification('导出所有对话功能待实现', 'info');
};

// 删除所有对话
const deleteAllChats = () => {
  if (confirm('确定要删除所有对话吗？此操作不可恢复。')) {
    chatStore.chats.forEach(chat => {
      chatStore.deleteChat(chat.id);
    });
    showNotification('所有对话已删除', 'success');
  }
};

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