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
    
    <!-- 应用控制按钮 -->
      <div class="flex items-center gap-4 pr-4">
        <!-- 直接显示视图按钮 -->
        <Button 
          icon="fa-columns"
          tooltip="视图"
          @click="toggleViewPanel"
          size="sm"
          shape="full"
        />
        
        <!-- 分隔栏 -->
        <div class="h-4 w-px bg-gray-200 dark:bg-dark-700 mx-1"></div>
        
        <!-- 主题切换按钮 -->
        <Button 
          :icon="settingsStore.systemSettings.darkMode ? 'fa-sun' : 'fa-moon'"
          tooltip="切换主题"
          @click="handleToggleTheme"
          size="sm"
          shape="full"
        />
        
        <Button 
          icon="fa-gear"
          tooltip="系统设置"
          @click="handleSystemSettingsClick"
          size="sm"
          shape="full"
        />
        
        <!-- 用户按钮带下拉菜单 -->
        <div class="relative hover-scale">
            <Button 
              icon="fa-user-circle"
              @click.stop="toggleUserMenu"
              size="sm"
              shape="full"
              class="i:text-base"
            />
          
          <!-- 用户功能下拉菜单 -->
          <div 
            v-if="showUserMenu"
            class="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 w-14 rounded-lg shadow-lg border z-50 dropdown-content flex flex-col items-center py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700"
          >
            <Button 
              icon="fa-exchange"
              tooltip="切换账户"
              @click="handleSwitchAccount"
              size="lg"
              shape="full"
            />
            <div class="my-1 w-8 border-t border-gray-200 dark:border-dark-700"></div>
            <Button 
              icon="fa-arrow-right-from-bracket"
              tooltip="退出账号"
              @click="handleLogout"
              size="lg"
              shape="full"
              class="text-red-500"
            />
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
