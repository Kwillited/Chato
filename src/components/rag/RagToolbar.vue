<template>
  <div class="toolbar flex justify-between items-center mb-3 p-2 bg-gray-50 dark:bg-gray-800 dark:border-gray-700 rounded-lg border border-gray-100 transition-all duration-300">
    <Button
      id="createKnowledgeBaseBtn"
      icon="fa-folder-plus"
      tooltip="新建知识库"
      @click="handleCreateKnowledgeBase"
      size="sm"
      shape="full"
    />

    <Button
      id="deleteAllBtn"
      icon="fa-trash-can"
      tooltip="删除所有文件夹"
      @click="handleDeleteAll"
      :disabled="loading"
      size="sm"
      shape="full"
      class="text-neutral hover:text-red-500 hover:bg-red-50"
    />
    <Button
      :id="isRagManagementView ? '返回对话' : '切换到文件管理'"
      :icon="isRagManagementView ? 'fa-comment' : 'fa-folder-tree'"
      :tooltip="isRagManagementView ? '返回对话' : '切换到文件管理'"
      @click="handleViewToggle"
      size="sm"
      shape="full"
    />
  </div>
  
  <!-- 搜索框 -->
  <SearchBar v-model="searchQuery" placeholder="搜索知识库..." @input="handleSearch" />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useVectorStore } from '../../store/vectorStore.js';
import { showNotification } from '../../services/notificationUtils.js';
import Button from '../common/Button.vue';
import SearchBar from '../common/SearchBar.vue';

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
});

// 初始化store
const settingsStore = useSettingsStore();
const ragStore = useVectorStore();

// 搜索查询
const searchQuery = ref('');
// 当前是否处于RAG文件管理视图
const isRagManagementView = ref(false);

// 处理新建知识库
const handleCreateKnowledgeBase = () => {
  // 触发创建知识库事件，由FilePanel组件处理并显示模态框
  const event = new CustomEvent('createKnowledgeBase');
  window.dispatchEvent(event);
};

// 处理删除所有文件
const handleDeleteAll = () => {
  // 触发删除所有文件事件，由FilePanel组件处理并显示确认模态框
  const event = new CustomEvent('deleteAll');
  window.dispatchEvent(event);
};

// 处理视图切换
const handleViewToggle = () => {
  if (isRagManagementView.value) {
    settingsStore.setActiveContent('chat');
    isRagManagementView.value = false;
  } else {
    settingsStore.setActiveContent('ragManagement');
    isRagManagementView.value = true;
  }
};

// 监听store中的activeContent变化
watch(
  () => settingsStore.activeContent,
  (newContent) => {
    isRagManagementView.value = newContent === 'ragManagement';
  },
  { immediate: true }
);

// 初始化当前视图状态
const initializeViewState = () => {
  // 直接从store获取当前活动内容
  isRagManagementView.value = settingsStore.activeContent === 'ragManagement';
};

onMounted(() => {
  initializeViewState();
});

// 处理搜索
const handleSearch = () => {
  // 直接调用store方法进行搜索
  ragStore.searchKnowledgeBase(searchQuery.value);
};
</script>

<style scoped>
/* 禁用状态样式 */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed !important;
}

button:disabled:hover {
  background-color: transparent !important;
}
</style>