<template>
  <!-- 文件管理主内容区域 -->
  <div id="fileManagerMainContent" class="flex-1 flex flex-col overflow-hidden bg-transparent dark:bg-transparent">
    <!-- 顶部导航 -->
    <div class="panel-header p-3 flex flex-wrap items-center justify-between gap-4 transition-all duration-300">
      <!-- 左侧区域：搜索框 -->
      <div class="flex-1 min-w-0">
        <!-- 搜索框 -->
        <SearchBar v-model="searchQuery" placeholder="搜索文件..." @input="handleSearch" />
      </div>
      
      <!-- 中间标题 -->
      <div class="hidden md:flex items-center">
        <h2 class="text-lg font-bold text-dark dark:text-white">文件管理</h2>
        <span class="text-sm text-gray-500 ml-2">({{filteredFiles.length}}个文件)</span>
      </div>
      
      <!-- 右侧按钮区域 -->
      <div class="flex items-center space-x-4">
        <!-- 保留滑动控件，供其他功能使用 -->
        <div class="toggle-wrapper transition-all duration-300"
          :class="{ 'is-active': isSliderActive }"
          @click="toggleSlider"
          :aria-label="`切换滑动控件状态`"
          style="width: 48px; height: 24px;">
          <div class="toggle-slider" :class="{ 'is-active': isSliderActive }" style="width: 20px; height: 20px;"></div>
          <span class="toggle-label grid-label" style="width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
            <i class="fa-solid fa-project-diagram" style="font-size: 12px;"></i>
          </span>
          <span class="toggle-label list-label" style="width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
            <i class="fa-solid fa-folder-open" style="font-size: 12px;"></i>
          </span>
        </div>
        
        <!-- 刷新按钮 -->
        <Button 
          shape="full"
          size="md"
          icon="fa-arrows-rotate" 
          tooltip="刷新" 
          @click="refreshFiles"
        />
        
        <!-- 文件夹信息按钮 -->
        <Button 
          shape="full"
          size="md"
          icon="fa-info-circle" 
          tooltip="文件夹信息" 
          @click="handleFileProperties"
        />
      </div>
    </div>
    
    <!-- 移动端标题 -->
    <div class="md:hidden p-3 text-center">
      <h2 class="text-lg font-bold text-dark dark:text-white">文件管理</h2>
      <span class="text-sm text-gray-500">({{filteredFiles.length}}个文件)</span>
    </div>
    
    <!-- 文件列表/网格容器 -->
    <div class="flex-1 overflow-y-auto p-4">
      
      <!-- 文件列表视图 -->
      <div v-if="isSliderActive" class="w-full h-full">
        <!-- 网格视图 -->
        <div v-if="settingsStore.systemSettings.viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div v-for="file in filteredFiles" :key="file.id || file.path" 
               class="bg-transparent dark:bg-transparent rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow p-3 cursor-pointer flex flex-col items-center justify-center h-40 relative group">
            <!-- 文件图标 -->
            <div class="text-primary text-4xl mb-2">
              <i v-if="file.type === 'pdf'" class="fa-solid fa-file-pdf"></i>
              <i v-else-if="file.type === 'docx' || file.type === 'doc'" class="fa-solid fa-file-word"></i>
              <i v-else-if="file.type === 'xlsx' || file.type === 'xls'" class="fa-solid fa-file-excel"></i>
              <i v-else-if="file.type === 'pptx' || file.type === 'ppt'" class="fa-solid fa-file-powerpoint"></i>
              <i v-else-if="file.type === 'txt'" class="fa-solid fa-file-lines"></i>
              <i v-else-if="file.type === 'md'" class="fa-solid fa-file-markdown"></i>
              <i v-else class="fa-solid fa-file"></i>
            </div>
            <!-- 文件名 -->
            <div class="text-sm font-medium text-center truncate w-full" :title="file.name">{{ file.name }}</div>
            <!-- 文件大小 -->
            <div class="text-xs text-gray-500 mt-1">{{ formatFileSize(file.size) }}</div>
            <!-- 底部操作按钮 -->
            <div class="flex space-x-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button 
                shape="full"
                size="sm"
                icon="fa-info-circle" 
                tooltip="属性" 
                @click.stop="handleFileProperties(file)"
                class="text-gray-500 hover:text-blue-500 w-6 h-6 p-1"
              />
              <Button 
                shape="full"
                size="sm"
                icon="fa-eye" 
                tooltip="预览" 
                @click.stop="handlePreviewFile(file)"
                class="text-gray-500 hover:text-green-500 w-6 h-6 p-1"
              />
              <Button 
                shape="full"
                size="sm"
                icon="fa-trash" 
                tooltip="删除" 
                @click.stop="handleDeleteFile(file.id)"
                class="text-gray-500 hover:text-red-500 w-6 h-6 p-1"
              />
            </div>
          </div>
        </div>
        
        <!-- 列表视图 -->
        <div v-else-if="settingsStore.systemSettings.viewMode === 'list'" class="bg-transparent dark:bg-transparent rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <!-- 列表标题行 -->
          <div class="grid grid-cols-12 gap-4 px-4 py-2 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 font-medium text-sm text-gray-600 dark:text-gray-300 rounded-t-lg">
            <div class="col-span-6">名称</div>
            <div class="col-span-2">类型</div>
            <div class="col-span-2">大小</div>
            <div class="col-span-2 text-right">操作</div>
          </div>
          <!-- 列表内容 -->
          <div v-for="(file, index) in filteredFiles" :key="file.id || file.path" 
               class="grid grid-cols-12 gap-4 px-4 py-3 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors" 
               :class="index === filteredFiles.length - 1 ? 'border-b-0 rounded-b-lg' : ''">
            <div class="col-span-6 flex items-center space-x-2">
              <div class="text-primary">
                <i v-if="file.type === 'pdf'" class="fa-solid fa-file-pdf"></i>
                <i v-else-if="file.type === 'docx' || file.type === 'doc'" class="fa-solid fa-file-word"></i>
                <i v-else-if="file.type === 'xlsx' || file.type === 'xls'" class="fa-solid fa-file-excel"></i>
                <i v-else-if="file.type === 'pptx' || file.type === 'ppt'" class="fa-solid fa-file-powerpoint"></i>
                <i v-else-if="file.type === 'txt'" class="fa-solid fa-file-lines"></i>
                <i v-else-if="file.type === 'md'" class="fa-solid fa-file-markdown"></i>
                <i v-else class="fa-solid fa-file"></i>
              </div>
              <span class="truncate" :title="file.name">{{ file.name }}</span>
            </div>
            <div class="col-span-2 flex items-center">{{ file.type || 'unknown' }}</div>
            <div class="col-span-2 flex items-center">{{ formatFileSize(file.size) }}</div>
            <div class="col-span-2 flex items-center justify-end space-x-2">
                <Button 
                  shape="full"
                  size="sm"
                  icon="fa-eye" 
                  tooltip="预览"
                  class="text-gray-500 hover:text-primary w-6 h-6 p-1"
                />
                <Button 
                  shape="full"
                  size="sm"
                  icon="fa-trash" 
                  tooltip="删除" 
                  @click="handleDeleteFile(file.id)"
                  class="text-gray-500 hover:text-red-500 w-6 h-6 p-1"
                />
              </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-if="filteredFiles.length === 0 && !isLoading" class="flex flex-col items-center justify-center h-64 text-gray-500">
          <i class="fa-solid fa-folder-open text-4xl mb-4"></i>
          <p v-if="currentFolder">当前文件夹中暂无文件</p>
          <p v-else-if="!selectedFolder">请选择左侧文件夹查看文件</p>
          <p v-else>暂无文件</p>
          <p v-if="!currentFolder && !selectedFolder" class="text-sm mt-2">选择文件夹后将显示其中的文件</p>
          <p v-else-if="!currentFolder && selectedFolder" class="text-sm mt-2">点击上传按钮添加文件</p>
        </div>
        
        <!-- 加载状态：使用骨架屏提升体验 -->
        <SkeletonLoader v-if="isLoading" type="grid" :count="4" />

      </div>
      
      <!-- 知识图谱可视化视图 -->
      <div v-else class="w-full h-full relative">
        <KnowledgeGraphVisualization 
          :nodes="knowledgeGraphNodes"
          :links="knowledgeGraphLinks"
          :visible="true"
          @node-click="handleNodeClick"
          @node-hover="handleNodeHover"
          @view-changed="handleViewChanged"
        />
      </div>
    </div>
  </div>
  
  <!-- 确认删除模态框 -->
  <ConfirmationModal
    :visible="showDeleteModal"
    title="确认删除"
    message="确定要删除这个文件吗？"
    confirmText="确认删除"
    cancelText="取消"
    confirmType="danger"
    @confirm="handleDeleteConfirm"
    @cancel="showDeleteModal = false"
  />
  

