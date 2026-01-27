<template>
  <ConfirmationModal
    :visible="visible"
    title="新建知识库"
    confirm-text="创建"
    cancel-text="取消"
    :loading="fileStore.loading"
    loading-text="创建中..."
    confirm-type="primary"
    @confirm="handleCreate"
    @close="handleCancel"
  >
    <!-- 自定义内容：知识库名称输入表单 -->
    <template #content>
      <div class="mb-4">
        <label for="knowledgeBaseName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">知识库名称</label>
        <input
          id="knowledgeBaseName"
          v-model="knowledgeBaseName"
          type="text"
          placeholder="请输入知识库名称"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors"
          @keyup.enter="handleCreate"
          ref="inputRef"
        />
        <p v-if="error" class="text-red-500 text-xs mt-1">{{ error }}</p>
      </div>
    </template>
  </ConfirmationModal>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useFileStore } from '../../store/fileStore.js';
import { showNotification } from '../../utils/notificationUtils.js';
import ConfirmationModal from '../common/ConfirmationModal.vue';

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
});

// Emits
const emit = defineEmits(['close', 'created']);

// Store
const fileStore = useFileStore();

// Refs
const knowledgeBaseName = ref('');
const error = ref('');
const inputRef = ref(null);

// 当模态框显示时，自动聚焦输入框
const focusInput = async () => {
  if (props.visible && inputRef.value) {
    await nextTick();
    inputRef.value.focus();
  }
};

// 监听visible属性变化
watch(() => props.visible, (newValue) => {
  if (newValue) {
    focusInput();
  }
});

// 处理创建知识库
const handleCreate = async () => {
  // 重置错误信息
  error.value = '';
  
  // 验证输入
  if (!knowledgeBaseName.value.trim()) {
    error.value = '请输入知识库名称';
    return;
  }
  
  try {
    // 通过fileStore创建知识库
    const result = await fileStore.createFolder(knowledgeBaseName.value.trim());
    if (result.success) {
      // 显示成功提示
      showNotification(`已成功创建知识库: ${knowledgeBaseName.value.trim()}`, 'success');
      
      // 触发创建成功事件
      emit('created', result);
      
      // 重置表单并关闭模态框
      resetForm();
      emit('close');
    } else {
      throw new Error(result.error || '创建知识库失败');
    }
  } catch (error) {
    // 显示错误提示
    error.value = `创建失败: ${error.message || String(error)}`;
    showNotification(`创建知识库失败: ${error.message || String(error)}`, 'error');
  }
};

// 处理取消
const handleCancel = () => {
  resetForm();
  emit('close');
};

// 重置表单
const resetForm = () => {
  knowledgeBaseName.value = '';
  error.value = '';
};

// 组件挂载时添加ESC键监听
onMounted(() => {
  focusInput();
  document.addEventListener('keydown', handleKeyDown);
});

// 组件卸载时移除ESC键监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});

// 处理ESC键关闭模态框
const handleKeyDown = (event) => {
  if (event.key === 'Escape' && props.visible) {
    handleCancel();
  }
};
</script>

<style scoped>
/* 动画效果已移至通用模态框组件 */
</style>