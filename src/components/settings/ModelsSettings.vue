<template>
  <div class="flex flex-col md:flex-row gap-6 max-w-6xl mx-auto h-full">
    <div class="card px-4 py-4 pb-0 depth-1 hover:depth-2 transition-all duration-300 flex-1 min-w-[300px] flex flex-col">
      <div class="flex items-center justify-between mb-4">
        <h4 class="font-medium">已配置模型</h4>
        <div class="relative w-40">
          <input
            type="text"
            v-model="configuredModelsSearch"
            placeholder="搜索模型..."
            class="w-full text-xs pl-7 pr-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all"
          />
          <i class="fa-solid fa-search absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-xs"></i>
        </div>
      </div>

      <div class="space-y-3 overflow-y-auto pr-2 scrollbar-thin flex-1" id="configuredModelsContainer">
        <template v-if="filteredConfiguredModels.length === 0">
          <div class="text-center py-6 text-neutral text-sm">暂无可用模型</div>
        </template>
        <template v-else>
          <div
            v-for="model in filteredConfiguredModels"
            :key="model.name"
            class="model-item p-3 rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 hover:border-primary transition-all"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <div class="p-1 rounded-full w-11 h-11 flex items-center justify-center overflow-hidden">
                  <img v-if="model.icon_url" :src="model.icon_url" :alt="model.name + ' 图标'" class="w-9 h-9 object-contain" />
                  <i v-else class="fa-robot text-xl"></i>
                </div>
                <div>
                  <div class="font-medium text-sm text-gray-900 dark:text-white">
                    {{ model.name }}
                    <span v-if="model.is_default" class="ml-1 text-xs px-1.5 py-0.5 bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary rounded">默认</span>
                  </div>
                </div>
              </div>
              <div class="flex items-center h-full">
                <label class="relative inline-flex items-center cursor-pointer mr-2">
                  <input
                    type="checkbox"
                    :checked="model.enabled"
                    @change="toggleModelEnabled(model)"
                    class="sr-only peer"
                  />
                  <div class="w-9 h-5 bg-gray-200 dark:bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                </label>
                <button
                  class="text-sm text-green-600 dark:text-green-400 border border-green-600 dark:border-green-500 rounded px-2 hover:text-green-700 dark:hover:text-green-300 hover:border-green-700 dark:hover:border-green-400 transition-colors"
                  @click="editModel(model)"
                >
                  新增
                </button>
                <button
                  class="text-sm text-red-600 dark:text-red-400 border border-red-600 dark:border-red-500 rounded px-2 hover:text-red-700 dark:hover:text-red-300 hover:border-red-700 dark:hover:border-red-400 transition-colors ml-2"
                  @click="deleteModelConfig(model)"
                >
                  删除
                </button>
              </div>
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">已配置版本</div>
            <div class="flex flex-wrap gap-2">
              <span v-for="version in model.versions || []" :key="version.version_name || version"
                        class="text-xs text-blue-500 dark:text-blue-400 cursor-pointer hover:text-blue-700 dark:hover:text-blue-300 transition-colors bg-blue-50 dark:bg-blue-900/20 px-2 py-0.5 rounded flex items-center"
                        @click="editModelVersion({...model, selected_version: version})">{{ version.custom_name || version.version_name }}<button 
                      class="ml-1 text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors"
                      @click.stop="deleteModelVersion(model, version)">
                      <i class="fa-solid fa-circle-xmark"></i>
                    </button></span>
            </div>
          </div>
        </template>
      </div>
    </div>

    <div class="card px-4 py-4 pb-0 depth-1 hover:depth-2 transition-all duration-300 flex-1 min-w-[300px] flex flex-col">
      <div class="flex items-center justify-between mb-4">
        <div class="relative inline-flex rounded-full bg-gray-100 dark:bg-gray-800 p-0.5 shadow-sm">
          <button 
            @click="switchTab('inference')"
            class="relative px-2 py-1 text-xs font-medium rounded-full transition-all duration-200 z-10"
            :class="activeTab === 'inference' 
              ? 'text-white font-medium' 
              : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            "
          >
            推理模型
          </button>
          <button 
            @click="switchTab('vector')"
            class="relative px-2 py-1 text-xs font-medium rounded-full transition-all duration-200 z-10"
            :class="activeTab === 'vector' 
              ? 'text-white font-medium' 
              : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            "
          >
            向量模型
          </button>
          <span 
            class="absolute inset-0.5 bg-gray-800 dark:bg-gray-700 rounded-full transition-all duration-300 ease-in-out"
            :style="{
              transform: activeTab === 'inference' ? 'translateX(0)' : 'translateX(100%)',
              width: '50%'
            }"
          ></span>
        </div>
        <div class="relative w-40">
          <input
            type="text"
            v-model="unconfiguredModelsSearch"
            placeholder="搜索模型..."
            class="w-full text-xs pl-7 pr-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all"
          />
          <i class="fa-solid fa-search absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-xs"></i>
        </div>
      </div>

      <!-- 推理模型内容 -->
      <div v-if="activeTab === 'inference'" class="space-y-3 overflow-y-auto pr-2 scrollbar-thin flex-1" id="unconfiguredModelsContainer">
        <template v-if="filteredUnconfiguredModels.length === 0">
          <div class="text-center py-6 text-neutral text-sm">暂无可用模型</div>
        </template>
        <template v-else>
          <div
            v-for="model in filteredUnconfiguredModels"
            :key="model.name"
            class="model-item p-3 rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 hover:border-primary transition-all"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="p-1 rounded-full w-11 h-11 flex items-center justify-center overflow-hidden">
                  <img v-if="model.icon_url" :src="model.icon_url" :alt="model.name + ' 图标'" class="w-9 h-9 object-contain" />
                  <i v-else class="fa-robot text-xl"></i>
                </div>
                <div>
                  <div class="font-medium text-sm text-gray-900 dark:text-white">{{ model.name }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ model.description }}</div>
                </div>
              </div>
              <button
                class="btn btn-primary px-3 py-1 text-xs rounded-lg hover:bg-[#4338ca] hover:shadow-md transform hover:-translate-y-0.5 transition-all text-white"
                @click="configModel(model)"
              >
                配置
              </button>
            </div>
          </div>
        </template>
      </div>
      
      <!-- 向量模型内容 -->
      <div v-else-if="activeTab === 'vector'" class="space-y-3 overflow-y-auto pr-2 scrollbar-thin flex-1">
        <template v-if="filteredUnconfiguredEmbeddingModels.length === 0">
          <div class="text-center py-6 text-neutral text-sm">暂无可用向量模型</div>
        </template>
        <template v-else>
          <div
            v-for="model in filteredUnconfiguredEmbeddingModels"
            :key="model.name"
            class="model-item p-3 rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 hover:border-primary transition-all"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="p-1 rounded-full w-11 h-11 flex items-center justify-center overflow-hidden">
                  <img v-if="model.icon_url" :src="model.icon_url" :alt="model.name + ' 图标'" class="w-9 h-9 object-contain" />
                  <i v-else class="fa-robot text-xl"></i>
                </div>
                <div>
                  <div class="font-medium text-sm text-gray-900 dark:text-white">{{ model.name }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ model.description }}</div>
                </div>
              </div>
              <button
                class="btn btn-primary px-3 py-1 text-xs rounded-lg hover:bg-[#4338ca] hover:shadow-md transform hover:-translate-y-0.5 transition-all text-white"
                @click="configEmbeddingModel(model)"
              >
                配置
              </button>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 默认模型设置已移至系统设置中的对话设置部分 -->
  </div>

  <!-- 模型配置抽屉 -->
  <ModelSettingsDrawer
    :is-visible="isConfigDrawerVisible"
    :model-title="currentEditingModel?.name || '模型配置'"
    @close="closeConfigDrawer"
    @save="saveModelConfig"
  />
  
  <!-- 模型版本表单组件 -->
  <ModelVersionForm 
    :visible="modelVersionFormVisible"
    :model-name="selectedModelName"
    :mode="modelVersionFormMode"
    :model-data="selectedModelData"
    @close="handleModelVersionFormClose"
    @success="handleModelVersionFormSuccess"
  />
  
  <!-- 模型版本编辑组件 -->

  <!-- 向量模型配置抽屉 -->
  <EmbeddingModelSettingsDrawer
    :is-visible="isEmbeddingConfigDrawerVisible"
    :model-title="currentEditingEmbeddingModel?.name || '向量模型配置'"
    @close="closeEmbeddingConfigDrawer"
    @save="saveEmbeddingModelConfig"
  />
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useUiStore } from '../../store/uiStore.js';
import { eventBus } from '../../services/eventBus.js';
import { showNotification } from '../../utils/notificationUtils.js';
import ModelSettingsDrawer from '../models/ModelSettingsDrawer.vue';
import EmbeddingModelSettingsDrawer from '../models/EmbeddingModelSettingsDrawer.vue';
import ModelVersionForm from '../models/ModelVersionForm.vue';

