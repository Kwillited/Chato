<template>
  <div id="ragPanel" class="h-full flex flex-col">
    <!-- 头部组件 -->
    <RagFilePanelHeader :currentFolder="currentFolder" />

    <!-- 主内容区域 -->
    <div class="overflow-y-auto flex-1 scrollbar-thin">
      <!-- 文件夹样式的根目录 -->
      <div class="folder-container p-2">
        <!-- 工具栏组件 -->
        <RagToolbar :loading="fileStore.loading" />
        
        <!-- 文件夹列表 - 根目录视图 -->
        <div v-if="!currentFolder">
          <RagFolderList v-if="folders.length > 0" :folders="folders" />
          
          <!-- 空状态提示 -->
          <StateDisplay v-else-if="!loadingFolders" type="empty" title="暂无知识库" message="点击右上角按钮创建您的第一个知识库" icon="fa-inbox" />
          
          <!-- 加载状态 -->
          <StateDisplay v-if="loadingFolders" type="loading" message="加载知识库中..." />
        </div>
        
        <!-- 文件列表 - 二级菜单视图 -->
        <RagFileList v-else
          :currentFolder="currentFolder"
          :currentFiles="currentFiles"
          :loadingFiles="loadingFiles"
        />
      </div>
    </div>

    <!-- 加载状态指示器 -->
    <div v-if="fileStore.loading" class="loading-overlay absolute inset-0 bg-white/80 flex items-center justify-center z-50">
      <Loading type="spin" size="medium" text="处理中..." />
    </div>
    
    <!-- 创建知识库模态弹窗 -->
    <RagCreateKnowledgeBaseModal 
      :visible="showCreateModal"
      @close="handleCloseModal"
      @created="handleKnowledgeBaseCreated"
    />
    
    <!-- 确认删除所有文件模态框 -->
    <ConfirmationModal
      :visible="showDeleteAllModal"
      title="确认删除所有内容"
      message="确定要删除所有文件和文件夹吗？<br><span class='text-red-500 font-medium'>此操作将同时清空向量数据库，且无法撤销！</span>"
      :html="true"
      confirmText="确认删除"
      :loading="isDeletingAll"
      loadingText="删除中..."
      @confirm="handleDeleteAllConfirm"
      @close="showDeleteAllModal = false"
    />
    
    <!-- 确认删除文件夹模态框 -->
    <ConfirmationModal
      :visible="showDeleteFolderModal"
      title="确认删除"
      :message="`确定要删除知识库文件夹 '${deleteFolderData?.name}' 吗？这将删除该文件夹下的所有内容！`"
      confirmText="确认删除"
      @confirm="handleDeleteFolderConfirm"
      @close="showDeleteFolderModal = false"
    />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { useVectorStore } from '../../store/vectorStore.js';
import { useFileStore } from '../../store/fileStore.js';
import { useFileManagement } from '../../composables/useFileManagement.js';
import { useNotifications } from '../../composables/useNotifications.js';
import eventBus from '../../services/eventBus.js';
import logger from '../../utils/logger.js';

// 导入子组件
import RagFilePanelHeader from '../file/RagFilePanelHeader.vue';
import RagToolbar from '../file/RagToolbar.vue';
import RagFolderList from '../file/RagFolderList.vue';
import RagFileList from '../file/RagFileList.vue';
import StateDisplay from '../common/StateDisplay.vue';
import { Loading, ConfirmationModal } from '../library/index.js';
import RagCreateKnowledgeBaseModal from '../file/RagCreateKnowledgeBaseModal.vue';

const ragStore = useVectorStore();
const fileStore = useFileStore();
const { 
  folders, 
  currentFolder, 
  currentFiles, 
  loadFiles, 
  loadFolders, 
  loadFilesInFolder, 
  batchUploadFiles, 
  deleteFolder, 
  deleteAllFiles 
} = useFileManagement();

// 使用通知管理组合函数
const { showSystemNotification } = useNotifications();

// 状态管理
// 模态弹窗显示状态
const showCreateModal = ref(false);
// 确认删除所有文件模态框显示状态
const showDeleteAllModal = ref(false);
// 确认删除文件夹模态框显示状态
const showDeleteFolderModal = ref(false);
// 当前要删除的文件夹数据
const deleteFolderData = ref(null);
// 文件夹ID到名称的映射
const folderIdMap = ref({});

