<template>
  <div v-if="visible" class="fixed inset-0 flex items-center justify-center z-50" @click="handleBackdropClick">
    <div class="bg-white dark:bg-gray-800 dark:text-white rounded-xl shadow-2xl dark:shadow-2xl border-2 border-gray-200 dark:border-gray-600 p-6 w-full max-w-md mx-4 transform transition-all duration-300 scale-100" @click.stop>
      <!-- 标题区域 -->
      <div class="mb-4">
        <slot name="header">
          <h3 class="text-lg font-semibold text-gray-800 dark:text-white">{{ title }}</h3>
        </slot>
      </div>
      
      <!-- 内容区域 -->
      <div class="mb-6">
        <slot name="content">
          <p v-if="html" class="text-gray-600 dark:text-gray-300" v-html="message"></p>
          <p v-else class="text-gray-600 dark:text-gray-300">{{ message }}</p>
        </slot>
      </div>
      
      <!-- 按钮区域 -->
      <div class="flex justify-end gap-3">
        <slot name="buttons">
          <button 
            class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 text-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
            @click="handleCancel"
          >
            {{ cancelText || '取消' }}
          </button>
          <button 
            :class="[
              'px-4 py-2 rounded-md text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
              {
                'bg-red-500 hover:bg-red-600': confirmType === 'danger',
                'bg-primary hover:bg-primary/90': confirmType === 'primary',
                'bg-green-500 hover:bg-green-600': confirmType === 'success',
                'bg-blue-500 hover:bg-blue-600': confirmType === 'blue'
              }
            ]"
            :disabled="loading"
            @click="handleConfirm"
          >
            <span v-if="!loading">{{ confirmText || '确认' }}</span>
            <span v-else>{{ loadingText || '处理中...' }}</span>
          </button>
        </slot>
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
    default: '确认操作'
  },
  // 模态框内容
  message: {
    type: String,
    default: '您确定要执行此操作吗？'
  },
  // 是否将消息内容作为HTML渲染
  html: {
    type: Boolean,
    default: false
  },
  // 确认按钮文本
  confirmText: {
    type: String,
    default: '确认'
  },
  // 取消按钮文本
  cancelText: {
    type: String,
    default: '取消'
  },
  // 加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 加载状态文本
  loadingText: {
    type: String,
    default: '处理中...'
  },
  // 确认按钮类型（primary/success/danger等）
  confirmType: {
    type: String,
    default: 'danger'
  }
});

// Emits
const emit = defineEmits(['confirm', 'cancel', 'close']);

// 处理确认按钮点击事件
const handleConfirm = () => {
  emit('confirm');
};

// 处理取消按钮点击事件
const handleCancel = () => {
  emit('cancel');
  emit('close');
};

// 处理背景点击事件，关闭模态框
const handleBackdropClick = () => {
  emit('cancel');
  emit('close');
};

// 处理ESC键关闭模态框
const handleKeyDown = (event) => {
  if (event.key === 'Escape') {
    handleCancel();
  }
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