// 初始化store
const settingsStore = useSettingsStore();
const uiStore = useUiStore();
const modelStore = useSettingsStore();

// 状态管理
const configuredModelsSearch = ref('');
const unconfiguredModelsSearch = ref('');
const isConfigDrawerVisible = ref(false);
const currentEditingModel = ref(null);
const activeTab = ref('inference'); // inference 或 vector

// 嵌入模型状态管理
const embeddingModelsSearch = ref('');
const isEmbeddingConfigDrawerVisible = ref(false);
const currentEditingEmbeddingModel = ref(null);

// ModelVersionForm 组件状态管理
const modelVersionFormVisible = ref(false);
const selectedModelName = ref('');
const modelVersionFormMode = ref('add'); // add 或 edit
const selectedModelData = ref(null);

// 计算属性：筛选已配置模型 - 合并LLM模型和嵌入模型
const configuredModels = computed(() => {
  return [
    ...modelStore.configuredModels,
    ...modelStore.configuredEmbeddingModels
  ];
});

// 计算属性：筛选未配置模型 - 直接使用store中的getter
const unconfiguredModels = computed(() => modelStore.unconfiguredModels);

// 计算属性：搜索后的已配置模型，根据标签页状态过滤
const filteredConfiguredModels = computed(() => {
  let models = configuredModels.value;
  
  // 根据当前标签页过滤模型类型
  if (activeTab.value === 'inference') {
    // 只显示推理模型
    models = models.filter(model => model.type !== 'embedding');
  } else if (activeTab.value === 'vector') {
    // 只显示嵌入模型
    models = models.filter(model => model.type === 'embedding');
  }
  
  // 应用搜索过滤
  if (configuredModelsSearch.value.trim()) {
    const searchTerm = configuredModelsSearch.value.toLowerCase();
    models = models.filter(model => 
      (model.name.toLowerCase().includes(searchTerm) || 
       (model.description && model.description.toLowerCase().includes(searchTerm)))
    );
  }
  
  return models;
});

