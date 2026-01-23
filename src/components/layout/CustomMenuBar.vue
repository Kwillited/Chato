<template>
  <!-- Tauri 自定义菜单栏 -->
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
</template>

<script setup>
import { computed } from 'vue';
import { getCurrentWindow } from '@tauri-apps/api/window';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';

// 初始化stores
const settingsStore = useSettingsStore();

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
    const chatStore = useChatStore();
    if (chatStore.currentChatId) {
      chatStore.deleteChat(chatStore.currentChatId);
    }
  }
};
</script>

<style scoped>
/* CustomMenuBar 组件特定样式 */
</style>