// 组件挂载时加载数据
onMounted(() => {
  loadFiles();
  loadFolders();
  
  // 添加事件监听器
  window.addEventListener('backToParent', handleBackToParent);
  window.addEventListener('createKnowledgeBase', handleCreateKnowledgeBase);
  window.addEventListener('deleteAll', handleDeleteAll);
  window.addEventListener('folderDoubleClick', handleFolderDoubleClick);
  window.addEventListener('folderDrop', handleFolderDrop);
  window.addEventListener('deleteFolder', handleDeleteFolder);
  window.addEventListener('uploadToFolder', handleUploadToFolder);
  window.addEventListener('folderSelected', handleFolderSelected);
  window.addEventListener('searchKnowledgeBase', handleSearchKnowledgeBase);
  // 监听知识库创建成功事件（可能包含ID信息）
  window.addEventListener('knowledge-base-created', handleKnowledgeBaseCreated);
});

// 组件卸载时移除事件监听器
onUnmounted(() => {
  // 当侧边栏组件卸载时，清除localStorage中的选中状态
  localStorage.removeItem('ragSelectedFolder');
  
  window.removeEventListener('backToParent', handleBackToParent);
  window.removeEventListener('createKnowledgeBase', handleCreateKnowledgeBase);
  window.removeEventListener('deleteAll', handleDeleteAll);
  window.removeEventListener('folderDoubleClick', handleFolderDoubleClick);
  window.removeEventListener('folderDrop', handleFolderDrop);
  window.removeEventListener('deleteFolder', handleDeleteFolder);
  window.removeEventListener('uploadToFolder', handleUploadToFolder);
  window.removeEventListener('folderSelected', handleFolderSelected);
  window.removeEventListener('searchKnowledgeBase', handleSearchKnowledgeBase);
});

// loadFiles 和 loadFolders 方法已从 useFileManagement 组合函数中导入

// 处理返回上一级
const handleBackToParent = () => {
  currentFolder.value = null;
  currentFiles.value = [];
  // 返回上一级时清除localStorage中的选中状态
  localStorage.removeItem('ragSelectedFolder');
};

// 处理新建知识库
const handleCreateKnowledgeBase = () => {
  // 显示创建知识库模态弹窗
  showCreateModal.value = true;
};

// 处理知识库创建成功
const handleKnowledgeBaseCreated = async (event) => {
  const data = event ? event.detail : null;
  // 重新加载文件夹列表和文件列表
  await loadFolders();
  await loadFiles();
  
  // 如果有新创建的文件夹信息，自动选中它
  if (data) {
    setTimeout(() => {
      // 优先通过ID查找文件夹，然后再通过名称查找
      let newFolder = null;
      if (data.id) {
        newFolder = folders.value.find(f => f.id === data.id);
      }
      // 如果通过ID没找到，再通过名称查找
      if (!newFolder && data.name) {
        newFolder = folders.value.find(f => f.name === data.name);
      }
      
      if (newFolder) {
        // 触发文件夹双击事件来打开它
        const event = new CustomEvent('folderDoubleClick', { detail: newFolder });
        window.dispatchEvent(event);
      }
    }, 300);
  }
};

// 处理关闭模态弹窗
const handleCloseModal = () => {
  showCreateModal.value = false;
};

// 处理删除所有文件 - 显示确认模态框
const handleDeleteAll = () => {
  // 显示确认删除模态框
  showDeleteAllModal.value = true;
};

// 处理确认删除所有文件
const handleDeleteAllConfirm = async () => {
  isDeletingAll.value = true;
  
  try {
    await deleteAllFiles();
    // 删除成功后，重新加载文件和文件夹列表
    await loadFiles();
    await loadFolders();
    // 重置当前文件夹状态和文件列表，确保UI正确显示空状态
    currentFolder.value = null;
    currentFiles.value = [];
    // 关闭模态框
    showDeleteAllModal.value = false;
  } finally {
    isDeletingAll.value = false;
  }
};

// loadFilesInFolder 方法已从 useFileManagement 组合函数中导入

// 处理文件夹双击事件
const handleFolderDoubleClick = async (event) => {
  const folder = event.detail;
  currentFolder.value = folder;
  // 设置当前文件夹为选中的文件夹，用于RAG检索范围
  ragStore.setCurrentSelectedFolder(folder);
  // 保存选中的文件夹到localStorage，包含ID信息
  localStorage.setItem('ragSelectedFolder', JSON.stringify(folder));
  await loadFilesInFolder(folder);
};

