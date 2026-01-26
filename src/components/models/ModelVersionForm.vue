<template>
  <!-- 模型版本表单模态框 - 支持添加和编辑 -->
  <ConfirmationModal
    :visible="visible"
    :title="isEditMode ? '编辑模型版本' : '添加模型版本'"
    :confirm-text="'保存'"
    :cancel-text="'取消'"
    :loading="false"
    confirm-type="primary"
    @confirm="handleSubmit"
    @close="handleClose"
    @cancel="handleClose"
  >
    <!-- 自定义内容：模型版本表单 -->
    <template #content>
      <form @submit.prevent="handleSubmit">
        <input type="hidden" v-model="versionId" />
        <div class="space-y-6">
          <div>
            <label class="block text-sm font-medium mb-2 dark:text-gray-300">模型名称</label>
            <input
              type="text"
              v-model="formModelName"
              :class="['input-field w-full px-3 py-2 focus:outline-none focus:ring-1', errors.modelName ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
              readonly
              @input="errors.modelName = ''"
            />
            <p v-if="errors.modelName" class="text-xs text-red-500 mt-1">{{ errors.modelName }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2 dark:text-gray-300">模型版本 <span class="text-red-500">*</span></label>
            <input
              type="text"
              v-model="modelVersion"
              :class="['input-field w-full px-3 py-2 focus:outline-none focus:ring-1', errors.modelVersion ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
              :placeholder="isEditMode ? '' : '例如：gpt-4, gpt-3.5-turbo, claude-3-opus-20240229等'"
              :readonly="isEditMode"
              @input="errors.modelVersion = ''"
            />
            <p v-if="errors.modelVersion" class="text-xs text-red-500 mt-1">{{ errors.modelVersion }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2 dark:text-gray-300">自定义名字</label>
            <input
              type="text"
              v-model="modelCustomName"
              class="input-field w-full px-3 py-2 focus:outline-none focus:ring-1 focus:ring-primary dark:bg-gray-700 dark:text-white dark:border-gray-600"
              placeholder="为模型设置用于显示的名字"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2 dark:text-gray-300">API 密钥 <span v-if="!isOllama" class="text-red-500">*</span></label>
            <input
              type="password"
              v-model="apiKey"
              :class="['input-field w-full px-3 py-2 focus:outline-none focus:ring-1', errors.apiKey ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
              :placeholder="isOllama ? 'Ollama不需要密钥' : 'sk-...'"
              @input="errors.apiKey = ''"
              :disabled="isOllama"
            />
            <p v-if="errors.apiKey" class="text-xs text-red-500 mt-1">{{ errors.apiKey }}</p>
            <p v-else-if="isOllama" class="text-xs text-green-500 mt-1">Ollama不需要API密钥</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2 dark:text-gray-300">API 基础 URL <span class="text-red-500">*</span></label>
            <input
              type="text"
              v-model="apiBaseUrl"
              :class="['input-field w-full px-3 py-2 focus:outline-none focus:ring-1', errors.apiBaseUrl ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
              placeholder="https://api.openai.com"
              @input="errors.apiBaseUrl = ''"
            />
            <p v-if="errors.apiBaseUrl" class="text-xs text-red-500 mt-1">{{ errors.apiBaseUrl }}</p>
          </div>

          <div class="pt-4 border-t border-gray-100 dark:border-gray-700">
            <label class="flex items-center">
              <input type="checkbox" v-model="streamingConfig" class="rounded text-primary focus:ring-primary dark:bg-gray-700 dark:border-gray-600" />
              <span class="ml-2 text-sm dark:text-gray-300">是否支持流式响应</span>
            </label>
          </div>
        </div>
      </form>
    </template>
  </ConfirmationModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useModelSettingStore } from '../../store/modelSettingStore.js';
import { eventBus } from '../../services/eventBus.js';
import { showNotification } from '../../services/notificationUtils.js';
import ConfirmationModal from '../common/ConfirmationModal.vue';

// 定义组件名称
defineOptions({
  name: 'ModelVersionForm'
});

// 初始化store
const modelStore = useModelSettingStore();

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  modelName: {
    type: String,
    default: ''
  },
  mode: {
    type: String,
    default: 'add' // add 或 edit
  },
  modelData: {
    type: Object,
    default: null
  }
});

// Emits
const emit = defineEmits(['close', 'success']);

// 表单数据
const isEditMode = ref(props.mode === 'edit');
const versionId = ref('');
const formModelName = ref(props.modelName || '');
const modelVersion = ref('');
const modelCustomName = ref('');
const apiKey = ref('');
const apiBaseUrl = ref('');
const streamingConfig = ref(false);

