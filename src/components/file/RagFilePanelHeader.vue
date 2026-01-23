<template>
  <!-- 已移除面板头部 -->
</template>

<script setup>
import ActionButton from '../common/ActionButton.vue';

defineProps({
  currentFolder: {
    type: Object,
    default: null
  }
});

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