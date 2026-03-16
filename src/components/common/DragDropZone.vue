<template>
  <div 
    ref="dragDropArea"
    class="relative"
    :class="containerClass"
    @dragover.prevent="handleDragOver"
    @dragenter.prevent="handleDragEnter"
    @dragleave="handleDragLeave"
    @drop.prevent="handleDrop"
  >
    <!-- 子内容插槽 -->
    <slot></slot>
    
    <!-- 拖拽提示区域 -->
    <div
      v-if="isDragOver"
      class="absolute inset-0 flex flex-col items-center justify-center bg-blue-50 dark:bg-blue-900/20 border-2 border-dashed border-primary dark:border-blue-400 opacity-100 pointer-events-none transition-all duration-300 z-20 animate-pulse"
      :class="[overlayClass, overlayRadius]"
    >
      <i class="fa-solid fa-cloud-arrow-up text-primary dark:text-blue-400" :class="iconClass"></i>
      <span class="text-primary dark:text-blue-400 font-medium" :class="mainTextClass">{{ overlayText || '释放文件以上传' }}</span>
      <span v-if="subText" class="text-gray-600 dark:text-gray-300" :class="subTextClass">{{ subText }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 定义组件属性
defineProps({
  // 容器类名
  containerClass: {
    type: String,
    default: ''
  },
  // 覆盖层类名
  overlayClass: {
    type: String,
    default: ''
  },
  // 覆盖层圆角类名
  overlayRadius: {
    type: String,
    default: 'rounded-3xl'
  },
  // 图标类名
  iconClass: {
    type: String,
    default: 'text-4xl mb-2'
  },
  // 主文本类名
  mainTextClass: {
    type: String,
    default: ''
  },
  // 次文本类名
  subTextClass: {
    type: String,
    default: 'text-sm mt-1'
  },
  // 覆盖层主文本
  overlayText: {
    type: String,
    default: '释放文件以上传'
  },
  // 覆盖层次文本
  subText: {
    type: String,
    default: '或点击上传按钮'
  }
});

// 定义事件
const emit = defineEmits(['drop', 'dragenter', 'dragleave', 'dragover']);

// 拖拽状态
const isDragOver = ref(false);
// 用于解决拖拽闪烁问题的计数器
const dragCounter = ref(0);
// DOM引用
const dragDropArea = ref(null);

// 处理拖拽进入事件
const handleDragEnter = (event) => {
  event.preventDefault();
  event.stopPropagation();
  
  dragCounter.value++;
  if (dragCounter.value === 1) {
    isDragOver.value = true;
    emit('dragenter', event);
  }
};

// 处理拖拽悬停事件
const handleDragOver = (event) => {
  event.preventDefault();
  event.stopPropagation();
  emit('dragover', event);
};

// 处理拖拽离开事件
const handleDragLeave = (event) => {
  event.preventDefault();
  event.stopPropagation();
  
  dragCounter.value--;
  if (dragCounter.value === 0) {
    isDragOver.value = false;
    emit('dragleave', event);
  }
};

// 处理拖拽释放事件
const handleDrop = (event) => {
  event.preventDefault();
  event.stopPropagation();
  
  dragCounter.value = 0;
  isDragOver.value = false;
  
  const files = Array.from(event.dataTransfer.files);
  if (files.length > 0) {
    emit('drop', files, event);
  }
};
</script>

<style scoped>
/* 基础样式已内联在组件中，可通过props进行自定义 */
</style>