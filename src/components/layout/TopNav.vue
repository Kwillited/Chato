<template>
  <div id="topNav" class="z-50 absolute top-0 left-0 right-0 h-8 flex items-center px-4 bg-[#F8FAFC] dark:bg-dark-primary transition-all duration-300" data-tauri-drag-region="">
    <!-- 菜单栏项目 -->
    <div class="flex items-center gap-6" data-tauri-drag-region>
      <!-- Mac风格窗口控制按钮 -->
       <div class="flex gap-2.5 mr-4">
          <Tooltip content="关闭">
            <button class="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors duration-200 focus:outline-none focus:ring-0" @click="handleClose"></button>
          </Tooltip>
          <Tooltip content="最小化">
            <button class="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors duration-200 focus:outline-none focus:ring-0" @click="handleMinimize"></button>
          </Tooltip>
          <Tooltip content="最大化">
            <button class="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors duration-200 focus:outline-none focus:ring-0" @click="handleMaximize"></button>
          </Tooltip>
        </div>
      <!-- NeoVAI标题已删除 -->
    </div>

    <!-- 中间：占位，确保右侧元素靠右 -->
    <div class="flex-1"></div>
    

  </div>
  
  <!-- 导航栏Header -->
  <div id="mainHeader" class="sticky top-8 z-40 bg-white dark:bg-dark-800 border-b border-gray-200 dark:border-gray-700 transition-all duration-300">
    <div class="flex items-center justify-between px-4 h-10">
      <!-- 左侧：导航链接 -->
      <div class="flex items-center">
        <nav class="hidden md:flex space-x-4">
          <button 
            class="px-3 py-1 text-sm font-medium rounded-md transition-colors hover:bg-gray-100 dark:hover:bg-dark-700"
            :class="settingsStore.activePanel === 'history' ? 'text-primary font-semibold' : 'text-gray-600 dark:text-gray-300'"
            @click="navigateTo('history')"
          >
            聊天
          </button>
          <button 
            class="px-3 py-1 text-sm font-medium rounded-md transition-colors hover:bg-gray-100 dark:hover:bg-dark-700"
            :class="settingsStore.activePanel === 'rag' ? 'text-primary font-semibold' : 'text-gray-600 dark:text-gray-300'"
            @click="navigateTo('rag')"
          >
            知识库
          </button>
          <button 
            class="px-3 py-1 text-sm font-medium rounded-md transition-colors hover:bg-gray-100 dark:hover:bg-dark-700"
            :class="settingsStore.activePanel === 'mcp' ? 'text-primary font-semibold' : 'text-gray-600 dark:text-gray-300'"
            @click="navigateTo('mcp')"
          >
            MCP工具
          </button>
          <button 
            class="px-3 py-1 text-sm font-medium rounded-md transition-colors hover:bg-gray-100 dark:hover:bg-dark-700"
            :class="settingsStore.activePanel === 'settings' ? 'text-primary font-semibold' : 'text-gray-600 dark:text-gray-300'"
            @click="navigateTo('settings')"
          >
            设置
          </button>
        </nav>
      </div>
    </div>
  </div>
  
  <!-- 历史会话面板头部 -->
  <div class="panel-header p-3 flex justify-between items-center transition-all duration-300" v-if="settingsStore.activePanel === 'history'">
    <h2 class="text-lg font-bold text-dark dark:text-white">历史会话</h2>
  </div>
  
  <!-- 聊天内容区域头部 -->
  <div class="panel-header p-3 flex flex-wrap items-center justify-end gap-4 relative transition-all duration-300" v-if="settingsStore.activeContent === 'chat' || settingsStore.activeContent === 'sendMessage'">
    <!-- 左侧按钮组 -->
    <div class="absolute left-3 flex space-x-2">
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
    </div>
    
    <!-- 标题绝对居中 -->
    <div class="absolute left-1/2 transform -translate-x-1/2 flex items-center">
      <h2 class="text-lg font-bold text-gray-800 dark:text-white">{{ currentTitle }}</h2>
    </div>
    
    <!-- 右侧按钮组 -->
    <div class="flex space-x-2">
      <!-- 历史对话按钮（带下拉菜单） -->
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
              v-for="chat in chatStore.chats" 
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
  
  <!-- 上下文工程面板头部 -->
  <div class="panel-header p-3 flex items-center justify-between gap-2" v-if="settingsStore.activeContent === 'contextEngineering'">
    <h2 class="text-lg font-bold text-dark dark:text-white flex-1">上下文工程</h2>
    <ActionButton 
      icon="sitemap"
      title="切换到上下文工程可视化视图"
      @click="toggleContextView"
    />
    <ActionButton 
      icon="times"
      title="关闭面板"
      @click="closePanel"
    />
  </div>
  
  <!-- 命令行窗口组件 -->
  <CommandLine 
    :visible="showCommandLine" 
    @close="closeCommandLine"
  />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { Window } from '@tauri-apps/api/window';
