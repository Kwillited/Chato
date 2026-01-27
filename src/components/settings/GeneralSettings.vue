<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <div class="card p-5 depth-1 hover:depth-2 transition-all duration-300">
      <div class="flex items-center">
        <img
          src="https://picsum.photos/id/64/60/60"
          alt="用户头像"
          class="w-14 h-14 rounded-full mr-4 border-2 border-white shadow-sm"
        />
        <div>
          <div class="font-medium">Administrator</div>
          <div class="text-sm text-neutral">Administrator@example.com</div>
        </div>
      </div>
    </div>

    <!-- 导出和删除按钮 -->
    <div class="card p-4 depth-1 hover:depth-2 transition-all duration-300 bg-white dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-gray-600">
      <div class="flex justify-between items-center">
        <h3 class="font-medium text-sm text-gray-700 dark:text-gray-200">对话管理</h3>
        <div class="flex gap-2">
          <Button
            id="exportAllBtn"
            shape="full"
            size="md"
            icon="fa-download"
            tooltip="导出所有对话"
            @click="handleExportAll"
            class="w-8 h-8 p-1.5 text-gray-500 dark:text-gray-300 hover:text-primary hover:bg-primary/10 rounded-full transition-colors duration-200"
          />
          <Button
            id="deleteAllBtn"
            shape="full"
            size="md"
            icon="fa-trash-can"
            tooltip="删除所有对话"
            @click="showDeleteAllModal = true"
            class="w-8 h-8 p-1.5 text-gray-500 dark:text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors duration-200"
          />
        </div>
      </div>
    </div>

    <div class="card depth-1 hover:depth-2 transition-all duration-300">
      <!-- 选项卡导航 -->
      <div class="border-b">
        <div class="flex">
          <button
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'chat' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="activeTab = 'chat'"
          >
            对话设置
          </button>
          <button
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'style' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="activeTab = 'style'"
          >
            样式设置
          </button>
        </div>
      </div>
      
      <!-- 对话设置选项卡内容 -->
      <div v-show="activeTab === 'chat'" class="p-4">
        <div class="space-y-4">

          <SettingItem
            type="toggle"
            title="启用流式输出"
            description="启用后，对话将以流式方式输出，而不是等待全部生成完成"
            v-model="settingsStore.systemSettings.streamingEnabled"
          />

          <div class="setting-item p-3 rounded-lg">
            <div>
              <div class="font-medium text-sm">默认模型</div>
              <div class="text-xs text-neutral mt-0.5">新对话默认使用的AI模型</div>

              <!-- 自定义下拉框实现 -->
              <div class="relative">
                <!-- 当没有模型时，显示一个只读的输入框 -->
                <input
                  v-if="!isLoading && allModelVersions.length === 0"
                  type="text"
                  value="请先配置模型"
                  class="input-field w-full text-sm px-2 py-1.5 mt-2 focus:outline-none bg-gray-50 text-gray-500 cursor-not-allowed"
                  readonly
                />
                <!-- 正常的下拉框 -->
                <select
                  v-else
                  class="input-field w-full text-sm px-2 py-1.5 mt-2 focus:outline-none focus:ring-1 focus:ring-primary"
                  v-model="defaultModel"
                  @change="setDefaultModel"
                >
                  <option v-if="isLoading" value="">加载中...</option>
                  <option v-else-if="allModelVersions.length > 0" :value="''" disabled>选择默认模型</option>
                  <option v-for="version in allModelVersions" :key="version.id" :value="version.id">{{ version.displayName }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 样式设置选项卡内容 -->
      <div v-show="activeTab === 'style'" class="p-4">
        <div class="space-y-4">
          <SettingItem
            type="toggle"
            title="深色模式"
            description="启用后，界面将切换到深色主题，减轻夜间使用时的视觉疲劳"
            v-model="settingsStore.systemSettings.darkMode"
          />
          <SettingItem
            type="button-group"
            title="对话样式"
            description="选择对话界面的显示样式"
            v-model="chatStyleValue"
            :options="[
              { value: 'bubble', label: '气泡模式', icon: 'fa-comment' },
              { value: 'document', label: '文档样式', icon: 'fa-file-lines' }
            ]"
            @change="setChatStyle"
          />

          <SettingItem
            type="button-group"
            title="文件视图模式"
            description="选择文件管理界面的显示方式"
            v-model="viewModeValue"
            :options="[
              { value: 'grid', label: '网格视图', icon: 'fa-th' },
              { value: 'list', label: '列表视图', icon: 'fa-list' }
            ]"
            @change="setViewMode"
          />
        </div>
      </div>
    </div>
    
    <!-- 确认删除所有对话模态框 -->
    <ConfirmationModal
      :visible="showDeleteAllModal"
      title="确认删除"
      message="确定要删除所有对话吗？这将删除所有历史对话，无法恢复！"
      confirmText="确认删除"
      :loading="isDeletingAll"
      loadingText="删除中..."
      @confirm="handleDeleteAllConfirm"
      @close="showDeleteAllModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { eventBus } from '../../services/eventBus.js';
