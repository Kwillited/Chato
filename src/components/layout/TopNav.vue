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
  
  <!-- 命令行窗口组件 -->
  <CommandLine 
    :visible="showCommandLine" 
    @close="closeCommandLine"
  />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { Window } from '@tauri-apps/api/window';
import { showNotification } from '../../services/notificationUtils.js';
import CommandLine from '../../components/common/CommandLine.vue';
import { Tooltip } from '../library/index.js';
import { Button } from '../library/index.js';

// 使用全局store管理视图状态
const settingsStore = useSettingsStore();
const appWindow = new Window('main');

// 用户菜单状态
const showUserMenu = ref(false);

// 命令行窗口状态
const showCommandLine = ref(false);

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
