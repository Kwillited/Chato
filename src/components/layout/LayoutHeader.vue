<template>
  <div class="panel-header p-3 flex items-center justify-between border-b border-gray-200 dark:border-dark-700 transition-all duration-300 relative z-50">
    <!-- 左侧：隐藏左侧面板按钮和新增会话按钮 -->
    <div class="flex space-x-2">
      <!-- 隐藏左侧面板按钮和新增会话按钮 - 只在非设置页面显示 -->
      <template v-if="uiStore.activePanel !== 'settings'">
        <!-- 隐藏左侧面板按钮 -->
        <Button 
          shape="full"
          size="md"
          icon="fa-bars"
          tooltip="隐藏左侧面板"
          @click="handleSideMenuToggle"
        />
        <!-- 新增会话按钮 -->
        <Button 
          id="newChat"
          shape="full"
          size="md"
          icon="fa-comment-dots"
          tooltip="新对话"
          @click="handleNewChat"
        />
      </template>
      <!-- 设置面板：返回按钮和系统设置标题 -->
      <div v-else class="flex items-center space-x-1">
        <!-- 返回按钮 -->
        <Button 
          shape="full"
          size="md"
          icon="fa-chevron-left"
          tooltip="返回聊天"
          @click="handleBackToChat"
          class="pr-0"
        />
        <!-- 系统设置标题 -->
        <h2 class="text-lg font-bold text-dark dark:text-white">系统设置</h2>
      </div>
    </div>
    
    <!-- 中间：标题容器 -->
      <div v-if="activeContent === 'chat'" ref="titleContainer" class="flex-1 flex justify-center items-center">
        <h2 class="text-lg font-bold text-gray-800 dark:text-white">{{ getChatTitle() }}</h2>
      </div>
      <div v-else ref="titleContainer" class="flex-1 flex justify-center items-center">
        <!-- 非聊天页面不显示标题 -->
      </div>
    
    <!-- 右侧：历史对话按钮 -->
    <div class="flex space-x-2">
      <!-- 历史对话按钮（带下拉菜单） - 只在非设置页面显示 -->
      <div v-if="activeContent !== 'settings'" class="relative hover-scale">
        <Button 
          id="historyChat"
          shape="full"
          size="md"
          icon="fa-clock-rotate-left"
          tooltip="历史对话"
          @click.stop="toggleHistoryMenu"
        />
        
        <!-- 历史对话下拉菜单 -->
        <div 
          v-if="showHistoryMenu"
          class="absolute top-full mt-2 right-0 w-64 rounded-lg shadow-lg border z-9999 dropdown-content flex flex-col py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700 max-h-96 overflow-y-auto"
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
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUiStore } from '../../store/uiStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { Button } from '../library/index.js';
import { formatDate } from '../../utils/time.js';

// Props
const props = defineProps({
  activeContent: {
    type: String,
    default: 'home'
  }
});

// Stores
const uiStore = useUiStore();
const chatStore = useChatStore();

// State
const showHistoryMenu = ref(false);
const titleContainer = ref(null);

// 获取当前对话标题
const getChatTitle = () => {
  if (props.activeContent === 'chat' && chatStore.currentChat) {
    return chatStore.currentChat.title || '未命名对话';
  }
  if (props.activeContent === 'sendMessage' || props.activeContent === 'home') {
    return '新对话';
  }
  if (props.activeContent === 'settings') {
    return getSettingsTitle();
  }
  if (props.activeContent === 'fileManager') {
    return '文件管理';
  }
  if (props.activeContent === 'contextVisualization') {
    return '上下文可视化';
  }
  if (props.activeContent === 'aiSettings') {
    return 'AI配置';
  }
  return '对话';
};

// 获取设置页面标题
const getSettingsTitle = () => {
  const activeSection = uiStore.activeSection || 'general';
  const sectionTitles = {
    general: '基本设置',
    models: '模型配置',
    notifications: '通知设置',
    about: '关于页面',
    rag: '知识库配置',
    mcp: 'MCP服务设置',
  };
  return sectionTitles[activeSection] || '设置';
};

// Methods
const handleSideMenuToggle = () => {
  uiStore.toggleLeftNav();
};

const handleNewChat = () => {
  chatStore.currentChatId = null;
  chatStore.resetUnreadStatus();
  uiStore.setActiveContent('home');
};

const handleBackToChat = () => {
  uiStore.setActiveContent(uiStore.previousContent || 'home');
  uiStore.setActivePanel('history');
};

const toggleHistoryMenu = () => {
  showHistoryMenu.value = !showHistoryMenu.value;
};

const selectChatFromHistory = (chatId) => {
  showHistoryMenu.value = false;
  chatStore.selectChat(chatId);
  uiStore.setActiveContent('chat');
};

// Expose
defineExpose({
  titleContainer
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
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>