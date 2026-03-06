<template>
  <!-- 工具列表骨架屏 -->
  <div v-if="type === 'tools' || !type" class="space-y-2">
    <div v-for="i in count" :key="i" class="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-3 flex items-center space-x-3">
      <!-- 左侧：图标骨架 -->
      <div class="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse"></div>
      <!-- 右侧：文本骨架 -->
      <div class="flex-1 space-y-2">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 animate-pulse"></div>
      </div>
    </div>
  </div>
  
  <!-- 文件列表骨架屏 -->
  <div v-else-if="type === 'files'" class="space-y-2">
    <div v-for="i in count" :key="i" class="border border-gray-300 dark:border-gray-600 rounded-lg p-3 mt-1 mb-2">
      <div class="file-header flex items-center justify-between">
        <div class="flex items-center">
          <div class="w-5 h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mr-2"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-pulse"></div>
        </div>
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16 animate-pulse"></div>
      </div>
      <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-24 animate-pulse mt-1"></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: 'tools'
  },
  count: {
    type: Number,
    default: 5
  }
});
</script>

<style scoped>
/* 骨架屏动画 */
.animate-pulse {
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>