</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useSettingsStore } from '../store/settingsStore.js';
import { useUiStore } from '../store/uiStore.js';
import { useVectorStore } from '../store/vectorStore.js';
import { useFileStore } from '../store/fileStore.js';
import { useChatStore } from '../store/chatStore.js';
import { eventBus } from '../services/eventBus.js';
import { generateId } from '../utils/data.js';
import { formatFileSize } from '../utils/file.js';
import { Button } from '../components/library/index.js';
import { defineAsyncComponent } from 'vue';

// 动态导入知识图谱组件
const KnowledgeGraphVisualization = defineAsyncComponent({
  loader: () => import('../components/library').then(module => module.KnowledgeGraphVisualization),
  loadingComponent: {
    template: '<div class="flex justify-center items-center h-full">加载知识图谱中...</div>'
  },
  errorComponent: {
    template: '<div class="flex justify-center items-center h-full">加载失败，请重试</div>'
  },
  timeout: 5000
});
import ConfirmationModal from '../components/common/ConfirmationModal.vue';
import SkeletonLoader from '../components/common/SkeletonLoader.vue';
import SearchBar from '../components/common/SearchBar.vue';
import { useNotification } from '../composables/useNotification.js';

// 初始化stores
const settingsStore = useSettingsStore();
const uiStore = useUiStore();

