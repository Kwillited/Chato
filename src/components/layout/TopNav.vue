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
    <!-- 三个面板头部水平布局 -->
    <div class="flex flex-wrap items-center justify-between px-4 h-auto py-2">
      <!-- 历史会话面板头部 -->
      <div class="flex-1 min-w-[250px] p-2">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-bold text-dark dark:text-white">历史会话</h2>
          <div class="flex gap-2">
            <!-- 自定义按钮插槽 -->
            <div class="relative flex items-center justify-center">
              <button class="btn-secondary flex items-center justify-center transition-all duration-300 w-8 h-8 p-1.5 rounded-full text-neutral dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700" id="exportAllBtn">
                <i class="fa-solid fa-download"></i>
              </button>
              <!-- 预渲染的隐藏tooltip，用于获取准确的尺寸 -->
              <div class="absolute left-[-9999px] top-[-9999px] opacity-0 visibility-hidden pointer-events-none whitespace-nowrap bg-black/80 text-white px-2 py-1 rounded text-xs custom-tooltip tooltip-measure">导出所有对话</div>
              <!-- 实际显示的tooltip，使用Teleport挂载到body -->
              <!--teleport start-->
              <!--teleport end-->
            </div>
            <div class="relative flex items-center justify-center">
              <button class="btn-secondary flex items-center justify-center transition-all duration-300 w-8 h-8 p-1.5 rounded-full text-neutral dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700" id="deleteAllBtn">
                <i class="fa-solid fa-trash-can"></i>
              </button>
              <!-- 预渲染的隐藏tooltip，用于获取准确的尺寸 -->
              <div class="absolute left-[-9999px] top-[-9999px] opacity-0 visibility-hidden pointer-events-none whitespace-nowrap bg-black/80 text-white px-2 py-1 rounded text-xs custom-tooltip tooltip-measure">删除所有对话</div>
              <!-- 实际显示的tooltip，使用Teleport挂载到body -->
              <!--teleport start-->
              <!--teleport end-->
            </div>
          </div>
        </div>
      </div>
      
      <!-- 聊天内容区域头部 -->
      <div class="flex-1 min-w-[250px] p-2">
        <div class="flex justify-between items-center">
          <div class="flex space-x-2">
            <!-- 隐藏左侧面板按钮 -->
            <div class="relative flex items-center justify-center">
              <button class="btn-secondary flex items-center justify-center transition-all duration-300 w-8 h-8 p-1.5 rounded-full text-neutral dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700">
                <i class="fa-solid fa-bars"></i>
              </button>
              <!-- 预渲染的隐藏tooltip，用于获取准确的尺寸 -->
              <div class="absolute left-[-9999px] top-[-9999px] opacity-0 visibility-hidden pointer-events-none whitespace-nowrap bg-black/80 text-white px-2 py-1 rounded text-xs custom-tooltip tooltip-measure">隐藏左侧面板</div>
              <!-- 实际显示的tooltip，使用Teleport挂载到body -->
              <!--teleport start-->
              <!--teleport end-->
            </div>
            <!-- 新增会话按钮 -->
            <div class="relative flex items-center justify-center">
              <button class="btn-secondary flex items-center justify-center transition-all duration-300 w-8 h-8 p-1.5 rounded-full text-neutral dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700" id="newChat">
                <i class="fa-solid fa-comment-dots"></i>
              </button>
              <!-- 预渲染的隐藏tooltip，用于获取准确的尺寸 -->
              <div class="absolute left-[-9999px] top-[-9999px] opacity-0 visibility-hidden pointer-events-none whitespace-nowrap bg-black/80 text-white px-2 py-1 rounded text-xs custom-tooltip tooltip-measure">新对话</div>
              <!-- 实际显示的tooltip，使用Teleport挂载到body -->
              <!--teleport start-->
              <!--teleport end-->
            </div>
          </div>
          <!-- 历史对话按钮（带下拉菜单） -->
          <div class="relative hover-scale">
            <div class="relative flex items-center justify-center">
              <button class="btn-secondary flex items-center justify-center transition-all duration-300 w-8 h-8 p-1.5 rounded-full text-neutral dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700" id="historyChat">
                <i class="fa-solid fa-clock-rotate-left"></i>
              </button>
              <!-- 预渲染的隐藏tooltip，用于获取准确的尺寸 -->
              <div class="absolute left-[-9999px] top-[-9999px] opacity-0 visibility-hidden pointer-events-none whitespace-nowrap bg-black/80 text-white px-2 py-1 rounded text-xs custom-tooltip tooltip-measure">历史对话</div>
              <!-- 实际显示的tooltip，使用Teleport挂载到body -->
              <!--teleport start-->
              <!--teleport end-->
            </div>
          </div>
        </div>
      </div>
      
      <!-- 上下文工程面板头部 -->
      <div class="flex-1 min-w-[250px] p-2">
        <div class="flex items-center justify-between gap-2">
          <h2 class="text-lg font-bold text-dark dark:text-white flex-1">上下文工程</h2>
          <div class="relative flex items-center justify-center">
            <button class="btn-secondary flex items-center justify-center transition-all duration-300 w-8 h-8 p-1.5 rounded-full text-neutral dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700">
              <i class="fa-solid fa-sitemap"></i>
            </button>
            <!-- 预渲染的隐藏tooltip，用于获取准确的尺寸 -->
            <div class="absolute left-[-9999px] top-[-9999px] opacity-0 visibility-hidden pointer-events-none whitespace-nowrap bg-black/80 text-white px-2 py-1 rounded text-xs custom-tooltip tooltip-measure">切换到上下文工程可视化视图</div>
            <!-- 实际显示的tooltip，使用Teleport挂载到body -->
            <!--teleport start-->
            <!--teleport end-->
          </div>
          <div class="relative flex items-center justify-center">
            <button class="btn-secondary flex items-center justify-center transition-all duration-300 w-8 h-8 p-1.5 rounded-full text-neutral dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700">
              <i class="fa-solid fa-times"></i>
            </button>
            <!-- 预渲染的隐藏tooltip，用于获取准确的尺寸 -->
            <div class="absolute left-[-9999px] top-[-9999px] opacity-0 visibility-hidden pointer-events-none whitespace-nowrap bg-black/80 text-white px-2 py-1 rounded text-xs custom-tooltip tooltip-measure">关闭面板</div>
            <!-- 实际显示的tooltip，使用Teleport挂载到body -->
            <!--teleport start-->
            <!--teleport end-->
          </div>
        </div>
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
