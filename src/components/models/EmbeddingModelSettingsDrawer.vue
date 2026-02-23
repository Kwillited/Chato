<template>
  <!-- 向量模型配置抽屉 -->
  <div :class="['drawer-backdrop', { active: isVisible }]" id="embeddingModelSettingsBackdrop" @click="closeDrawer"></div>
  <div :class="['model-settings-drawer depth-3 dark:bg-gray-800 dark:text-white dark:shadow-panel-dark', { active: isVisible }]" id="embeddingModelSettingsDrawer">
    <div class="panel-header p-2 flex justify-between items-center dark:border-gray-700">
      <h3 class="text-base font-semibold dark:text-white" id="drawerModelTitle">{{ modelTitle }}</h3>
      <button
        id="closeDrawerBtn"
        class="btn-secondary p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full text-neutral dark:text-gray-300"
        @click="closeDrawer"
      >
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>

    <div class="p-4">
      <div class="space-y-4">
        <div id="modelVersionsContainer">
          <label class="block text-sm font-medium mb-1.5 dark:text-gray-300">模型版本 <span class="text-red-500">*</span></label>
          <input
            type="text"
            :class="['input-field w-full px-3 py-1.5 focus:outline-none focus:ring-1', errors.modelVersion ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
            placeholder="请输入模型版本"
            id="modelVersionInput"
            v-model="modelVersion"
            @input="errors.modelVersion = ''"
          />
          <p v-if="errors.modelVersion" class="text-xs text-red-500 mt-1">{{ errors.modelVersion }}</p>
          <p v-else class="text-xs text-neutral dark:text-gray-400 mt-0.5">例如：text-embedding-3-small, all-MiniLM-L6-v2</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5 dark:text-gray-300">自定义名字</label>
          <input
            type="text"
            class="input-field w-full px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary dark:bg-gray-700 dark:text-white dark:border-gray-600"
            placeholder="请输入自定义名字"
            id="modelCustomNameInput"
            v-model="customName"
          />
          <p class="text-xs text-neutral dark:text-gray-400 mt-0.5">为模型设置用于显示的名字</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5 dark:text-gray-300">API 密钥</label>
          <input
            type="password"
            :class="['input-field w-full px-3 py-1.5 focus:outline-none focus:ring-1', errors.apiKey ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
            placeholder="请输入API密钥（如OpenAI）"
            id="apiKeyInput"
            v-model="apiKey"
            @input="errors.apiKey = ''"
          />
          <p v-if="errors.apiKey" class="text-xs text-red-500 mt-1">{{ errors.apiKey }}</p>
          <p v-else class="text-xs text-neutral dark:text-gray-400 mt-0.5">本地模型（如Hugging Face）不需要API密钥</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5 dark:text-gray-300">API 基础 URL <span class="text-red-500">*</span></label>
          <input
            type="text"
            :class="['input-field w-full px-3 py-1.5 focus:outline-none focus:ring-1', errors.apiBaseUrl ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
            placeholder="https://api.openai.com"
            id="apiBaseUrlInput"
            v-model="apiBaseUrl"
            @input="errors.apiBaseUrl = ''"
          />
          <p v-if="errors.apiBaseUrl" class="text-xs text-red-500 mt-1">{{ errors.apiBaseUrl }}</p>
          <p v-else class="text-xs text-neutral dark:text-gray-400 mt-0.5">获取URL地址请访问官方网站</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5 dark:text-gray-300">本地模型路径</label>
          <input
            type="text"
            class="input-field w-full px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary dark:bg-gray-700 dark:text-white dark:border-gray-600"
            placeholder="例如：C:\\models\\all-MiniLM-L6-v2"
            id="modelPathInput"
            v-model="modelPath"
          />
          <p class="text-xs text-neutral dark:text-gray-400 mt-0.5">本地模型文件的路径（如Hugging Face本地模型）</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5 dark:text-gray-300">向量维度</label>
          <input
            type="number"
            class="input-field w-full px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary dark:bg-gray-700 dark:text-white dark:border-gray-600"
            placeholder="例如：384, 1536"
            id="dimensionInput"
            v-model.number="dimension"
            min="1"
          />
          <p class="text-xs text-neutral dark:text-gray-400 mt-0.5">嵌入模型生成的向量维度（all-MiniLM-L6-v2为384，OpenAI为1536）</p>
        </div>


      </div>

      <div class="mt-4 flex justify-end gap-2">
        <button
          id="cancelConfigBtn"
          class="btn btn-secondary px-3 py-1.5 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 transition-colors hover-scale"
          @click="cancelConfig"
        >
          取消
        </button>
        <button
          id="saveConfigBtn"
          class="btn btn-primary px-3 py-1.5 text-white rounded-lg text-sm hover:bg-[#4338ca] hover:shadow-md transform hover:-translate-y-0.5 transition-all hover-scale"
          @click="saveConfig"
        >
          保存
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { showNotification } from '../../utils/notificationUtils.js';

// 定义组件属性
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false,
  },
  modelTitle: {
    type: String,
    default: '向量模型配置',
  },
});

// 定义组件事件
const emit = defineEmits(['close', 'save']);

// 定义组件名称
defineOptions({
  name: 'EmbeddingModelSettingsDrawer'
});

// 初始化store
const modelStore = useSettingsStore();

// 组件状态
const modelVersion = ref('');
const customName = ref('');
const apiKey = ref('');
const apiBaseUrl = ref('');
const modelPath = ref('');
const dimension = ref(0);

// 错误状态对象
const errors = ref({
  modelVersion: '',
  apiKey: '',
  apiBaseUrl: ''
});

// 清除错误信息
const clearErrors = () => {
  errors.value.modelVersion = '';
  errors.value.apiKey = '';
  errors.value.apiBaseUrl = '';
};

// 重置表单
const resetForm = () => {
  modelVersion.value = '';
  customName.value = '';
  apiKey.value = '';
  apiBaseUrl.value = '';
  modelPath.value = '';
  dimension.value = 0;
  clearErrors();
};

const closeDrawer = () => {
  resetForm();
  emit('close');
};

const cancelConfig = () => {
  resetForm();
  emit('close');
};

const saveConfig = async () => {
  try {
    // 清除之前的错误
    clearErrors();
    
    // 表单验证
    let hasError = false;
    
    if (!modelVersion.value.trim()) {
      errors.value.modelVersion = '请输入模型版本';
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
    const configData = {
      customName: customName.value,
      apiKey: apiKey.value,
      apiBaseUrl: apiBaseUrl.value,
      versionName: modelVersion.value,
      modelPath: modelPath.value,
      dimension: dimension.value
    };
    
    console.log('保存的向量模型配置数据:', JSON.stringify(configData));
    
    // 调用modelStore保存向量模型配置
    await modelStore.saveEmbeddingModelConfig(props.modelTitle, configData);
    
    // 使用统一的通知服务
    showNotification('向量模型配置保存成功', 'success');
    
    // 保存后重置表单并关闭抽屉
    resetForm();
    closeDrawer();
  } catch (error) {
    console.error('保存向量模型配置失败:', error);
    // 使用统一的通知服务
    showNotification('保存向量模型配置失败，请稍后重试', 'error');
  }
};
</script>

<style scoped>
/* 向量模型配置抽屉样式已经在全局CSS中定义，这里不再重复 */
</style>