// 使用通知组合式函数
const { showError, showSuccess } = useNotification();
const vectorStore = useVectorStore();
const fileStore = useFileStore();
const chatStore = useChatStore();

// 处理新对话点击事件
const handleNewChat = () => {
  // 取消当前会话的激活状态
  chatStore.currentChatId = null;
  
  // 清除所有对话的未读标记
  chatStore.chats = chatStore.chats.map(chat => ({
    ...chat,
    hasUnreadMessage: false
  }));
  
  // 切换到发送消息视图
  uiStore.setActiveContent('home');
};

// 本地状态
const searchQuery = ref('');
const isLoading = ref(false);
const selectedFolder = ref(null); // 当前选中的文件夹
const currentFolder = ref('');
const folders = ref([]);
// 使用本地状态控制视图切换，默认true（文件列表视图）
const isSliderActive = ref(true);
const showDeleteModal = ref(false); // 确认删除模态框显示状态
const fileIdToDelete = ref(null); // 要删除的文件ID

// 初始化时加载文件夹
const loadFolders = async () => {
  try {
    // 使用fileStore加载文件夹列表
    await fileStore.loadFolders();
    folders.value = fileStore.folders || [];
  } catch (error) {
    console.error('加载文件夹失败:', error);
  }
};

// 获取文件列表
const files = computed(() => {
  // 从store获取文件列表
  if (fileStore.files && fileStore.files.length > 0) {
    return fileStore.files.map(file => ({
      ...file,
      type: getFileExtension(file.name),
      path: file.path || '',
    }));
  }
  
  // 如果store中没有文件，返回空数组
  return [];
});

// 过滤文件（只考虑搜索查询）
const filteredFiles = computed(() => {
  let result = files.value;
  
  // 根据搜索查询过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(file => 
      file.name.toLowerCase().includes(query) || 
      (file.type && file.type.toLowerCase().includes(query))
    );
  }
  
  return result;
});

// 切换滑动控件状态（控制文件列表和知识图谱视图切换）
const toggleSlider = () => {
  // 直接修改本地状态
  isSliderActive.value = !isSliderActive.value;
  console.log('滑动控件状态切换:', isSliderActive.value);
};