import { showNotification } from '../../utils/notificationUtils.js';
import SettingItem from '../common/SettingItem.vue';
import { Button } from '../library/index.js';
import ConfirmationModal from '../common/ConfirmationModal.vue';

const settingsStore = useSettingsStore();
const modelStore = useSettingsStore();
const chatStore = useChatStore();

// 状态管理
const isLoading = ref(false);
const models = ref([]);
const defaultModel = ref('');
const activeTab = ref('chat'); // 默认选中对话设置选项卡
// 对话管理相关状态
const showDeleteAllModal = ref(false);
const isDeletingAll = ref(false);

// 计算属性：聊天样式值（转换为字符串格式）
const chatStyleValue = computed({
  get: () => settingsStore.systemSettings.chatStyleDocument ? 'document' : 'bubble',
  set: (value) => {
    settingsStore.systemSettings.chatStyleDocument = value === 'document';
  }
});

// 计算属性：文件视图模式值
const viewModeValue = computed({
  get: () => settingsStore.systemSettings.viewMode,
  set: (value) => {
    settingsStore.systemSettings.viewMode = value;
  }
});

// 计算属性：所有可用的模型版本
const allModelVersions = computed(() => {
  const versions = [];
  
  models.value.forEach(model => {
    if (model.configured && model.enabled && model.versions) {
      model.versions.forEach(version => {
        // 只使用version_name字段
        const versionName = version?.version_name;
        if (versionName) {
          // 构造模型版本标识，格式为 "name-versionName"
          const id = `${model.name}-${versionName}`;
          const displayName = `${model.name}-${version.custom_name || versionName}`;
          
          versions.push({
            id,
            displayName
          });
        }
      });
    }
  });
  
  return versions;
});

// 从后端加载模型列表
async function loadModels() {
  try {
    isLoading.value = true;
    
    // 从模型设置store获取模型数据
    if (modelStore.allModels && modelStore.allModels.length > 0) {
      models.value = modelStore.allModels;
    } else {
      // 如果模型数据尚未加载，则触发加载
      await modelStore.loadModels();
      models.value = modelStore.allModels;
    }
    
    // 加载系统设置中的默认模型
    defaultModel.value = settingsStore.getDefaultModel();
    
    // 如果系统设置中没有默认模型，但模型存储中有选择，则使用它
    if (!defaultModel.value && modelStore.selectedModel) {
      defaultModel.value = modelStore.selectedModel;
      settingsStore.setDefaultModel(defaultModel.value);
    }
    
    // 如果有模型但没有选择默认模型，自动选择第一个模型
    if (!defaultModel.value && allModelVersions.value.length > 0) {
      defaultModel.value = allModelVersions.value[0].id;
      settingsStore.setDefaultModel(defaultModel.value);
      modelStore.selectModel(defaultModel.value);
      eventBus.emit('modelSelected', { model: defaultModel.value });
    }
    
    // 确保在没有模型时，默认显示为空字符串，这样可以显示disabled的提示选项
    if (allModelVersions.value.length === 0) {
      defaultModel.value = '';
    }
  } catch (error) {
    console.error('加载模型列表失败:', error);
  } finally {
    isLoading.value = false;
  }
}

