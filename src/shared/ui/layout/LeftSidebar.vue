<template>
  <!-- 左侧侧边栏组件 - 基于通用 Sidebar -->
  <Sidebar type="left" default-title="左侧边栏" default-content="左侧边栏内容">
    <template #content>
      <!-- 历史对话面板 -->
      <div v-if="activePanel === 'history'" class="history-panel p-4">
        <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-white">历史对话</h3>
        <div v-if="chatHistory.length > 0" class="chat-history-list space-y-2">
          <button 
            v-for="chat in chatHistory" 
            :key="chat.id" 
            class="w-full text-left p-2 rounded hover:bg-gray-100 dark:hover:bg-dark-700 text-gray-700 dark:text-gray-300 transition-colors"
            @click="selectChat(chat.id)"
          >
            {{ chat.title }}
          </button>
        </div>
        <div v-else class="text-center text-gray-500 dark:text-gray-400 py-4">
          暂无历史对话
        </div>
      </div>
      
      <!-- 设置面板 -->
      <div v-else-if="activePanel === 'settings'" class="settings-panel p-4">
        <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-white">设置</h3>
        <button class="w-full text-left p-2 rounded hover:bg-gray-100 dark:hover:bg-dark-700 text-gray-700 dark:text-gray-300 transition-colors mb-2"
          @click="setActiveContent('settings')"
        >
          应用设置
        </button>
        <button class="w-full text-left p-2 rounded hover:bg-gray-100 dark:hover:bg-dark-700 text-gray-700 dark:text-gray-300 transition-colors"
          @click="setActiveContent('ragManagement')"
        >
          知识库配置
        </button>
      </div>
      
      <!-- 知识库面板 -->
      <div v-else-if="activePanel === 'rag'" class="rag-panel p-4">
        <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-white">知识库</h3>
        <div class="text-gray-600 dark:text-gray-400">
          <p>知识库配置内容</p>
        </div>
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import { computed } from 'vue';
import { useChatStore } from '../../../app/store/chatStore.js';
import { useSettingsStore } from '../../../app/store/settingsStore.js';
import Sidebar from './Sidebar.vue';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();

// 计算属性
const activePanel = computed(() => settingsStore.activePanel);
const chatHistory = computed(() => chatStore.chatHistory);

// 方法
const selectChat = (chatId) => {
  chatStore.selectChat(chatId);
};

const setActiveContent = (content) => {
  settingsStore.setActiveContent(content);
};
</script>

<style scoped>
/* 移除通用样式，已移至 Sidebar.vue */
/* 仅保留特定于左侧侧边栏的样式 */
.chat-history-list {
  /* 历史对话列表特定样式 */
}

.history-panel,
.settings-panel,
.rag-panel {
  /* 各面板特定样式 */
}
</style>