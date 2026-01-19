<template>
  <div class="panel-header p-3 flex justify-between items-center transition-all duration-300">
    <div class="flex items-center">
      <h2 class="text-lg font-bold text-dark">{{ currentFolder ? currentFolder.name : '知识库' }}</h2>
    </div>
    <!-- 按钮区域 - 保持相同位置 -->
    <div class="flex items-center">
      <!-- 二级菜单时显示返回上一级按钮 -->
      <ActionButton
        v-if="currentFolder"
        icon="fa-chevron-left"
        title="返回上一级"
        @click="handleBackToParent"
      />
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settingsStore.js';
import ActionButton from '../common/ActionButton.vue';

const props = defineProps({
  currentFolder: {
    type: Object,
    default: null
  }
});

const settingsStore = useSettingsStore();

// 处理返回上一级
const handleBackToParent = () => {
  // 触发返回上一级事件，让FilePanel组件处理返回逻辑
  window.dispatchEvent(new CustomEvent('backToParent'));
};
</script>

<style scoped>
/* 组件特定样式 */
.panel-header {
  position: relative;
}
</style>