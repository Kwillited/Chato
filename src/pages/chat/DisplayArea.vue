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
import SettingsPage from './SettingsPage.vue';
import FileManager from './FileManager.vue';
import home from './home.vue';

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
  settings: SettingsPage,
  aiSettings: SettingsPage,
  ragManagement: FileManager,
  sendMessage: home
};

const currentContentComponent = computed(() => componentMap[props.activeContent] || home);
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