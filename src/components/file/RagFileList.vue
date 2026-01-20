<template>
  <div class="files-list mt-3">
    <h3 class="text-sm font-medium text-gray-700 dark:text-white mb-2 px-2">{{ currentFolder.name }} 中的文件 ({{ currentFiles.length }})</h3>
    
    <!-- 文件列表 -->
    <div v-if="currentFiles.length > 0">
      <div v-for="file in currentFiles" :key="file.path"
        class="file-item bg-white border border-gray-200 dark:bg-dark-bg-secondary rounded-lg p-3 mb-2 hover:bg-gray-50 dark:hover:bg-dark-bg-tertiary transition-all duration-300"
      >
        <div class="file-header flex items-center justify-between">
          <div class="flex items-center">
            <i class="fa-solid fa-file text-gray-500 dark:text-gray-400 mr-2"></i>
            <span class="font-medium text-sm text-gray-700 dark:text-gray-300">{{ file.name }}</span>
          </div>
          <span class="text-xs text-gray-500 dark:text-gray-400">{{ formatFileSize(file.size) }}</span>
        </div>
        <div class="file-meta text-xs text-gray-500 dark:text-gray-400 mt-1">
          {{ file.created_at ? new Date(file.created_at).toLocaleDateString() : '未知时间' }}
        </div>
      </div>
    </div>
    
    <!-- 空文件状态 -->
    <StateDisplay v-else-if="!loadingFiles" type="empty" title="暂无文件" message="该知识库中暂无文件，点击上方'上传文件'按钮添加" icon="fa-file-circle-exclamation" />
    
    <!-- 加载文件状态 -->
    <StateDisplay v-if="loadingFiles" type="loading" message="加载文件中..." />
  </div>
</template>

<script setup>
import StateDisplay from '../common/StateDisplay.vue';
import { formatFileSize } from '../../store/utils.js';

defineProps({
  currentFolder: {
    type: Object,
    required: true
  },
  currentFiles: {
    type: Array,
    default: () => []
  },
  loadingFiles: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
/* 文件列表样式 */
.files-list {
  margin-top: 12px;
}

.files-list h3 {
  font-size: 13px;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 8px;
  padding: 0 8px;
}

.dark .files-list h3 {
  color: white;
}

.file-item {
  transition: all 0.2s ease;
}

.file-item:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.file-header {
  display: flex;
  align-items: center;
  height: 28px;
  line-height: 28px;
}

/* 空状态和加载状态样式 */
.empty-state,
.loading-state {
  padding: 24px;
  text-align: center;
  color: #6b7280;
}

.empty-state i {
  font-size: 36px;
  margin-bottom: 8px;
  color: #9ca3af;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

.empty-state p:last-child {
  font-size: 12px;
  margin-top: 4px;
  color: #9ca3af;
}

.loading-state .animate-spin {
  width: 24px;
  height: 24px;
  margin: 0 auto 8px;
}

.loading-state p {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}
</style>