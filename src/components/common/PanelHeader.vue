<template>
  <div class="panel-header p-3 flex justify-end items-center transition-all duration-300">
    <template v-if="!hideDefaultActions">
      <!-- 自定义按钮插槽 -->
      <slot name="actions"></slot>
      
      <!-- 默认返回按钮（如果有返回按钮配置） -->
      <Button
        v-if="showBackButton"
        :id="backButtonId"
        icon="fa-arrow-left"
        tooltip="返回聊天"
        @click="handleBack"
        size="sm"
        shape="full"
        class="ml-2"
      />
    </template>
  </div>
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