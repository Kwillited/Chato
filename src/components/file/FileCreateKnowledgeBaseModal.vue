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
      
      <!-- 知识库描述 -->
      <div class="mb-4">
        <label for="knowledgeBaseDescription" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">知识库描述</label>
        <textarea
          id="knowledgeBaseDescription"
          v-model="knowledgeBaseDescription"
          type="text"
          placeholder="请输入知识库描述（可选）"
          class="w-full min-h-24 px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors knowledge-base-description"
          rows="3"
        ></textarea>
      </div>
      
      <!-- 文本分块设置 -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">文本分块设置</label>
        
        <div class="flex space-x-4">
          <!-- chunk_size 设置 -->
          <div class="flex-1">
            <div class="flex justify-between items-center mb-1">
              <label for="chunkSize" class="text-xs text-gray-600 dark:text-gray-400">分块大小 ({{ chunkSize }}字符)</label>
            </div>
            <input
              id="chunkSize"
              v-model.number="chunkSize"
              type="range"
              min="500"
              max="6000"
              step="100"
              class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            >
          </div>
          
          <!-- chunk_overlap 设置 -->
          <div class="flex-1">
            <div class="flex justify-between items-center mb-1">
              <label for="chunkOverlap" class="text-xs text-gray-600 dark:text-gray-400">分块重叠 ({{ chunkOverlap }}字符)</label>
            </div>
            <input
              id="chunkOverlap"
              v-model.number="chunkOverlap"
              type="range"
              min="0"
              max="3000"
              step="50"
              class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            >
          </div>
        </div>
      </div>
      
      <!-- 向量模型选择 -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">向量模型</label>
        <template v-if="settingsStore.embeddingModelLoading">
          <div class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md text-center text-gray-500 dark:text-gray-400">
            加载中...
          </div>
        </template>
        <template v-else-if="hasAvailableEmbeddingModels">
          <select
            id="embeddingModel"
            v-model="selectedEmbeddingModel"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors"
          >
            <option value="">选择向量模型(选填)</option>
            <option v-for="option in embeddingModelOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </template>
        <template v-else>
          <div class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md text-center text-gray-500 dark:text-gray-400">
            暂无可用模型
          </div>
        </template>
      </div>
    </template>
  </ConfirmationModal>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useFileStore } from '../../store/fileStore.js';
import { useSettingsStore } from '../../store/settingsStore.js';
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
const settingsStore = useSettingsStore();

// Refs
const knowledgeBaseName = ref('');
const knowledgeBaseDescription = ref('');
const selectedEmbeddingModel = ref(''); // 默认值将在计算属性中设置
const chunkSize = ref(1000); // 默认分块大小
const chunkOverlap = ref(200); // 默认分块重叠大小
const error = ref('');
const inputRef = ref(null);

// 计算属性：获取已配置的嵌入模型列表
const configuredEmbeddingModels = computed(() => {
  return settingsStore.configuredEmbeddingModels;
});

// 计算属性：构建嵌入模型选项列表
const embeddingModelOptions = computed(() => {
  const options = [];
  
  // 遍历已配置的嵌入模型
  configuredEmbeddingModels.value.forEach(model => {
    if (model.versions && model.versions.length > 0) {
      // 为每个模型的每个版本创建选项
      model.versions.forEach(version => {
        const optionValue = `${model.name}-${version.version_name}`;
        const optionLabel = `${model.name} ${version.custom_name || version.version_name}`;
        options.push({ value: optionValue, label: optionLabel });
      });
    }
  });
  
  return options;
});

// 计算属性：是否有可用的嵌入模型
const hasAvailableEmbeddingModels = computed(() => {
  return embeddingModelOptions.value.length > 0;
});

// 当模态框显示时，自动聚焦输入框并加载嵌入模型
const focusInput = async () => {
  if (props.visible && inputRef.value) {
    // 检查嵌入模型是否已加载，如果未加载则触发加载
    if (settingsStore.embeddingModels.length === 0 && !settingsStore.embeddingModelLoading) {
      await settingsStore.loadEmbeddingModels();
    }
    
    // 设置默认嵌入模型
    if (embeddingModelOptions.value.length > 0 && !selectedEmbeddingModel.value) {
      selectedEmbeddingModel.value = embeddingModelOptions.value[0].value;
    }
    
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
    // 当没有可用模型时传递null，否则传递选择的嵌入模型
    const embeddingModel = hasAvailableEmbeddingModels.value && selectedEmbeddingModel.value ? selectedEmbeddingModel.value : null;
    
    // 通过fileStore创建知识库，传递选择的嵌入模型、描述和分块参数
    const result = await fileStore.createFolder(knowledgeBaseName.value.trim(), embeddingModel, knowledgeBaseDescription.value.trim(), chunkSize.value, chunkOverlap.value);
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
  knowledgeBaseDescription.value = '';
  // 设置默认嵌入模型
  if (embeddingModelOptions.value.length > 0) {
    selectedEmbeddingModel.value = embeddingModelOptions.value[0].value;
  } else {
    selectedEmbeddingModel.value = '';
  }
  // 重置分块参数
  chunkSize.value = 1000;
  chunkOverlap.value = 200;
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

/* 确保知识库描述textarea有边框 */
.knowledge-base-description {
  outline: none !important;
  border: 1px solid #d1d5db !important;
  box-shadow: none !important;
}

.dark .knowledge-base-description {
  border: 1px solid #4b5563 !important;
}

.knowledge-base-description:focus {
  outline: none !important;
  border: 1px solid #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

.dark .knowledge-base-description:focus {
  border: 1px solid #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
}
</style>