// 计算属性：搜索后的未配置模型
const filteredUnconfiguredModels = computed(() => {
  if (!unconfiguredModelsSearch.value.trim()) {
    return unconfiguredModels.value;
  }
  const searchTerm = unconfiguredModelsSearch.value.toLowerCase();
  return unconfiguredModels.value.filter(model => 
    model.name.toLowerCase().includes(searchTerm) || 
    (model.description && model.description.toLowerCase().includes(searchTerm))
  );
});

// 嵌入模型相关计算属性
const embeddingModels = computed(() => modelStore.allEmbeddingModels);
const configuredEmbeddingModels = computed(() => modelStore.configuredEmbeddingModels);
const unconfiguredEmbeddingModels = computed(() => modelStore.unconfiguredEmbeddingModels);
const isEmbeddingModelLoading = computed(() => modelStore.isEmbeddingModelLoading);

// 计算属性：搜索后的未配置嵌入模型
const filteredUnconfiguredEmbeddingModels = computed(() => {
  if (!unconfiguredModelsSearch.value.trim()) {
    return unconfiguredEmbeddingModels.value;
  }
  const searchTerm = unconfiguredModelsSearch.value.toLowerCase();
  return unconfiguredEmbeddingModels.value.filter(model => 
    model.name.toLowerCase().includes(searchTerm) || 
    (model.description && model.description.toLowerCase().includes(searchTerm))
  );
});

