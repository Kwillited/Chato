<template>
  <!-- 文件夹列表侧边栏组件 -->
  <Sidebar class="folder-list-sidebar left">
    <template #content>
      <div id="ragPanel" class="h-full flex flex-col">
        <!-- 主内容区域 -->
        <div class="overflow-y-auto h-full scrollbar-thin">
          <!-- 文件夹样式的根目录 -->
          <div class="folder-container p-2">
            <!-- 工具栏组件 -->
            <div class="flex items-center justify-between mb-4 p-2">
              <h3 class="text-lg font-bold text-gray-800 dark:text-white">文件夹</h3>
              <button 
                class="text-sm px-2 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors"
                @click="handleCreateKnowledgeBase"
              >
                + 新建
              </button>
            </div>
            
            <!-- 文件夹列表 - 根目录视图 -->
            <div v-if="!currentFolder">
              <!-- 文件夹列表 -->
              <div v-if="folders.length > 0" class="folder-tree">
                <div v-for="folder in folders" :key="folder.id" class="folder-item mb-2">
                  <div 
                    class="flex items-center justify-between gap-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-dark-700 cursor-pointer transition-colors"
                  >
                    <div 
                      class="flex items-center gap-2 cursor-pointer"
                      @click="handleFolderDoubleClick(folder)"
                    >
                      <span class="text-gray-600 dark:text-gray-400">
                        📁
                      </span>
                      <span class="text-gray-700 dark:text-gray-300">{{ folder.name }}</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">({{ folder.itemCount || 0 }})</span>
                    </div>
                    <button 
                      class="text-xs text-red-500 hover:text-red-600 p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                      @click.stop="handleDeleteFolder(folder)"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- 空状态提示 -->
              <div v-else-if="!loadingFolders" class="text-center text-gray-500 dark:text-gray-400 py-8">
                暂无文件夹
              </div>
              
              <!-- 加载状态 -->
              <div v-if="loadingFolders" class="text-center text-gray-500 dark:text-gray-400 py-8">
                加载文件夹中...
              </div>
            </div>
            
            <!-- 文件列表 - 二级菜单视图 -->
            <div v-else class="ml-4">
              <div class="flex items-center gap-2 mb-4 p-2">
                <button 
                  class="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                  @click="handleBackToParent"
                >
                  ← 返回
                </button>
                <span class="text-gray-700 dark:text-gray-300 font-medium">{{ currentFolder.name }}</span>
              </div>
              
              <!-- 文件列表 -->
              <div v-if="currentFiles.length > 0" class="file-list space-y-1">
                <div 
                  v-for="file in currentFiles" 
                  :key="file.id"
                  class="flex items-center gap-2 p-1.5 rounded hover:bg-gray-50 dark:hover:bg-dark-800 cursor-pointer transition-colors text-sm"
                >
                  <span class="text-gray-500 dark:text-gray-400">📄</span>
                  <span class="text-gray-600 dark:text-gray-400">{{ file.name }}</span>
                </div>
              </div>
              
              <!-- 文件列表空状态 -->
              <div v-else-if="!loadingFiles" class="text-center text-gray-500 dark:text-gray-400 py-4">
                文件夹为空
              </div>
              
              <!-- 文件列表加载状态 -->
              <div v-if="loadingFiles" class="text-center text-gray-500 dark:text-gray-400 py-4">
                加载文件中...
              </div>
            </div>
          </div>
        </div>

        <!-- 确认删除文件夹模态框 -->
        <ConfirmationModal
          :visible="showDeleteFolderModal"
          title="确认删除"
          :message="`确定要删除文件夹 '${deleteFolderData?.name}' 吗？这将删除该文件夹下的所有内容！`"
          confirmText="确认删除"
          @confirm="handleDeleteFolderConfirm"
          @close="showDeleteFolderModal = false"
        />
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { useVectorStore } from '../../app/store/vectorStore.js';
import { useFileStore } from '../../app/store/fileStore.js';
import { showNotification } from '../../shared/utils/notificationUtils.js';
import ConfirmationModal from '../../shared/ui/ConfirmationModal.vue';
import Sidebar from '../../shared/ui/layout/Sidebar.vue';

