<template>
  <div 
    id="panelContainer" 
    ref="leftPanel"
    class="h-full flex-shrink-0 z-40 overflow-hidden transition-all duration-300" 
    :style="{
      width: uiStore.leftNavVisible ? uiStore.leftNavWidth : 'auto',
      minWidth: uiStore.leftNavVisible ? '200px' : 'auto',
      maxWidth: uiStore.leftNavVisible ? '370px' : 'auto',
      flexShrink: 0
    }"
  >
    <!-- 面板内容 -->
    <div v-if="uiStore.leftNavVisible && uiStore.activePanel !== 'settings'" class="transition-all duration-300 h-full">
      <PanelContent :active-panel="uiStore.activePanel" />
    </div>
  </div>
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