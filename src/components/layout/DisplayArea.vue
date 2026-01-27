<template>
  <div id="displayArea" class="flex-1 flex p-0 pl-0 pr-0 pt-0 bg-light dark:bg-dark-primary overflow-hidden" :class="{ 'transition-all duration-300': !isInitialLoading }">
    <!-- 主内容区域 -->
    <div id="mainContent" class="flex-1 flex flex-col overflow-hidden bg-[#F8FAFC] dark:bg-dark-primary" :class="{ 'transition-all duration-300': !isInitialLoading }">
      <!-- 根据activeContent动态切换内容组件 -->
      <ChatContent v-if="activeContent === 'chat'" />
      <SettingsContent v-if="activeContent === 'settings'" />
      <RagManagementContent v-if="activeContent === 'ragManagement'" />
      <ContextVisualizationContent v-if="activeContent === 'contextVisualization'" />
      <SendMessageContent v-if="activeContent === 'sendMessage'" />
      <AISettingsContent v-if="activeContent === 'aiSettings'" />

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import ChatContent from '../../views/ChatContent.vue'; // 移动到views目录
import SettingsContent from '../../views/SettingsContent.vue'; // 移动到views目录
import RagManagementContent from '../../views/RagManagementContent.vue'; // 移动到views目录
import { ContextVisualizationContent } from '../library';
import SendMessageContent from '../../views/SendMessageContent.vue'; // 新增发送消息视图组件
import AISettingsContent from '../../views/AISettingsContent.vue'; // 新增AI配置视图组件
import { useSettingsStore } from '../../store/settingsStore.js';

// 定义props
const props = defineProps({
  activeContent: {
    type: String,
    default: 'sendMessage' // 默认值改为sendMessage，避免空白chatMainContent
  },
  savedRightPanelWidth: {
    type: String,
    default: '256px'
  },
  isInitialLoading: {
    type: Boolean,
    default: true
  }
});

// 初始化store
const settingsStore = useSettingsStore();

// 组件挂载时初始化
onMounted(() => {
  // 初始化逻辑
});

// 组件卸载时清理
onUnmounted(() => {
  // 清理逻辑
});
</script>