// 计算属性：搜索后的已配置嵌入模型
const filteredConfiguredEmbeddingModels = computed(() => {
  if (!configuredModelsSearch.value.trim()) {
    return configuredEmbeddingModels.value;
  }
  const searchTerm = configuredModelsSearch.value.toLowerCase();
  return configuredEmbeddingModels.value.filter(model => 
    model.name.toLowerCase().includes(searchTerm) || 
    (model.description && model.description.toLowerCase().includes(searchTerm))
  );
});



// 导入图标服务
import iconService from '../../services/iconService';

// 加载模型列表 - 使用modelStore中的方法
// 为模型添加图标URL
const addModelIconUrls = (models) => {
  return iconService.addIconUrls(models);
};

// 预加载图标
const preloadIcons = (models) => {
  const modelNames = models.map(model => model.name);
  iconService.preloadIcons(modelNames);
};

const loadModels = async () => {
  try {
    // 使用modelStore加载模型
    await modelStore.loadModels();
    
    // 获取配置好的模型并添加图标URL
    const configuredModelsWithIcons = addModelIconUrls(modelStore.configuredModels);
    const unconfiguredModelsWithIcons = addModelIconUrls(modelStore.unconfiguredModels);
    
    // 更新模型数据，添加图标URL
    modelStore.updateModelsWithIcons(configuredModelsWithIcons, unconfiguredModelsWithIcons);
    
    // 预加载图标
    preloadIcons([...configuredModelsWithIcons, ...unconfiguredModelsWithIcons]);
    
    // 通知事件总线，模型列表已更新
    eventBus.emit('modelsUpdated', { models: modelStore.models });
  } catch (error) {
    console.error('加载模型列表失败:', error);
    showNotification('加载模型列表失败', 'error');
  }
};

// 加载嵌入模型列表
const loadEmbeddingModels = async () => {
  try {
    // 使用modelStore加载嵌入模型
    await modelStore.loadEmbeddingModels();
    
    // 获取配置好的嵌入模型并添加图标URL
    const configuredEmbeddingModelsWithIcons = addModelIconUrls(modelStore.configuredEmbeddingModels);
    const unconfiguredEmbeddingModelsWithIcons = addModelIconUrls(modelStore.unconfiguredEmbeddingModels);
    
    // 更新嵌入模型数据，添加图标URL
    modelStore.updateEmbeddingModelsWithIcons(configuredEmbeddingModelsWithIcons, unconfiguredEmbeddingModelsWithIcons);
    
    // 预加载图标
    preloadIcons([...configuredEmbeddingModelsWithIcons, ...unconfiguredEmbeddingModelsWithIcons]);
    
    // 通知事件总线，嵌入模型列表已更新
    eventBus.emit('embeddingModelsUpdated', { models: modelStore.allEmbeddingModels });
  } catch (error) {
    console.error('加载嵌入模型列表失败:', error);
    showNotification('加载嵌入模型列表失败', 'error');
  }
};

// 打开配置抽屉
const configModel = (model) => {
  currentEditingModel.value = { ...model };
  isConfigDrawerVisible.value = true;
};

// 编辑模型
const editModel = (model) => {
  // 使用新的方式显示添加模型版本的模态框
  modelVersionFormVisible.value = true;
  selectedModelName.value = model.name;
  modelVersionFormMode.value = 'add';
  selectedModelData.value = null;
};