// 设置默认模型
function setDefaultModel() {
  if (!defaultModel.value) return;
  
  try {
    // 设置到系统设置中
    settingsStore.setDefaultModel(defaultModel.value);
    
    // 同步到模型设置store
    modelStore.selectModel(defaultModel.value);
    
    // 发送模型选择变更事件
    eventBus.emit('modelSelected', { model: defaultModel.value });
    
    // 显示成功提示
    showNotification('默认模型已设置', 'success');
  } catch (error) {
    console.error('设置默认模型失败:', error);
    showNotification('设置失败: ' + error.message, 'error');
  }
}

// 监听模型列表更新
function handleModelsUpdated({ models: updatedModels }) {
  models.value = updatedModels;
  
  // 检查当前默认模型是否仍然存在于可用模型中
  const isDefaultModelStillAvailable = allModelVersions.value.some(
    version => version.id === defaultModel.value
  );
  
  // 如果默认模型不再可用，且还有其他可用模型，则自动选择第一个可用模型
  if (!isDefaultModelStillAvailable && allModelVersions.value.length > 0) {
    defaultModel.value = allModelVersions.value[0].id;
    settingsStore.setDefaultModel(defaultModel.value);
    modelStore.selectModel(defaultModel.value);
    eventBus.emit('modelSelected', { model: defaultModel.value });
    showNotification('默认模型已更新为: ' + allModelVersions.value[0].displayName, 'success');
  } else if (!isDefaultModelStillAvailable && allModelVersions.value.length === 0) {
    // 如果没有可用模型，清除默认模型设置
    defaultModel.value = '';
    settingsStore.setDefaultModel('');
    modelStore.selectModel('');
  }
}

onMounted(async () => {
  // 确保深色模式立即应用
  settingsStore.applyDarkMode();
  
  // 加载模型列表和默认模型设置
  await loadModels();
  
  // 监听模型列表更新事件
  eventBus.on('modelsUpdated', handleModelsUpdated);
});

// 监听流式输出设置变化，自动保存
watch(
  () => settingsStore.systemSettings.streamingEnabled,
  (_newValue) => {
    settingsStore.saveSettings();
  }
);

// 监听darkMode变化，立即应用
watch(
  () => settingsStore.systemSettings.darkMode,
  (_newValue) => {
    settingsStore.applyDarkMode();
    settingsStore.saveSettings();
  }
);

// 监听其他系统设置变化，自动保存
watch(
  () => settingsStore.systemSettings,
  (_newValue) => {
    settingsStore.saveSettings();
  },
  { deep: true }
);

onUnmounted(() => {
  // 移除事件监听
  eventBus.off('modelsUpdated', handleModelsUpdated);
});

// 设置聊天样式
const setChatStyle = (style) => {
  settingsStore.updateSystemSettings({
    chatStyleDocument: style === 'document'
  });
};

// 设置文件视图模式
const setViewMode = (mode) => {
  settingsStore.updateSystemSettings({
    viewMode: mode
  });
};

// 切换深色模式
const _toggleDarkMode = () => {
  settingsStore.toggleDarkMode();
};

// 导出所有对话
const handleExportAll = () => {
  try {
    chatStore.exportAllChats();
    showNotification('所有对话已导出', 'success');
  } catch (error) {
    console.error('导出对话失败:', error);
    showNotification('导出失败: ' + error.message, 'error');
  }
};

// 确认删除所有对话
const handleDeleteAllConfirm = async () => {
  try {
    isDeletingAll.value = true;
    await chatStore.deleteAllChats();
    showNotification('所有对话已删除', 'success');
  } catch (error) {
    console.error('删除对话失败:', error);
    showNotification('删除失败: ' + error.message, 'error');
  } finally {
    isDeletingAll.value = false;
    showDeleteAllModal.value = false;
  }
};


</script>