// 处理搜索
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
};

// 将文件转换为知识图谱节点
const knowledgeGraphNodes = computed(() => {
  const nodes = [];
  
  // 为每个文件创建一个节点
  filteredFiles.value.forEach((file, index) => {
    const node = {
      id: file.id || file.path || index,
      name: file.name,
      type: file.type,
      radius: 20,
      color: getFileColor(file.type)
    };
    nodes.push(node);
  });
  
  // 增加更多随机测试节点
  const testNodeCount = 15; // 增加15个测试节点
  const fileTypes = ['pdf', 'docx', 'xlsx', 'pptx', 'txt', 'md'];
  
  for (let i = 0; i < testNodeCount; i++) {
    const randomType = fileTypes[Math.floor(Math.random() * fileTypes.length)];
    const node = {
      id: `test-node-${i}`,
      name: `Test-${i}.${randomType}`,
      type: randomType,
      radius: 20,
      color: getFileColor(randomType)
    };
    nodes.push(node);
  }
  
  return nodes;
});

// 生成知识图谱连线
const knowledgeGraphLinks = computed(() => {
  const links = [];
  const nodeCount = knowledgeGraphNodes.value.length;
  
  // 生成随机连线
  for (let i = 0; i < nodeCount; i++) {
    for (let j = i + 1; j < nodeCount; j++) {
      if (Math.random() < 0.15) { // 增加连线概率
        links.push({
          source: i,
          target: j
        });
      }
    }
  }
  
  return links;
});

// 获取文件类型对应的颜色
const getFileColor = (type) => {
  const colorMap = {
    'pdf': '#FF5733',
    'docx': '#3366FF',
    'doc': '#3366FF',
    'xlsx': '#33FF57',
    'xls': '#33FF57',
    'pptx': '#FF33F5',
    'ppt': '#FF33F5',
    'txt': '#FFC300',
    'md': '#8E44AD'
  };
  return colorMap[type] || '#95A5A6';
};

// 处理知识图谱节点点击事件
const handleNodeClick = (node) => {
  console.log('知识图谱节点被点击:', node);
};

// 处理知识图谱节点悬停事件
const handleNodeHover = (node) => {
  console.log('知识图谱节点悬停:', node);
};

// 处理知识图谱视图变化事件
const handleViewChanged = (viewInfo) => {
  console.log('知识图谱视图变化:', viewInfo);
};

// 刷新文件列表
const refreshFiles = async () => {
  isLoading.value = true;
  try {
    // 实际项目中应该从后端或store重新加载文件
    await fileStore.loadFiles();
    // 模拟加载延迟
    await new Promise(resolve => setTimeout(resolve, 500));
  } catch (error) {
    console.error('刷新文件列表失败:', error);
  } finally {
    // 使用nextTick确保数据更新完成后再隐藏加载状态
    await nextTick();
    isLoading.value = false;
  }
};

// 处理上传文件
const handleUploadClick = async () => {
  try {
    // 创建原生文件选择器
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    
    // 使用Promise处理文件选择事件
    const filesPromise = new Promise((resolve) => {
      input.onchange = (e) => {
        resolve(Array.from(e.target.files));
      };
    });
    
    // 触发文件选择器
    input.click();
    
    // 等待用户选择文件
    const files = await filesPromise;
    
    if (files && files.length > 0) {
      
      // 调用fileStore的批量上传方法
      await fileStore.batchUploadFiles(files);
      
      // 上传完成后刷新文件列表
      await refreshFiles();
    }
  } catch (error) {
    console.error('上传文件失败:', error);
    showError(`上传文件失败: ${error.message || String(error)}`);
  }
};

// 获取文件扩展名
const getFileExtension = (filename) => {
  if (!filename) return '';
  const parts = filename.split('.');
  if (parts.length === 1) return '';
  return parts.pop().toLowerCase();
};

// 跟踪最近的双击时间
let lastDoubleClickTime = 0;