// 关闭配置抽屉
const closeConfigDrawer = () => {
  isConfigDrawerVisible.value = false;
  currentEditingModel.value = null;
};

// 编辑模型版本
const editModelVersion = (model) => {
  if (model.selected_version) {
    // 获取版本对象
    const version = model.selected_version;
    
    // 填充表单数据并显示模态框
    modelVersionFormVisible.value = true;
    selectedModelName.value = model.name;
    modelVersionFormMode.value = 'edit';
    selectedModelData.value = {
      id: typeof version === 'object' ? version.version_name : version, // 只使用version_name字段
      modelName: model.name,
      versionName: typeof version === 'object' ? version.version_name : version,
      customName: typeof version === 'object' ? (version.custom_name || '') : '',
      apiKey: typeof version === 'object' ? (version.api_key || '') : '',
      apiBaseUrl: typeof version === 'object' ? (version.api_base_url || 'https://api.openai.com') : 'https://api.openai.com',
      streamingConfig: typeof version === 'object' ? (version.streaming_config || false) : false
    };
  }
};

// 处理模型版本表单关闭
const handleModelVersionFormClose = () => {
  modelVersionFormVisible.value = false;
  selectedModelName.value = '';
  selectedModelData.value = null;
};

// 处理模型版本表单成功
const handleModelVersionFormSuccess = () => {
  modelVersionFormVisible.value = false;
  selectedModelName.value = '';
  selectedModelData.value = null;
  // 重新加载模型数据
  loadModels();
};

// 删除模型版本 - 使用modelStore中的方法
const deleteModelVersion = async (model, version) => {
  try {
    // 检查模型类型，调用相应的方法
    if (model.type === 'embedding') {
      // 嵌入模型
      await modelStore.deleteEmbeddingModelVersion(model.name, version.version_name);
    } else {
      // LLM模型
      await modelStore.deleteModelVersion(model.name, version.version_name);
    }
    // modelStore内部会处理通知和加载模型列表
  } catch (error) {
    // modelStore内部已处理错误通知
    console.error('删除模型版本失败:', error);
  }
};

// 保存模型配置 - 使用modelStore中的方法
const saveModelConfig = async (config) => {
  try {
    // 调用modelStore保存配置
    await modelStore.saveModelConfig(currentEditingModel.value.name, {
      customName: config.customName,
      apiKey: config.apiKey,
      apiBaseUrl: config.apiBaseUrl,
      version_name: config.versionName,
      streaming_config: config.isStreamingEnabled
    });
    
    // 关闭抽屉
    closeConfigDrawer();
    
    // 显示成功提示
    showNotification('模型配置保存成功', 'success');
  } catch (error) {
    // modelStore内部已处理错误通知
    console.error('保存模型配置失败:', error);
  }
};

// 删除模型配置 - 使用modelStore中的方法
const deleteModelConfig = async (model) => {
  try {
    // 检查模型类型，调用相应的方法
    if (model.type === 'embedding') {
      // 嵌入模型
      await modelStore.deleteEmbeddingModelConfig(model.name);
    } else {
      // LLM模型
      await modelStore.deleteModelConfig(model.name);
    }
    // modelStore内部会处理通知和加载模型列表
  } catch (error) {
    // modelStore内部已处理错误通知
    console.error('删除模型配置失败:', error);
  }
};

// 切换模型启用状态 - 使用modelStore中的方法
const toggleModelEnabled = async (model) => {
  try {
    const newEnabledState = !model.enabled;
    
    // 检查模型类型，调用相应的方法
    if (model.type === 'embedding') {
      // 嵌入模型
      await modelStore.toggleEmbeddingModelEnabled(model.name, newEnabledState);
    } else {
      // LLM模型
      await modelStore.toggleModelEnabled(model.name, newEnabledState);
    }
    // modelStore内部会处理通知和加载模型列表
  } catch (error) {
    // modelStore内部已处理错误通知
    console.error('更新模型启用状态失败:', error);
    // 恢复原始状态
    await loadModels();
    await loadEmbeddingModels();
  }
};

