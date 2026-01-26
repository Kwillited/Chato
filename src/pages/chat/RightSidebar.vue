<template>
  <!-- 右侧侧边栏组件 - 基于通用 Sidebar -->
  <Sidebar class="right">
    <template #content>
      <!-- 右侧侧边栏内容 -->
      <div class="p-4">
        <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-white">右侧面板</h3>
        <div class="text-gray-600 dark:text-gray-400">
          <p>右侧侧边栏内容区域</p>
        </div>
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import Sidebar from '../../shared/ui/layout/Sidebar.vue';
</script>

<style scoped>
/* 移除通用样式，已移至 Sidebar.vue */
/* 仅保留特定于右侧面板的样式 */
/* 右侧面板特定样式可以在这里添加 */
</style>