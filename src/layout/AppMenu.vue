<template>
  <div 
    id="appMenuBar" 
    class="z-50 relative top-0 left-0 right-0 h-8 flex items-center px-4 bg-light dark:bg-dark-primary transition-all duration-300" 
    style="-webkit-app-region: drag;"
  >
    <!-- 菜单栏项目 -->
    <div class="flex items-center gap-6" style="-webkit-app-region: drag;">
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
  </div>
  
  <!-- 命令行窗口组件 -->
  <CommandLine 
    :visible="showCommandLine" 
    @close="closeCommandLine"
  />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useSettingsStore } from '../store/settingsStore.js';
import { useUiStore } from '../store/uiStore.js';
import { showNotification } from '../utils/notificationUtils.js';
import CommandLine from '../components/common/CommandLine.vue';
import { Tooltip } from '../components/library/index.js';
import { Button } from '../components/library/index.js';

// 使用全局store管理视图状态
const settingsStore = useSettingsStore();
const uiStore = useUiStore();

// 用户菜单状态
const showUserMenu = ref(false);

// 命令行窗口状态
const showCommandLine = ref(false);

// 处理窗口控制按钮点击事件
const handleMinimize = () => {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.minimize_window();
  } else {
    showNotification('最小化窗口', 'info');
  }
};

const handleMaximize = () => {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.maximize_window();
  } else {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        showNotification(`全屏错误: ${err.message}`, 'error');
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }
};

const handleClose = () => {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.close_window();
  } else {
    window.close();
  }
};

// 处理视图按钮点击事件 - 切换右侧面板
const toggleViewPanel = () => {
  uiStore.toggleRightPanel();
};

// 处理系统设置按钮点击事件
const handleSystemSettingsClick = () => {
  uiStore.setActivePanel('settings');
  uiStore.setActiveContent('settings');
};

// 处理AI配置按钮点击事件
const handleAISettingsClick = () => {
  uiStore.setActiveContent('aiSettings');
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
  uiStore.setActivePanel(panel);
  // 根据面板类型设置默认内容
  switch (panel) {
    case 'history':
      uiStore.setActiveContent('chat');
      break;
    case 'rag':
      uiStore.setActiveContent('fileManager');
      break;
    case 'mcp':
      uiStore.setActiveContent('mcp');
      break;
    case 'settings':
      uiStore.setActiveContent('settings');
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