// 切换选项卡
const switchTab = (tab) => {
  activeTab.value = tab;
};

// 注：默认模型设置功能已移至系统设置中的对话设置部分

// 组件挂载时加载模型
onMounted(() => {
  // 首先加载本地存储的设置
  modelStore.loadModelSettings();
  
  // 然后加载模型配置
  loadModels();
  loadEmbeddingModels();
  
  // 监听模型更新事件
  eventBus.on('modelUpdated', loadModels);
  eventBus.on('embeddingModelUpdated', loadEmbeddingModels);
});

// 组件卸载时清理事件监听器
onUnmounted(() => {
  eventBus.off('modelUpdated', loadModels);
  eventBus.off('embeddingModelUpdated', loadEmbeddingModels);
});

// 监听设置面板变化，刷新模型列表
watch(
  () => uiStore.activePanel,
  (newPanel) => {
    if (newPanel === 'settings' && settingsStore.activeSection === 'models') {
      loadModels();
    }
  }
);

// 监听设置部分变化，刷新模型列表
watch(
  () => settingsStore.activeSection,
  (newSection) => {
    if (uiStore.activePanel === 'settings' && newSection === 'models') {
      loadModels();
      loadEmbeddingModels();
    }
  }
);

// 监听modelStore中的models变化 - 不再需要手动同步，直接使用getter
// watch(
//   () => modelStore.models,
//   (newModels) => {
//     models.value = newModels;
//   },
//   { deep: true }
// );

// 打开嵌入模型配置抽屉
const configEmbeddingModel = (model) => {
  currentEditingEmbeddingModel.value = { ...model };
  isEmbeddingConfigDrawerVisible.value = true;
};

// 关闭嵌入模型配置抽屉
const closeEmbeddingConfigDrawer = () => {
  isEmbeddingConfigDrawerVisible.value = false;
  currentEditingEmbeddingModel.value = null;
};

// 保存嵌入模型配置
const saveEmbeddingModelConfig = async (config) => {
  try {
    // 调用modelStore保存配置
    await modelStore.saveEmbeddingModelConfig(currentEditingEmbeddingModel.value.name, {
      customName: config.customName,
      apiKey: config.apiKey,
      apiBaseUrl: config.apiBaseUrl,
      versionName: config.versionName,
      streamingConfig: config.isStreamingEnabled
    });
    
    // 关闭抽屉
    closeEmbeddingConfigDrawer();
    
    // 显示成功提示
    showNotification('嵌入模型配置保存成功', 'success');
  } catch (error) {
    // modelStore内部已处理错误通知
    console.error('保存嵌入模型配置失败:', error);
  }
};

// 删除嵌入模型配置
const deleteEmbeddingModelConfig = async (model) => {
  try {
    // 使用modelStore删除嵌入模型配置
    await modelStore.deleteEmbeddingModelConfig(model.name);
    // modelStore内部会处理通知和加载模型列表
  } catch (error) {
    // modelStore内部已处理错误通知
    console.error('删除嵌入模型配置失败:', error);
  }
};

// 切换嵌入模型启用状态
const toggleEmbeddingModelEnabled = async (model) => {
  try {
    const newEnabledState = !model.enabled;
    
    // 使用modelStore更新启用状态
    await modelStore.toggleEmbeddingModelEnabled(model.name, newEnabledState);
    // modelStore内部会处理通知和加载模型列表
  } catch (error) {
    // modelStore内部已处理错误通知
    console.error('更新嵌入模型启用状态失败:', error);
    // 恢复原始状态
    await loadEmbeddingModels();
  }
};
</script>

<style scoped>
.model-item {
  transition: all 0.2s ease;
  margin-top: 4px;
}

.model-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.text-xs.text-gray-500.mb-1 {
  border-top: 1px solid #e5e7eb;
  padding-top: 0.5rem;
  margin-top: 0.5rem;
  font-weight: bold;
}
</style>