const ragStore = useVectorStore();
const fileStore = useFileStore();

// 状态管理
// 文件夹列表
const folders = ref([]);
// 当前选中的文件夹
const currentFolder = ref(null);
// 当前文件夹中的文件列表
const currentFiles = ref([]);
// 加载状态
const loadingFolders = ref(false);
const loadingFiles = ref(false);
// 确认删除文件夹模态框显示状态
const showDeleteFolderModal = ref(false);
// 当前要删除的文件夹数据
const deleteFolderData = ref(null);

// 组件挂载时加载数据
onMounted(() => {
  loadFolders();
  loadFiles();
});

// 组件卸载时移除事件监听器
onUnmounted(() => {
  // 当侧边栏组件卸载时，清除localStorage中的选中状态
  localStorage.removeItem('ragSelectedFolder');
});

// 加载文件列表
const loadFiles = async () => {
  loadingFiles.value = true;
  try {
    await fileStore.loadFiles();
  } catch (error) {
    console.error('加载文件列表失败:', error);
    showNotification(`加载文件列表失败: ${error.message || String(error)}`, 'error');
  } finally {
    loadingFiles.value = false;
  }
};

// 加载文件夹列表
const loadFolders = async () => {
  loadingFolders.value = true;
  try {
    // 通过fileStore加载文件夹列表
    await fileStore.loadFolders();
    folders.value = fileStore.folders || [];
  } catch (error) {
    console.error('加载文件夹失败:', error);
    showNotification(`加载文件夹失败: ${error.message || String(error)}`, 'error');
  } finally {
    loadingFolders.value = false;
  }
};

// 处理返回上一级
const handleBackToParent = () => {
  currentFolder.value = null;
  currentFiles.value = [];
  // 返回上一级时清除localStorage中的选中状态
  localStorage.removeItem('ragSelectedFolder');
};

// 处理新建知识库
const handleCreateKnowledgeBase = () => {
  // 这里可以显示创建知识库的模态框
  showNotification('新建文件夹功能待实现', 'info');
};

// 加载指定文件夹中的文件
const loadFilesInFolder = async (folder) => {
  loadingFiles.value = true;
  try {
    // 通过fileStore加载文件夹中的文件
    const result = await fileStore.loadFilesInFolder(folder);
    currentFiles.value = result || [];
  } catch (error) {
    console.error('加载文件失败:', error);
    showNotification(`加载文件失败: ${error.message || String(error)}`, 'error');
  } finally {
    loadingFiles.value = false;
  }
};

// 处理文件夹双击事件
const handleFolderDoubleClick = async (folder) => {
  currentFolder.value = folder;
  // 设置当前文件夹为选中的文件夹，用于RAG检索范围
  ragStore.setCurrentSelectedFolder(folder);
  // 保存选中的文件夹到localStorage
  localStorage.setItem('ragSelectedFolder', JSON.stringify(folder));
  await loadFilesInFolder(folder);
};

// 处理删除文件夹 - 显示确认模态框
const handleDeleteFolder = (folder) => {
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
    // 这里应该调用fileStore的删除文件夹方法
    // await fileStore.deleteFolder(folder.id);
    
    // 模拟删除成功
    showNotification(`已成功删除文件夹: ${folder.name}`, 'success');
    
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
    console.error('删除文件夹失败:', error);
    showNotification(`删除文件夹失败: ${error.message || String(error)}`, 'error');
  }
};
</script>

<style scoped>
.folder-container {
  position: relative;
}

.folder-tree {
  overflow-y: auto;
}

.folder-item {
  /* 文件夹项样式 */
}

/* 滚动条样式 - 与其他组件保持一致 */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 深色模式滚动条样式 */
.dark .scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  transition: background-color 0.3s ease-in-out;
}

.dark .scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>