<template>
  <!-- 纯样式侧边栏组件 -->
  <div class="sidebar">
    <!-- 插槽：侧边栏内容区域 -->
    <slot name="content"></slot>
  </div>
</template>

<script setup>
// 简化为纯样式组件，只提供基础样式
// 移除所有逻辑和 props
</script>

<style scoped>
/* 侧边栏基础样式 */
.sidebar {
  height: 100%;
  background-color: inherit;
  transition: all 0.3s ease;
  overflow-y: auto;
  border-right: 1px solid #f0f0f0;
}

/* 深色模式滚动条 */
.dark .sidebar {
  border-right: 1px solid #2d3748;
}

/* 滚动条样式 */
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 深色模式滚动条 */
.dark .sidebar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
}

.dark .sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 左侧侧边栏特定样式 */
.sidebar.left {
  border-right: 1px solid #e5e7eb;
}

.dark .sidebar.left {
  border-right: 1px solid #4b5563;
}

/* 右侧侧边栏特定样式 */
.sidebar.right {
  border-left: 1px solid #e5e7eb;
  border-right: none;
}

.dark .sidebar.right {
  border-left: 1px solid #4b5563;
}
</style>