import { showNotification } from '../../services/notificationUtils.js';
import CommandLine from '../../components/common/CommandLine.vue';
import ActionButton from '../common/ActionButton.vue';
import { Tooltip } from '../library/index.js';
import { Button } from '../library/index.js';

// 使用全局store管理视图状态
const settingsStore = useSettingsStore();
const chatStore = useChatStore();
const appWindow = new Window('main');

// 用户菜单状态
const showUserMenu = ref(false);

// 命令行窗口状态
const showCommandLine = ref(false);

// 历史对话下拉菜单状态
const showHistoryMenu = ref(false);
const currentTitle = ref('新对话');

// 处理窗口控制按钮点击事件
const handleMinimize = () => {
  appWindow.minimize();
};

const handleMaximize = () => {
  appWindow.toggleMaximize();
};

const handleClose = () => {
  appWindow.close();
};

// 处理视图按钮点击事件 - 切换右侧面板
const toggleViewPanel = () => {
  settingsStore.toggleRightPanel();
};

// 处理系统设置按钮点击事件
const handleSystemSettingsClick = () => {
  settingsStore.setActivePanel('settings');
  settingsStore.setActiveContent('settings');
};

// 处理AI配置按钮点击事件
const handleAISettingsClick = () => {
  settingsStore.setActiveContent('aiSettings');
};

// 切换主题
const handleToggleTheme = () => {
  settingsStore.toggleDarkMode();
};

// 切换用户菜单显示状态
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

// 处理切换账户点击
const handleSwitchAccount = () => {
  showUserMenu.value = false;
  console.log('切换账户');
};

// 处理退出账号点击
const handleLogout = () => {
  showUserMenu.value = false;
  showNotification('退出账号功能待实现', 'info');
};



// 关闭命令行窗口
const closeCommandLine = () => {
  showCommandLine.value = false;
};

// 导航方法
const navigateTo = (panel) => {
  settingsStore.setActivePanel(panel);
  // 根据面板类型设置默认内容
  switch (panel) {
    case 'history':
      settingsStore.setActiveContent('chat');
      break;
    case 'rag':
      settingsStore.setActiveContent('ragManagement');
      break;
    case 'mcp':
      settingsStore.setActiveContent('mcp');
      break;
    case 'settings':
      settingsStore.setActiveContent('settings');
      break;
    default:
      break;
  }
};

// 处理隐藏左侧面板
const handleSideMenuToggle = () => {
  settingsStore.toggleLeftNav();
};

// 处理新增会话
const handleNewChat = () => {
  // 取消当前会话的激活状态
  chatStore.currentChatId = null;
  
  // 清除所有对话的未读标记
  chatStore.chats = chatStore.chats.map(chat => ({
    ...chat,
    hasUnreadMessage: false
  }));
  
  // 切换到发送消息视图
  settingsStore.setActiveContent('sendMessage');
  
  // 更新当前标题
  currentTitle.value = '新对话';
};

// 切换历史对话下拉菜单
const toggleHistoryMenu = () => {
  showHistoryMenu.value = !showHistoryMenu.value;
};

// 从历史对话中选择
const selectChatFromHistory = (chatId) => {
  // 关闭下拉菜单
  showHistoryMenu.value = false;
  
  // 设置当前聊天ID
  chatStore.currentChatId = chatId;
  
  // 切换到聊天视图
  settingsStore.setActiveContent('chat');
  
  // 更新当前标题
  const chat = chatStore.chats.find(c => c.id === chatId);
  if (chat) {
    currentTitle.value = chat.title;
  }
};

// 格式化日期
const formatDate = (timestamp) => {
  if (!timestamp) return '';
  
  const date = new Date(timestamp);
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 切换到上下文工程可视化视图
const toggleContextView = () => {
  // 这里可以添加切换到上下文工程可视化视图的逻辑
  console.log('切换到上下文工程可视化视图');
};

// 关闭面板
const closePanel = () => {
  // 这里可以添加关闭面板的逻辑
  console.log('关闭面板');
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
    showUserMenu.value = false;
  }
};

// 添加点击外部事件监听
onMounted(() => {
  document.addEventListener('click', closeMenusOnClickOutside);
});

// 移除事件监听
onUnmounted(() => {
  document.removeEventListener('click', closeMenusOnClickOutside);
});
</script>

<style scoped>



/* 下拉菜单动画 */
.dropdown-content {
  animation: fadeInDown 0.2s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translate(-50%, -10px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

/* 确保圆形按钮中的图标居中 */
.dropdown-content button i {
  display: flex;
  justify-content: center;
}
</style>
