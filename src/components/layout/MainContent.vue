<template>
  <div id="mainContent" ref="mainContent" class="flex-1 flex flex-col overflow-hidden bg-light dark:bg-dark-primary" :class="{'transition-all duration-300': !isInitialLoading}">
    <!-- 根据activeContent动态切换内容组件 -->
    <ChatContent v-if="activeContent === 'chat'" />
    <SettingsContent v-if="activeContent === 'settings'" />
    <FileMangerContent v-if="activeContent === 'ragManagement' || activeContent === 'fileManager'" />
    <ContextVisualizationContent v-if="activeContent === 'contextVisualization'" />
    <HomeContent v-if="activeContent === 'sendMessage' || activeContent === 'home'" />
    <AISettingsContent v-if="activeContent === 'aiSettings'" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import ChatContent from '../../views/ChatContent.vue';
import SettingsContent from '../../views/SettingsContent.vue';
import FileMangerContent from '../../views/FileMangerContent.vue';
import { ContextVisualizationContent } from '../library';
import HomeContent from '../../views/HomeContent.vue';
import AISettingsContent from '../../views/AISettingsContent.vue';

// Props
const props = defineProps({
  activeContent: {
    type: String,
    default: 'home'
  },
  isInitialLoading: {
    type: Boolean,
    default: true
  }
});

// Refs
const mainContent = ref(null);

// Expose
defineExpose({
  mainContent
});
</script>

<style scoped>
/* 主内容区域样式 */
</style>