// 判断是否为Ollama模型
const isOllama = computed(() => {
  return formModelName.value && formModelName.value.toLowerCase() === 'ollama';
});

// 错误状态对象
const errors = ref({
    modelName: '',
    modelVersion: '',
    apiKey: '',
    apiBaseUrl: ''
  });

// 监听props变化，更新表单数据
watch(() => props.visible, (newValue) => {
  if (newValue) {
    // 显示模态框时初始化数据
    isEditMode.value = props.mode === 'edit';
    versionId.value = '';
    formModelName.value = props.modelName || '';
    modelVersion.value = '';
    modelCustomName.value = '';
    apiKey.value = '';
    apiBaseUrl.value = '';
    streamingConfig.value = false;
    clearErrors();
    
    // 如果是编辑模式，填充表单数据
    if (isEditMode.value && props.modelData) {
      populateFormData(props.modelData);
    }
  }
});

// 清除错误信息
const clearErrors = () => {
  errors.value.modelName = '';
  errors.value.modelVersion = '';
  errors.value.apiKey = '';
  errors.value.apiBaseUrl = '';
};

// 处理表单提交
const handleSubmit = async () => {
  try {
    // 清除之前的错误
    clearErrors();
    
    // 表单验证
    let hasError = false;
    
    if (!formModelName.value) {
      errors.value.modelName = '模型名称不能为空';
      hasError = true;
    }
    
    if (!modelVersion.value) {
      errors.value.modelVersion = '请输入模型版本';
      hasError = true;
    }
    
    if (!isOllama.value && !apiKey.value.trim()) {
      errors.value.apiKey = '请输入API密钥';
      hasError = true;
    }
    
    if (!apiBaseUrl.value.trim()) {
      errors.value.apiBaseUrl = '请输入API基础URL';
      hasError = true;
    }
    
    if (hasError) {
      return;
    }

    // 构建请求数据
    const versionConfig = {
      customName: modelCustomName.value,
      apiKey: apiKey.value,
      apiBaseUrl: apiBaseUrl.value,
      versionName: modelVersion.value,
      streamingConfig: streamingConfig.value
    };

    if (isEditMode.value) {
      // 使用modelStore更新模型版本
      await modelStore.updateModelVersion(formModelName.value, modelVersion.value, versionConfig);
    } else {
      // 使用modelStore添加模型版本
      await modelStore.addModelVersion(formModelName.value, versionConfig);
    }

    // 显示成功提示
    showNotification('模型版本配置已保存', 'success');
    
    // 清除错误
    clearErrors();

    // 关闭模态框
    emit('close');
    emit('success');

    // 通过事件总线通知模型已更新
    eventBus.emit('modelUpdated');
  } catch (error) {
    // 显示错误信息
    console.error('保存模型版本失败:', error);
    showNotification(`保存模型版本失败: ${error.message}`, 'error');
  }
};

// 处理关闭模态框
const handleClose = () => {
  emit('close');
};

// 填充表单数据（编辑模式）
const populateFormData = (data) => {
  // 填充表单数据，处理不同来源的字段名称差异
  versionId.value = data.id || '';
  formModelName.value = data.modelName || '';
  // 处理 modelVersion 或 versionName 字段
  modelVersion.value = data.modelVersion || data.versionName || '';
  modelCustomName.value = data.customName || '';
  // 处理 apiKey 或 api_key 字段
  apiKey.value = data.apiKey || data.api_key || '';
  // 处理 apiBaseUrl 或 api_base_url 字段
  apiBaseUrl.value = data.apiBaseUrl || data.api_base_url || '';
  // 处理 streamingConfig 或 streaming_config 或 streaming 字段
  streamingConfig.value = data.streamingConfig || data.streaming_config || data.streaming || false;
};


</script>

<style scoped>
/* 组件特定样式 */
.panel-header {
  border-bottom: 1px solid #e5e7eb;
}

.dark .panel-header {
  border-bottom-color: #374151;
}

.input-field {
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
  background-color: white;
  border-radius: 6px;
}

.dark .input-field {
  border-color: #374151;
  background-color: #1f2937;
  color: white;
}

.input-field:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
  transform: translateY(-0.5px);
}

.dark .input-field:focus {
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
}

.btn {
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s ease;
}





.hover-scale {
  transition: transform 0.2s ease;
}

.hover-scale:hover {
  transform: scale(1.02);
}
</style>
