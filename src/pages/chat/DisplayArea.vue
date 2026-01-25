<template>
  <div class="display-area">
    <!-- 这里是显示区域的内容，可以根据activeContent动态渲染不同的组件 -->
    <component :is="currentContentComponent" />
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue';
import { useSettingsStore } from '../../app/store/settingsStore.js';

// 组件导入
import ChatContent from './ChatContent.vue';
import AISettingsContent from './AISettingsContent.vue';
import RagManagementContent from './RagManagementContent.vue';
import SendMessageContent from './SendMessageContent.vue';

// Props
const props = defineProps({
  activeContent: { type: String, default: 'sendMessage' },
  isInitialLoading: { type: Boolean, default: true }
});

// Stores & Utils
const settingsStore = useSettingsStore();
const emitter = inject('emitter', null); 

// 动态组件映射
const componentMap = {
  chat: ChatContent,
  settings: AISettingsContent,
  aiSettings: AISettingsContent,
  ragManagement: RagManagementContent,
  contextVisualization: RagManagementContent,
  sendMessage: SendMessageContent
};

const currentContentComponent = computed(() => componentMap[props.activeContent] || SendMessageContent);
</script>

<style scoped>
.display-area {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>