<template>
  <div id="settingsPanel" class="h-full flex flex-col">
    <div class="overflow-y-auto h-full scrollbar-thin">
      <!-- 设置导航项已移至顶部导航栏 -->
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUiStore } from '../../store/uiStore.js';

const uiStore = useUiStore();

// 组件挂载时，确保store中至少有一个选中的section
onMounted(() => {
  if (!uiStore.activeSection) {
    uiStore.setActiveSection('general');
  }
});
</script>

<style scoped>
/* 组件特定样式 - 遵循项目整体风格 */

/* 面板标题深色模式 */
.dark .panel-header h2 {
  color: #e2e8f0;
}


</style>
