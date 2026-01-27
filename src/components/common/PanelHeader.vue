<template>
  <div class="panel-header p-3 flex justify-between items-center transition-all duration-300">
    <h2 class="text-lg font-bold text-dark dark:text-white">{{ title }}</h2>
    <!-- 默认返回按钮（如果有返回按钮配置） -->
    <Button
      v-if="showBackButton && !hideDefaultActions"
      :id="backButtonId"
      icon="fa-arrow-left"
      tooltip="返回聊天"
      @click="handleBack"
      size="sm"
      shape="full"
    />
  </div>
</template>

<script setup>
import { Button } from '../library/index.js';
import { useUiStore } from '../../store/uiStore.js';

// 定义props
defineProps({
  title: {
    type: String,
    required: true
  },
  showBackButton: {
    type: Boolean,
    default: true
  },
  backButtonId: {
    type: String,
    default: 'backToChatBtn'
  },
  hideDefaultActions: {
    type: Boolean,
    default: false
  }
});

// 使用store
const uiStore = useUiStore();

// 处理返回按钮点击
const handleBack = () => {
  uiStore.setActivePanel('history');
  
  // 直接使用store方法切换内容，不再使用全局事件
  uiStore.setActiveContent('sendMessage');
};
</script>

<style scoped>
</style>