// 处理文件夹拖拽放置
  const handleFolderDrop = async (event) => {
    const { folder, files } = event.detail;
    
    if (files && files.length > 0) {
      try {
        // 使用batchUploadFiles组合函数批量上传文件
        await batchUploadFiles(files, folder.id);
        
        // 重新加载文件和文件夹列表
        await loadFiles();
        await loadFolders();
      } catch (error) {
        logger.error('上传文件时发生错误:', error);
      }
    }
  };
  
  // 读取文件为ArrayBuffer
const _readFileAsArrayBuffer = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (event) => {
        resolve(event.target.result);
      };
      reader.onerror = (error) => {
        reject(error);
      };
      reader.readAsArrayBuffer(file);
    });
  };

// 处理上传文件到当前文件夹
const handleUploadToFolder = async (event) => {
  const folder = event.detail || currentFolder.value;
  if (!folder) {
    return;
  }
  
  try {
    // 创建文件选择器
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    
    // 监听文件选择事件
    input.onchange = async (e) => {
      const files = Array.from(e.target.files);
      
      if (files && files.length > 0) {
        try {
          // 使用batchUploadFiles组合函数批量上传文件
          await batchUploadFiles(files, folder.id);
          
          // 重新加载文件和文件夹列表
          await loadFiles();
          await loadFolders();
          
          // 触发文件上传完成事件
          eventBus.emit('filesUploaded');
        } catch (error) {
          logger.error('上传文件时发生错误:', error);
        }
      }
    };
    
    // 触发文件选择器
    input.click();
  } catch (error) {
    logger.error('上传文件时发生错误:', error);
  }
};

// _processFiles 函数已被 batchUploadFiles 组合函数取代

// 处理删除文件夹 - 显示确认模态框
const handleDeleteFolder = (event) => {
  const folder = event.detail;
  // 保存当前要删除的文件夹
  deleteFolderData.value = folder;
  // 显示确认删除模态框
  showDeleteFolderModal.value = true;
};

// 处理确认删除文件夹
const handleDeleteFolderConfirm = async () => {
  if (!deleteFolderData.value) return;
  
  const folder = deleteFolderData.value;
  
  try {
    // 使用deleteFolder组合函数删除文件夹
    await deleteFolder(folder);
    
    // 重新加载文件夹列表
    await loadFolders();
    
    // 如果删除的是当前文件夹，则返回上一级
    if (currentFolder.value === folder) {
      currentFolder.value = null;
      currentFiles.value = [];
    }
    
    // 关闭模态框
    showDeleteFolderModal.value = false;
  } catch (error) {
    // 错误处理已在组合函数中完成
    logger.error('删除文件夹失败:', error);
  }
};

// 处理文件夹选中状态变化
const handleFolderSelected = (event) => {
  const selectedFolder = event.detail;
  // 保存选中的文件夹到localStorage，包含ID信息
  localStorage.setItem('ragSelectedFolder', JSON.stringify(selectedFolder));
  // 更新ragStore的currentSelectedFolder状态
  ragStore.setCurrentSelectedFolder(selectedFolder);
  // 更新fileStore中的当前选中文件夹状态
  fileStore.currentFolder = selectedFolder;
};

// 通过文件夹ID获取文件夹名称（辅助函数）
const _getFolderNameById = (folderId) => {
  if (!folderId) return null;
  
  // 首先从映射中查找
  if (folderIdMap.value[folderId]) {
    return folderIdMap.value[folderId];
  }
  
  // 如果映射中没有，则遍历文件夹列表查找
  const folder = folders.value.find(f => f.id === folderId);
  return folder ? folder.name : null;
};

// 处理刷新文档
const _handleReloadDocuments = () => {
  loadFiles();
  loadFolders();
};

// 处理知识库搜索
const handleSearchKnowledgeBase = async (event) => {
  const searchTerm = event.detail;
  try {
    if (currentFolder.value) {
      // 在当前文件夹中搜索
      const _filteredFiles = currentFiles.value.filter(file => 
        file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (file.description && file.description.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      // 这里可以添加逻辑来显示搜索结果
    } else {
      // 在所有文件夹中搜索
      const _filteredFolders = folders.value.filter(folder => 
        folder.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      // 这里可以添加逻辑来显示搜索结果
    }
    // 实际项目中可能需要调用API进行后端搜索
    // const result = await ragStore.searchKnowledgeBase(searchTerm);
  } catch (error) {
    logger.error('搜索知识库失败:', error);
    showSystemNotification(`搜索知识库失败: ${error.message || String(error)}`, 'error');
  }
};
</script>

<style scoped>
/* 组件特定样式 */
.folder-container {
  position: relative;
}

.loading-overlay {
  animation: fadeIn 0.2s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.loading-spinner {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}
</style>
