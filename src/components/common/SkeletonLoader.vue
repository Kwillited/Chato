<template>
  <div class="skeleton-loader">
    <div class="skeleton-pulse">
      <!-- 文件夹列表骨架屏 -->
      <div v-if="type === 'folders'" class="skeleton-folders">
        <div v-if="showHeader" class="skeleton-header"></div>
        <div class="skeleton-items">
          <div v-for="i in count" :key="'folder-' + i" class="skeleton-folder-item">
            <div class="skeleton-folder-header">
              <div class="skeleton-folder-info">
                <div class="skeleton-icon"></div>
                <div class="skeleton-text skeleton-text-medium"></div>
              </div>
              <div class="skeleton-action"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件列表骨架屏 -->
      <div v-else-if="type === 'files'" class="skeleton-files">
        <div class="skeleton-items">
          <div v-for="i in count" :key="'file-' + i" class="skeleton-file-item">
            <div class="skeleton-file-header">
              <div class="skeleton-file-info">
                <div class="skeleton-icon"></div>
                <div class="skeleton-text skeleton-text-medium"></div>
              </div>
              <div class="skeleton-text skeleton-text-small"></div>
            </div>
            <div class="skeleton-text skeleton-text-smaller"></div>
          </div>
        </div>
      </div>

      <!-- MCP工具列表骨架屏 -->
      <div v-else-if="type === 'tools'" class="skeleton-tools">
        <div class="skeleton-items">
          <div v-for="i in count" :key="'tool-' + i" class="skeleton-tool-item">
            <div class="skeleton-tool-header">
              <div class="skeleton-tool-info">
                <div class="skeleton-tool-icon"></div>
                <div class="skeleton-tool-texts">
                  <div class="skeleton-text skeleton-text-medium"></div>
                  <div class="skeleton-text skeleton-text-small"></div>
                </div>
              </div>
              <div class="skeleton-tool-action"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件管理网格骨架屏 -->
      <div v-else-if="type === 'grid'" class="skeleton-grid">
        <div class="skeleton-grid-container">
          <div v-for="i in count" :key="'grid-' + i" class="skeleton-grid-item">
            <div class="skeleton-grid-icon"></div>
            <div class="skeleton-text skeleton-text-medium"></div>
            <div class="skeleton-text skeleton-text-small"></div>
          </div>
        </div>
      </div>

      <!-- 历史对话列表骨架屏 -->
      <div v-else-if="type === 'history'" class="skeleton-history">
        <div v-if="showHeader" class="skeleton-header"></div>
        <div class="skeleton-items">
          <div v-for="i in count" :key="'history-' + i" class="skeleton-history-item">
            <div class="skeleton-history-info">
              <div class="skeleton-icon"></div>
              <div class="skeleton-text skeleton-text-medium"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  // 骨架屏类型: folders, files, tools, grid, history
  type: {
    type: String,
    required: true,
    validator: (value) => ['folders', 'files', 'tools', 'grid', 'history'].includes(value)
  },
  // 显示数量
  count: {
    type: Number,
    default: 3
  },
  // 是否显示标题（仅folders类型适用）
  showHeader: {
    type: Boolean,
    default: true
  }
});
</script>

<style scoped>
/* CSS 变量定义 */
:root {
  /* 浅色模式 */
  --skeleton-bg: #f9fafb;
  --skeleton-bg-secondary: #f3f4f6;
  --skeleton-border: #d1d5db;
  --skeleton-placeholder: #e5e7eb;
  --skeleton-placeholder-dark: #d1d5db;
  --skeleton-text: #9ca3af;
  
  /* 深色模式 */
  --skeleton-bg-dark: #1f2937;
  --skeleton-bg-secondary-dark: #111827;
  --skeleton-border-dark: #374151;
  --skeleton-placeholder-dark: #374151;
  --skeleton-placeholder-darker: #1f2937;
  --skeleton-text-dark: #6b7280;
  
  /* 尺寸和间距 */
  --skeleton-spacing-xs: 0.25rem;
  --skeleton-spacing-sm: 0.5rem;
  --skeleton-spacing-md: 0.75rem;
  --skeleton-spacing-lg: 1rem;
  --skeleton-spacing-xl: 1.5rem;
  
  /* 边框圆角 */
  --skeleton-radius-sm: 0.25rem;
  --skeleton-radius-md: 0.375rem;
  --skeleton-radius-lg: 0.5rem;
  --skeleton-radius-xl: 0.75rem;
  
  /* 过渡动画 */
  --skeleton-transition: all 0.3s ease-in-out;
}

/* 基础样式 */
.skeleton-loader {
  width: 100%;
  transition: opacity 0.3s ease-in-out;
}

