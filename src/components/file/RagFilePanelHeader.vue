<template>
  <div class="panel-header p-3 flex justify-end items-center transition-all duration-300">
    <!-- 二级菜单时显示返回上一级按钮 -->
    <ActionButton
      v-if="currentFolder"
      icon="fa-chevron-left"
      title="返回上一级"
      @click="handleBackToParent"
    />
  </div>
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