<template>
  <div v-if="visible" class="fixed inset-0 flex items-center justify-center z-50" @click="handleBackdropClick">
    <div class="bg-white dark:bg-gray-800 dark:text-white rounded-xl shadow-2xl dark:shadow-2xl border-2 border-gray-200 dark:border-gray-600 p-6 w-full max-w-md mx-4 transform transition-all duration-300 scale-100" @click.stop>
      <!-- 标题区域 -->
      <div class="mb-4 flex justify-between items-center">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-white">{{ title }}</h3>
        <button 
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
          @click="handleClose"
        >
          <i class="fa-solid fa-times"></i>
        </button>
      </div>
      
      <!-- 内容区域 -->
      <div class="mb-6">
        <div v-if="folderInfo" class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">ID:</span>
            <span class="font-medium">{{ folderInfo.id }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">名称:</span>
            <span class="font-medium">{{ folderInfo.name }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">描述:</span>
            <span class="font-medium">{{ folderInfo.description || '无' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">嵌入模型:</span>
            <span class="font-medium">{{ folderInfo.embedding_model || '无' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">创建时间:</span>
            <span class="font-medium">{{ formatDate(folderInfo.created_at) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">分块大小:</span>
            <span class="font-medium">{{ folderInfo.chunk_size }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">分块重叠:</span>
            <span class="font-medium">{{ folderInfo.chunk_overlap }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">文件数量:</span>
            <span class="font-medium">{{ folderInfo.file_count }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">路径:</span>
            <span class="font-medium text-xs truncate max-w-[200px]">{{ folderInfo.path }}</span>
          </div>
        </div>
        <div v-else class="text-gray-500 dark:text-gray-400">
          加载中...
        </div>
      </div>
      
      <!-- 按钮区域 -->
      <div class="flex justify-end">
        <button 
          class="px-4 py-2 rounded-md bg-primary hover:bg-primary/90 text-white transition-colors"
          @click="handleClose"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';

// Props
const _props = defineProps({
  // 是否显示模态框
  visible: {
    type: Boolean,
    default: false
  },
  // 模态框标题
  title: {
    type: String,
    default: '文件夹信息'
  },
  // 文件夹信息
  folderInfo: {
    type: Object,
    default: null
  }
});

// Emits
const emit = defineEmits(['close']);

// 处理关闭按钮点击事件
const handleClose = () => {
  emit('close');
};

// 处理背景点击事件，关闭模态框
const handleBackdropClick = () => {
  emit('close');
};

// 处理ESC键关闭模态框
const handleKeyDown = (event) => {
  if (event.key === 'Escape') {
    handleClose();
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无';
  const date = new Date(dateString);
  return date.toLocaleString();
};

// 监听键盘事件
onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});
</script>

<style scoped>
/* 可以添加组件特定的样式 */
</style>