/* 呼吸动画 */
.skeleton-pulse {
  animation: skeleton-pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes skeleton-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

/* 通用布局 */
.skeleton-items {
  display: flex;
  flex-direction: column;
  gap: var(--skeleton-spacing-sm);
}

/* 占位元素样式 */
.skeleton-text {
  background-color: var(--skeleton-placeholder);
  border-radius: var(--skeleton-radius-sm);
  transition: var(--skeleton-transition);
}

.skeleton-text-small {
  height: 1rem;
  max-width: 4rem;
}

.skeleton-text-medium {
  height: 1rem;
  max-width: 5rem;
}

.skeleton-text-smaller {
  height: 0.75rem;
  max-width: 3.75rem;
  margin-top: var(--skeleton-spacing-xs);
}

.skeleton-icon {
  width: 1rem;
  height: 1rem;
  background-color: var(--skeleton-placeholder-dark);
  border-radius: 50%;
  margin-right: var(--skeleton-spacing-sm);
  transition: var(--skeleton-transition);
}

/* 头部占位 */
.skeleton-header {
  height: 1.5rem;
  background-color: var(--skeleton-placeholder);
  border-radius: var(--skeleton-radius-md);
  margin: 0 var(--skeleton-spacing-sm) var(--skeleton-spacing-lg);
  transition: var(--skeleton-transition);
}

/* 文件夹列表骨架屏 */
.skeleton-folders {
  width: 100%;
}

.skeleton-folder-item {
  background-color: var(--skeleton-bg);
  border: 1px solid var(--skeleton-border);
  border-radius: var(--skeleton-radius-lg);
  padding: var(--skeleton-spacing-md);
  margin-bottom: var(--skeleton-spacing-sm);
  transition: var(--skeleton-transition);
}

.skeleton-folder-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.skeleton-folder-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.skeleton-action {
  width: 1.5rem;
  height: 1.5rem;
  background-color: var(--skeleton-placeholder);
  border-radius: 50%;
  transition: var(--skeleton-transition);
}

/* 文件列表骨架屏 */
.skeleton-files {
  width: 100%;
}

.skeleton-file-item {
  background-color: var(--skeleton-bg);
  border: 1px solid var(--skeleton-border);
  border-radius: var(--skeleton-radius-lg);
  padding: var(--skeleton-spacing-md);
  margin-bottom: var(--skeleton-spacing-sm);
  transition: var(--skeleton-transition);
}

.skeleton-file-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.skeleton-file-info {
  display: flex;
  align-items: center;
  flex: 1;
}

/* MCP工具列表骨架屏 */
.skeleton-tools {
  width: 100%;
}

.skeleton-tool-item {
  background-color: var(--skeleton-bg);
  border: 1px solid var(--skeleton-border);
  border-radius: var(--skeleton-radius-lg);
  padding: var(--skeleton-spacing-md);
  margin-bottom: var(--skeleton-spacing-sm);
  transition: var(--skeleton-transition);
}

.skeleton-tool-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.skeleton-tool-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.skeleton-tool-icon {
  width: 2rem;
  height: 2rem;
  background-color: var(--skeleton-placeholder);
  border-radius: 50%;
  margin-right: var(--skeleton-spacing-md);
  transition: var(--skeleton-transition);
}

.skeleton-tool-texts {
  display: flex;
  flex-direction: column;
  gap: var(--skeleton-spacing-xs);
}

.skeleton-tool-action {
  width: 2rem;
  height: 2rem;
  background-color: var(--skeleton-placeholder);
  border-radius: 50%;
  transition: var(--skeleton-transition);
}

/* 文件管理网格骨架屏 */
.skeleton-grid {
  width: 100%;
}

.skeleton-grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--skeleton-spacing-md);
}

@media (min-width: 640px) {
  .skeleton-grid-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 768px) {
  .skeleton-grid-container {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .skeleton-grid-container {
    grid-template-columns: repeat(4, 1fr);
  }
}

.skeleton-grid-item {
  background-color: var(--skeleton-bg);
  border: 1px solid var(--skeleton-border);
  border-radius: var(--skeleton-radius-lg);
  padding: var(--skeleton-spacing-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 10rem;
  transition: var(--skeleton-transition);
}

.skeleton-grid-icon {
  width: 3rem;
  height: 3rem;
  background-color: var(--skeleton-placeholder);
  border-radius: 50%;
  margin-bottom: var(--skeleton-spacing-sm);
  transition: var(--skeleton-transition);
}

/* 历史对话列表骨架屏 */
.skeleton-history {
  width: 100%;
}

.skeleton-history-item {
  background-color: var(--skeleton-bg);
  border: 1px solid var(--skeleton-border);
  border-radius: var(--skeleton-radius-lg);
  padding: var(--skeleton-spacing-sm);
  margin-bottom: var(--skeleton-spacing-sm);
  transition: var(--skeleton-transition);
}

.skeleton-history-info {
  display: flex;
  align-items: center;
  width: 100%;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .skeleton-text,
  .skeleton-header,
  .skeleton-action,
  .skeleton-tool-action,
  .skeleton-grid-icon,
  .skeleton-tool-icon,
  .skeleton-icon {
    background-color: var(--skeleton-placeholder-dark);
  }
  
  .skeleton-folder-item,
  .skeleton-file-item,
  .skeleton-tool-item,
  .skeleton-grid-item,
  .skeleton-history-item {
    background-color: var(--skeleton-bg-dark);
    border-color: var(--skeleton-border-dark);
  }
}

/* 强制深色模式（当应用设置为深色模式时） */
.dark .skeleton-text,
.dark .skeleton-header,
.dark .skeleton-action,
.dark .skeleton-tool-action,
.dark .skeleton-grid-icon,
.dark .skeleton-tool-icon,
.dark .skeleton-icon {
  background-color: var(--skeleton-placeholder-dark);
}

.dark .skeleton-folder-item,
.dark .skeleton-file-item,
.dark .skeleton-tool-item,
.dark .skeleton-grid-item,
.dark .skeleton-history-item {
  background-color: var(--skeleton-bg-dark);
  border-color: var(--skeleton-border-dark);
}
</style>