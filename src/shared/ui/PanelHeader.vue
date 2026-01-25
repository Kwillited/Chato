<template>
  <!-- 已移除面板头部 -->
</template>

<script setup>
import { Button } from '../library/index.js';
import { useSettingsStore } from '../../store/settingsStore.js';

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
const settingsStore = useSettingsStore();

// 处理返回按钮点击
const handleBack = () => {
  settingsStore.setActivePanel('history');
  
  // 直接使用store方法切换内容，不再使用全局事件
  settingsStore.setActiveContent('chat');
};
</script>

<style scoped>
</style>