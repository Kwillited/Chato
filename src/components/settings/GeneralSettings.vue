<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <Card class="p-5">
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
    </Card>

    <!-- 导出和删除按钮 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- 导出对话卡片 -->
      <Card class="p-4">
        <div class="flex justify-between items-center">
          <h3 class="font-medium text-sm text-gray-700 dark:text-gray-200">导出对话</h3>
          <Button
            id="exportAllBtn"
            shape="full"
            size="md"
            icon="fa-download"
            tooltip="导出所有对话"
            @click="handleExportAll"
            class="w-8 h-8 p-1.5 text-gray-500 dark:text-gray-300 hover:text-primary hover:bg-primary/10 rounded-full transition-colors duration-200"
          />
        </div>
      </Card>
      <!-- 删除对话卡片 -->
      <Card class="p-4">
        <div class="flex justify-between items-center">
          <h3 class="font-medium text-sm text-gray-700 dark:text-gray-200">删除对话</h3>
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
      </Card>
    </div>

    <Card>
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
          <button
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'notification' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="activeTab = 'notification'"
          >
            通知设置
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
      
      <!-- 通知设置选项卡内容 -->
      <div v-show="activeTab === 'notification'" class="p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 新消息通知卡片 -->
          <Card class="p-4">
            <SettingItem
              type="toggle"
              title="新消息通知"
              description="当收到AI回复时通知"
              v-model="settingsStore.notificationsConfig.newMessage"
              @change="settingsStore.saveSettings"
            />
          </Card>
          
          <!-- 声音提示卡片 -->
          <Card class="p-4">
            <SettingItem
              type="toggle"
              title="声音提示"
              description="新消息通知时播放提示音"
              v-model="settingsStore.notificationsConfig.sound"
              @change="settingsStore.saveSettings"
            />
          </Card>
          
          <!-- 系统通知卡片 -->
          <Card class="p-4">
            <SettingItem
              type="toggle"
              title="系统通知"
              description="显示应用更新等系统通知"
              v-model="settingsStore.notificationsConfig.system"
              @change="settingsStore.saveSettings"
            />
          </Card>
          
          <!-- 通知显示时间卡片 -->
          <Card class="p-4">
            <SettingItem
              type="select"
              title="通知显示时间"
              description="控制通知在屏幕上停留的时间"
              v-model="settingsStore.notificationsConfig.displayTime"
              :options="displayTimeOptions"
              @change="settingsStore.saveSettings"
            />
          </Card>
        </div>
      </div>
    </Card>
    
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
import { ref, computed, onMounted, watch } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { showNotification } from '../../utils/notificationUtils.js';
import SettingItem from '../common/SettingItem.vue';
import { Button, Card } from '../library/index.js';
import ConfirmationModal from '../common/ConfirmationModal.vue';

const settingsStore = useSettingsStore();
const chatStore = useChatStore();

// 状态管理
const activeTab = ref('chat'); // 默认选中对话设置选项卡
// 对话管理相关状态
const showDeleteAllModal = ref(false);
const isDeletingAll = ref(false);

// 计算属性：聊天样式值
const chatStyleValue = computed({
  get: () => settingsStore.systemSettings.chatStyle,
  set: (value) => {
    settingsStore.systemSettings.chatStyle = value;
  }
});

// 计算属性：文件视图模式值
const viewModeValue = computed({
  get: () => settingsStore.systemSettings.viewMode,
  set: (value) => {
    settingsStore.systemSettings.viewMode = value;
  }
});

// 通知显示时间选项
const displayTimeOptions = [
  { value: '2秒', label: '2秒' },
  { value: '5秒', label: '5秒' },
  { value: '10秒', label: '10秒' }
];

// 所有可用的模型版本已从 useModelUtils 中获取

onMounted(() => {
  // 确保深色模式立即应用
  settingsStore.applyDarkMode();
});

// 监听系统设置变化，自动保存
watch(
  () => settingsStore.systemSettings,
  (_newValue) => {
    settingsStore.applyDarkMode(); // 确保深色模式立即应用
    settingsStore.saveSettings();
  },
  { deep: true }
);



// 设置聊天样式
const setChatStyle = (style) => {
  settingsStore.updateSystemSettings({
    chatStyle: style
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