// 处理文件夹选中事件
const handleFolderSelected = (folder) => {
  selectedFolder.value = folder;
  
  // 检查是否在短时间内发生了双击（300ms内）
  const now = Date.now();
  if (now - lastDoubleClickTime > 300) {
    // 如果不是双击，加载文件夹内容
    handleFolderClick(folder);
  }
};

// 删除文件
const handleDeleteFile = (fileId) => {
  // 保存要删除的文件ID
  fileIdToDelete.value = fileId;
  // 显示确认删除模态框
  showDeleteModal.value = true;
};

// 处理确认删除
const handleDeleteConfirm = async () => {
  if (!fileIdToDelete.value) return;
  
  try {
    // 获取当前文件夹ID（如果有）
    const folderId = selectedFolder.value?.id || '';
    // 传递文件夹ID给deleteFile方法
    await fileStore.deleteDocument(fileToDelete.name, folderId);
    // 删除后刷新文件列表
    // 根据当前是否有选中的文件夹决定如何刷新
    if (currentFolder.value && selectedFolder.value) {
      // 如果在某个文件夹中删除文件，重新加载该文件夹的内容
      await handleFolderClick(selectedFolder.value);
    } else {
      // 否则刷新根目录的文件列表
      await refreshFiles();
    }
  } catch (error) {
    console.error('删除文件失败:', error);
    showError(`删除文件失败: ${error.message || String(error)}`);
  } finally {
    // 关闭模态框
    showDeleteModal.value = false;
    // 重置要删除的文件ID
    fileIdToDelete.value = null;
  }
};

// 处理文件或文件夹属性
const handleFileProperties = async (item) => {
  try {
    // 显示右侧面板
    uiStore.setRightPanelVisible(true);
    
    if (item.type) {
      // 如果是文件，触发事件通知右侧面板显示文件属性
      eventBus.emit('showFileProperties', item);
    } else {
      // 如果是文件夹，触发事件通知右侧面板显示文件夹属性
      eventBus.emit('showFolderProperties', item);
    }
  } catch (error) {
    console.error('处理属性失败:', error);
    showError(`处理属性失败: ${error.message || String(error)}`);
  }
};

// 处理文件预览
const handlePreviewFile = async (file) => {
  try {
    console.log('预览文件:', file);
    // 这里可以添加文件预览的逻辑
    showSuccess(`正在预览文件: ${file.name}`);
  } catch (error) {
    console.error('预览文件失败:', error);
    showError(`预览文件失败: ${error.message || String(error)}`);
  }
};

// 处理文件夹点击
const handleFolderClick = async (folder) => {
  console.log(`尝试加载文件夹: ${JSON.stringify(folder)}`);
  currentFolder.value = folder.name;
  isLoading.value = true;
  try {
    // 使用fileStore的方法保存状态
    fileStore.currentFolder = folder;
    fileStore.saveSelectedFolder(folder);
    
    // 使用fileStore加载指定文件夹的文件
    const folderFiles = await fileStore.loadFilesInFolder(folder);
    // 更新store中的文件列表
    if (folderFiles && Array.isArray(folderFiles)) {
      const formattedFiles = folderFiles.map((file) => ({
        id: generateId('file'),
        name: file.name,
        path: file.path || '',
        size: file.size || 0,
        type: file.type || (file.name ? file.name.split('.').pop()?.toLowerCase() : 'unknown'),
        uploadedAt: file.uploadedAt || Date.now()
      }));
      // 更新fileStore.files，确保文件列表正确显示
      fileStore.files = formattedFiles;
    }
    
    // 打印文件列表用于调试
    console.log(`加载的文件列表: ${fileStore.files?.length || 0} 个文件`);
  } catch (error) {
    console.error('读取文件夹内容失败:', error);
    // 发生错误时清空文件列表
    fileStore.files = [];
  } finally {
    // 使用nextTick确保数据更新完成后再隐藏加载状态
    await nextTick();
    isLoading.value = false;
  }
};

// 处理视图切换事件
const handleViewSwitch = (event) => {
  if (event.detail === 'grid') {
    settingsStore.systemSettings.viewMode = 'grid';
  }
};

