<template>
  <div 
    v-if="uiStore.leftNavVisible && uiStore.activePanel !== 'settings'"
    id="panelContainer" 
    ref="leftPanel"
    class="h-full flex-shrink-0 overflow-hidden transition-all duration-300" 
    :style="{
      width: uiStore.leftNavWidth,
      minWidth: '200px',
      maxWidth: '370px',
      flexShrink: 0,
      zIndex: 'var(--z-panel)'
    }"
  >
    <!-- 面板内容 -->
    <div class="transition-all duration-300 h-full">
      <PanelContent :active-panel="uiStore.activePanel" />
    </div>
  </div>
  <div v-else class="w-0 flex-shrink-0"></div>
</template>

<script setup>
import { ref } from 'vue';
import { useUiStore } from '../../store/uiStore.js';
import PanelContent from './PanelContent.vue';

// Stores
const uiStore = useUiStore();

// Refs
const leftPanel = ref(null);

// Expose
defineExpose({
  leftPanel
});
</script>

<style scoped>
/* 左侧面板样式 */
</style>