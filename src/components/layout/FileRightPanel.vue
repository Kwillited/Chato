<template>
  <div 
    class="h-full overflow-hidden"
  >
    <!-- 右侧面板内容 -->
    <div class="h-full flex flex-col">
      <!-- 面板切换按钮 -->
      <div class="p-2 pb-0">
        <TabSwitcher
          :tabs="[
            { id: 'fileProperties', name: '属性概览' },
            { id: 'fileOverview', name: '文件概览' }
          ]"
          :active-tab="activeTab"
          :border-radius="'8px'"
          container-class="w-full"
          tab-class="px-2 py-1 text-xs"
          @tab-change="(tab) => activeTab = tab"
        />
      </div>
      
      <!-- 面板内容区域 -->
      <div class="flex-1 p-2">
        <!-- 文件概览面板 -->
        <div v-if="activeTab === 'fileOverview'" class="flex flex-col">
          <!-- 检索内容 -->
          <div class="mb-4">
            <h3 class="text-sm font-semibold text-gray-500 mb-2">检索内容</h3>
            <Card class="p-3">
              <div class="flex items-center justify-center py-4">
                <p class="text-sm text-gray-500 dark:text-gray-400">检索内容区域</p>
              </div>
            </Card>
          </div>
          
          <!-- 文件列表 -->
          <div class="flex-1 flex flex-col">
            <div class="flex justify-between items-center mb-2">
              <h3 class="text-sm font-semibold text-gray-500">最近文件</h3>
              <div class="flex space-x-2">
                <Button
                  shape="rounded"
                  size="md"
                  variant="secondary"
                  icon="fa-refresh"
                  tooltip="刷新"
                  @click="refreshFileList"
                />
              </div>
            </div>
            
            <Card class="h-[calc(100vh-330px)] overflow-hidden flex flex-col mb-4">
              <div class="flex-1 overflow-y-auto p-2 scrollbar-thin">
                <!-- 文件列表 -->
                <div v-if="fileStore.files && fileStore.files.length > 0">
                  <div
                    v-for="file in recentFiles"
                    :key="file.id"
                    class="file-item mb-3 p-2 rounded border border-gray-200 dark:border-dark-border hover:bg-gray-100 dark:hover:bg-dark-700 transition-colors"
                    :class="{ 'selected': selectedFiles.has(file.id) }"
                  >
                    <div class="flex items-start space-x-2">
                      <!-- 选择复选框 -->
                      <input
                        type="checkbox"
                        :id="`file-${file.id}`"
                        :checked="selectedFiles.has(file.id)"
                        @change="toggleFileSelection(file.id)"
                        class="mt-1"
                      />
                      
                      <!-- 文件信息 -->
                      <div class="flex-1">
                        <div class="flex justify-between items-center mb-1">
                          <span class="text-xs font-semibold text-gray-500 dark:text-gray-400">
                            {{ file.name }}
                          </span>
                          <span class="text-xs text-gray-400 dark:text-gray-500">
                            {{ formatFileSize(file.size) }}
                          </span>
                        </div>
                        <p class="text-xs text-gray-600 dark:text-dark-text-secondary">
                          {{ file.path }}
                        </p>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          添加时间: {{ formatTime(file.timestamp) }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 无文件提示 -->
                <div v-else class="text-center py-4 text-xs text-gray-500 dark:text-gray-400">
                  暂无文件信息
                </div>
              </div>
              

            </Card>
          </div>
        </div>
        
        <!-- 文件属性面板 -->
        <div v-else-if="activeTab === 'fileProperties'" class="h-full flex flex-col">
          <div class="panel-section flex-1 flex flex-col">
            <!-- 文件夹属性 -->
            <Card v-if="selectedFolder" class="flex-1 overflow-hidden flex flex-col p-3">
              <h4 class="text-sm font-semibold text-gray-500 mb-3">文件夹属性</h4>
              <div class="space-y-1">
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">文件夹名称: {{ selectedFolder?.name || '未选择文件夹' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">文件夹路径: {{ selectedFolder?.path || '未知' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">文件夹ID: {{ folderInfo?.id || '未知' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">创建时间: {{ folderInfo?.created_at ? formatTime(folderInfo.created_at) : '未知' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">修改时间: {{ folderInfo?.updated_at ? formatTime(folderInfo.updated_at) : '未知' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">描述: {{ folderInfo?.description || '无' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">嵌入模型: {{ folderInfo?.embedding_model || '默认' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">分块大小: {{ folderInfo?.chunk_size || '默认' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">分块重叠: {{ folderInfo?.chunk_overlap || '默认' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">总文件数: {{ getTotalFileCount() }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">文件夹数: {{ getFolderCount() }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">文档数: {{ getDocumentCount() }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">总大小: {{ getTotalFileSize() }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">最新添加: {{ getLastAddedTime() }}</p>
              </div>
            </Card>
            
            <!-- 选中文件属性 -->
            <Card v-else-if="selectedFiles.size > 0" class="flex-1 overflow-hidden flex flex-col p-3">
              <h4 class="text-sm font-semibold text-gray-500 mb-3">选中文件属性</h4>
              <div class="space-y-3">
                <div class="flex justify-between items-center">
                  <span class="text-xs text-gray-600 dark:text-dark-text-secondary">文件数量:</span>
                  <span class="text-xs text-gray-800 dark:text-white">{{ selectedFiles.size }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-xs text-gray-600 dark:text-dark-text-secondary">总大小:</span>
                  <span class="text-xs text-gray-800 dark:text-white">{{ formatFileSize(getSelectedFilesSize()) }}</span>
                </div>
                <div class="border-t border-gray-200 dark:border-dark-border pt-3">
                  <h5 class="text-xs font-semibold text-gray-500 mb-2">操作</h5>
                  <div class="flex space-x-2">
                    <Button
                      shape="full"
                      size="sm"
                      icon="fa-download"
                      tooltip="下载"
                      @click="downloadSelectedFiles"
                      class="transition-all duration-200 hover:scale-105"
                      :class="{
                        'bg-primary hover:bg-primary/90 text-white': true
                      }"
                    />
                    <Button
                      shape="full"
                      size="sm"
                      icon="fa-trash-can"
                      tooltip="删除"
                      @click="deleteSelectedFiles"
                      class="transition-all duration-200 hover:scale-105"
                      :class="{
                        'bg-red-500 hover:bg-red-600 text-white': true
                      }"
                    />
                  </div>
                </div>
              </div>
            </Card>
            
            <!-- 未选中文件提示 -->
            <Card v-else class="flex-1 flex items-center justify-center">
              <p class="text-xs text-gray-500 dark:text-gray-400">请选择文件或文件夹查看属性</p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settingsStore.js';
import { useFileStore } from '../../store/fileStore.js';
import { useUiStore } from '../../store/uiStore.js';
import { Button, Card } from '../library/index.js';
import { showNotification } from '../../utils/notificationUtils.js';
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
// 导入公共工具函数
import { formatTime } from '../../utils/time.js';
import { eventBus } from '../../services/eventBus.js';
import TabSwitcher from '../common/TabSwitcher.vue';

// 定义props
const _props = defineProps({
  isInitialLoading: {
    type: Boolean,
    default: true
  }
});

// 初始化stores
const settingsStore = useSettingsStore();
const fileStore = useFileStore();
const uiStore = useUiStore();

// 文件选择状态
const selectedFiles = ref(new Set());

// 标签页切换状态
const activeTab = ref('fileProperties');

// 当前选中的文件夹
const selectedFolder = ref(null);
// 文件夹详细信息
const folderInfo = ref(null);

// 监听fileStore中的currentFolder变化
watch(() => fileStore.currentFolder, async (newFolder) => {
  selectedFolder.value = newFolder;
  if (newFolder && newFolder.id) {
    await loadFolderInfo(newFolder.id);
  } else {
    folderInfo.value = null;
  }
});

// 加载文件夹详细信息
const loadFolderInfo = async (folderId) => {
  try {
    const info = await fileStore.getFolderInfo(folderId);
    folderInfo.value = info;
  } catch (error) {
    console.error('加载文件夹信息失败:', error);
    folderInfo.value = null;
  }
};

// 计算最近文件（按时间排序）
const recentFiles = computed(() => {
  if (!fileStore.files) return [];
  return [...fileStore.files]
    .sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0))
    .slice(0, 10);
});

// 计算总文件数
const getTotalFileCount = () => {
  return fileStore.files ? fileStore.files.length : 0;
};

// 计算文件夹数
const getFolderCount = () => {
  if (!fileStore.folders) return 0;
  return fileStore.folders.length;
};

// 计算文档数
const getDocumentCount = () => {
  if (!fileStore.files) return 0;
  return fileStore.files.filter(file => file.type === 'document').length;
};

// 计算总文件大小
const getTotalFileSize = () => {
  if (!fileStore.files) return '0 B';
  const totalSize = fileStore.files.reduce((sum, file) => sum + (file.size || 0), 0);
  return formatFileSize(totalSize);
};

// 计算选中文件大小
const getSelectedFilesSize = () => {
  if (!fileStore.files || selectedFiles.value.size === 0) return 0;
  return fileStore.files
    .filter(file => selectedFiles.value.has(file.id))
    .reduce((sum, file) => sum + (file.size || 0), 0);
};

// 获取最新添加时间
const getLastAddedTime = () => {
  if (!fileStore.files || fileStore.files.length === 0) {
    return '无';
  }
  
  const files = fileStore.files;
  let lastAdded = 0;
  
  files.forEach(file => {
    if ((file.timestamp || 0) > lastAdded) {
      lastAdded = file.timestamp || 0;
    }
  });
  
  return formatTime(lastAdded);
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 切换文件选择状态
const toggleFileSelection = (fileId) => {
  if (selectedFiles.value.has(fileId)) {
    selectedFiles.value.delete(fileId);
  } else {
    selectedFiles.value.add(fileId);
  }
};

// 刷新文件列表
const refreshFileList = () => {
  // 这里可以添加刷新文件列表的逻辑
  showNotification('文件列表已刷新', 'success');
};

// 下载选中文件
const downloadSelectedFiles = () => {
  if (selectedFiles.value.size === 0) return;
  // 这里可以添加下载文件的逻辑
  showNotification(`正在下载 ${selectedFiles.value.size} 个文件`, 'success');
};

// 删除选中文件
const deleteSelectedFiles = () => {
  if (selectedFiles.value.size === 0) return;
  // 这里可以添加删除文件的逻辑
  showNotification(`已删除 ${selectedFiles.value.size} 个文件`, 'success');
  selectedFiles.value.clear();
};

// 监听文件变化，重置选择状态
watch(() => fileStore.files, () => {
  selectedFiles.value.clear();
}, { deep: true });

// 组件挂载时监听事件
onMounted(() => {
  // 监听显示文件夹属性的事件
  eventBus.on('showFolderProperties', handleShowFolderProperties);
  // 监听显示文件属性的事件
  eventBus.on('showFileProperties', handleShowFileProperties);
});

// 组件卸载时取消监听
onUnmounted(() => {
  eventBus.off('showFolderProperties', handleShowFolderProperties);
  eventBus.off('showFileProperties', handleShowFileProperties);
});

// 处理显示文件夹属性的事件
const handleShowFolderProperties = async (folder) => {
  try {
    // 切换到文件属性标签页
    activeTab.value = 'fileProperties';
    
    // 设置当前选中的文件夹
    selectedFolder.value = folder;
    
    // 加载文件夹详细信息
    if (folder && folder.id) {
      await loadFolderInfo(folder.id);
    }
  } catch (error) {
    console.error('显示文件夹属性失败:', error);
  }
};

// 处理显示文件属性的事件
const handleShowFileProperties = async (file) => {
  try {
    // 切换到文件属性标签页
    activeTab.value = 'fileProperties';
    
    // 清空选中的文件夹，确保显示文件属性
    selectedFolder.value = null;
    
    // 清除之前的文件选择
    selectedFiles.value.clear();
    
    // 添加当前文件到选择中
    if (file && file.id) {
      selectedFiles.value.add(file.id);
    }
  } catch (error) {
    console.error('显示文件属性失败:', error);
  }
};
</script>

<style scoped>
.panel-section {
  margin-bottom: 1rem;
}

.file-item {
  position: relative;
}

.file-item.selected {
  background-color: #e3f2fd !important;
  border-color: #90caf9 !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.file-item.dark:selected {
  background-color: #1a237e !important;
  border-color: #3949ab !important;
}

/* 滚动条样式 - 使用全局scrollbar-thin样式，与文件面板保持一致 */
</style>