// 处理文件上传完成事件
const handleFilesUploaded = () => {
  // 如果有选中的文件夹，重新加载该文件夹的内容
  if (selectedFolder.value) {
    handleFolderClick(selectedFolder.value);
  } else {
    refreshFiles();
  }
  loadFolders();
};

// 组件挂载时加载文件并监听事件
onMounted(() => {
  console.log('FileMangerContent组件挂载');
  
  // 初始加载文件夹列表
  loadFolders().then(() => {
    // 使用fileStore加载持久化状态
    fileStore.loadPersistedState();
    if (fileStore.currentFolder) {
      const folder = fileStore.currentFolder;
      selectedFolder.value = folder;
      currentFolder.value = folder.name;
      // 加载选中文件夹的内容
      handleFolderClick(folder);
    }
  });
  
  // 监听文件夹选中事件
  eventBus.on('folderSelected', handleFolderSelected);
  
  // 监听FilePanel中的文件上传完成事件
  eventBus.on('filesUploaded', handleFilesUploaded);
  
  // 监听视图切换事件
  window.addEventListener('switchToThumbnailView', handleViewSwitch);
  
  // 监听可能的全局内容变化事件
  window.addEventListener('contentChanged', handleContentChanged);
});

// 组件卸载时取消监听
onUnmounted(() => {
  eventBus.off('folderSelected', handleFolderSelected);
  eventBus.off('filesUploaded', handleFilesUploaded);
  
  // 移除视图切换事件监听
  window.removeEventListener('switchToThumbnailView', handleViewSwitch);
  
  // 清除contentChanged事件监听
  window.removeEventListener('contentChanged', handleContentChanged);
});

// 处理内容变化事件的单独函数
const handleContentChanged = async (event) => {
  // 如果切换到了文件管理视图，尝试恢复之前保存的选中状态
  if (event.detail && event.detail.contentType === 'fileManager') {
    // 确保文件夹列表已加载
    if (folders.value.length === 0) {
      await loadFolders();
    }
    
    // 直接使用fileStore中的currentFolder
    if (fileStore.currentFolder) {
      const folder = fileStore.currentFolder;
      selectedFolder.value = folder;
      currentFolder.value = folder.name;
      // 自动加载选中文件夹的内容
      handleFolderClick(folder);
    } else {
      // 尝试从持久化存储加载
      fileStore.loadPersistedState();
      if (fileStore.currentFolder) {
        const folder = fileStore.currentFolder;
        selectedFolder.value = folder;
        currentFolder.value = folder.name;
        handleFolderClick(folder);
      } else {
        // 重置状态
        selectedFolder.value = null;
        currentFolder.value = '';
        fileStore.files = [];
      }
    }
  }
}
</script>

<style scoped>
/* 视图切换滑块样式 */
.toggle-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  background-color: #f0f2f5;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  user-select: none;
}

.toggle-wrapper:hover {
  background-color: #e4e6eb;
}

.toggle-wrapper.is-active {
  background-color: #f0f2f5;
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  background-color: #fff;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.toggle-slider.is-active {
  transform: translateX(24px);
}

.toggle-label {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #65676b;
  transition: color 0.3s ease;
}

.toggle-wrapper.is-active .list-label {
  color: #fff;
}

.toggle-wrapper:not(.is-active) .grid-label {
  color: #fff;
}

.toggle-wrapper.is-active .grid-label {
  color: #65676b;
}

.toggle-wrapper:not(.is-active) .list-label {
  color: #65676b;
}

/* 动画效果增强 */
.toggle-wrapper:active .toggle-slider {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

/* 适配暗色模式 */
@media (prefers-color-scheme: dark) {
  .toggle-wrapper {
    background-color: #3a3b3c;
  }
  
  .toggle-wrapper:hover {
    background-color: #4a4b4c;
  }
  
  .toggle-wrapper.is-active {
    background-color: #3a3b3c;
  }
  
  .toggle-label {
    color: #b0b3b8;
  }
  
  .toggle-wrapper.is-active .list-label,
  .toggle-wrapper:not(.is-active) .grid-label {
    color: #fff;
  }
  
  .toggle-wrapper.is-active .grid-label,
  .toggle-wrapper:not(.is-active) .list-label {
    color: #b0b3b8;
  }
}
</style>