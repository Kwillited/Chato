<template>
  <div class="panel-header p-3 flex items-center justify-between gap-2 transition-all duration-300" :class="customClass">
    <!-- 标题区域 -->
    <h2 class="text-lg font-bold text-dark dark:text-white" :class="{ 'flex-1': centerTitle }">
      {{ title }}
    </h2>
    
    <!-- 左侧按钮组（仅在指定时显示） -->
    <div v-if="leftButtons" class="absolute left-3 flex space-x-2">
      <slot name="leftButtons"></slot>
    </div>
    
    <!-- 右侧按钮组 -->
    <div class="flex items-center gap-2">
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
      />
    </div>
  </div>
</template>

<script setup>
import { Button } from '../library/index.js';
import { useSettingsStore } from '../../store/settingsStore.js';

// 定义props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  showBackButton: {
    type: Boolean,
    default: false
  },
  backButtonId: {
    type: String,
    default: 'backToChatBtn'
  },
  leftButtons: {
    type: Boolean,
    default: false
  },
  centerTitle: {
    type: Boolean,
    default: false
  },
  customClass: {
    type: String,
    default: ''
  }
});

// 使用store
const settingsStore = useSettingsStore();

// 处理返回按钮点击
const handleBack = () => {
  settingsStore.setActivePanel('history');
  settingsStore.setActiveContent('chat');
};
</script>

<style scoped>
/* 可以添加组件特定的样式 */
</style>