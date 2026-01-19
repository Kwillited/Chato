<template>
  <!-- RAG文件管理主内容区域 -->
  <div id="ragManagementMainContent" class="flex-1 flex flex-col overflow-hidden bg-transparent dark:bg-transparent">
    <!-- 顶部导航 -->
    <div class="panel-header p-3 flex flex-wrap items-center justify-between gap-4 transition-all duration-300">
      <!-- 左侧区域：按钮组 + 搜索框 -->
      <div class="flex items-center space-x-2 flex-1 min-w-0">
        <!-- 左侧按钮组 -->
        <div class="flex space-x-2">
          <ActionButton 
            icon="fa-bars" 
            title="隐藏左侧面板" 
            @click="handleSideMenuToggle"
          />
          <!-- 新增会话按钮 -->
          <ActionButton 
            id="newChat"
            icon="fa-comment-dots" 
            title="新对话"
            @click="handleNewChat"
          />
        </div>
        
        <!-- 搜索框 -->
        <div class="relative flex-1 ml-4 min-w-[200px]">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索文件..."
            class="w-full pl-10 pr-4 py-1 border border-gray-300 rounded-[15px] focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            @input="handleSearch"
          >
          <i class="fa-solid fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
        </div>
      </div>
      
      <!-- 中间标题 -->
      <div class="hidden md:flex items-center">
        <h2 class="text-lg font-bold text-dark dark:text-white">RAG文件管理</h2>
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
        
        <!-- 上传文件按钮 -->
        <ActionButton 
          icon="fa-upload" 
          title="上传文件" 
          @click="handleUploadClick"
        />
        
        <!-- 刷新按钮 -->
        <ActionButton 
          icon="fa-arrows-rotate" 
          title="刷新" 
          @click="refreshFiles"
        />
      </div>
    </div>
    
    <!-- 移动端标题 -->
    <div class="md:hidden p-3 text-center">
      <h2 class="text-lg font-bold text-dark dark:text-white">RAG文件管理</h2>
      <span class="text-sm text-gray-500">({{filteredFiles.length}}个文件)</span>
    </div>
    
    <!-- 文件列表/网格容器 -->
    <div class="flex-1 overflow-y-auto p-4">
      
      <!-- 文件列表视图 (div) -->
      <div v-if="isSliderActive" class="w-full h-full">
        <!-- 网格视图 -->
        <div v-if="settingsStore.systemSettings.viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div v-for="file in filteredFiles" :key="file.id || file.path" 
               class="bg-transparent dark:bg-transparent rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow p-3 cursor-pointer flex flex-col items-center justify-center h-40 relative">
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
            <!-- 操作按钮 -->
            <div class="absolute top-2 right-2 opacity-0 hover:opacity-100 transition-opacity">
              <ActionButton 
                icon="fa-trash" 
                title="删除" 
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
                <ActionButton 
                  icon="fa-eye" 
                  title="预览"
                  class="text-gray-500 hover:text-primary w-6 h-6 p-1"
                />
                <ActionButton 
                  icon="fa-trash" 
                  title="删除" 
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
          <p v-else-if="!currentFolder && selectedFolder" class="text-sm mt-2">点击上传按钮添加RAG文件</p>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="flex flex-col items-center justify-center h-64 text-gray-500">
          <div class="w-10 h-10 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
          <p>加载中...</p>
        </div>
      </div>
      
      <!-- 知识图谱可视化视图 -->
      <div v-else class="w-full h-full relative">
        <KnowledgeGraphVisualization 
          :nodes="knowledgeGraphNodes"
          :links="knowledgeGraphLinks"
          :visible="!isSliderActive"
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
import { useRagStore } from '../store/ragStore.js';
import { fileStore } from '../store/fileStore.js';
import { useChatStore } from '../store/chatStore.js';
import { eventBus } from '../services/eventBus.js';
import { generateId, formatFileSize } from '../store/utils.js';
import ActionButton from '../components/common/ActionButton.vue';
import { KnowledgeGraphVisualization } from '../components/library';
import ConfirmationModal from '../components/common/ConfirmationModal.vue';
import { showNotification } from '../services/notificationUtils.js';

// 导入Tauri API用于文件操作
// 移除不再需要的Tauri导入

// 初始化stores
const settingsStore = useSettingsStore();
const ragStore = useRagStore();
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
  settingsStore.setActiveContent('sendMessage');
};

// 本地状态
const searchQuery = ref('');
const isLoading = ref(false);
const selectedFolder = ref(null); // 当前选中的文件夹
const currentFolder = ref('');
const folders = ref([]);
const isSliderActive = ref(false); // 滑动控件状态
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
  if (ragStore.files && ragStore.files.length > 0) {
    return ragStore.files.map(file => ({
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
    await ragStore.loadFiles();
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
      
      // 调用ragStore的批量上传方法
      await ragStore.batchUploadFiles(files);
      
      // 上传完成后刷新文件列表
      await refreshFiles();
    }
  } catch (error) {
    console.error('上传文件失败:', error);
    showNotification(`上传文件失败: ${error.message || String(error)}`, 'error');
  }
};

// 处理隐藏菜单
const handleSideMenuToggle = () => {
  // 只使用store提供的方法切换左侧导航栏的可见性
  // DOM操作逻辑移至App.vue中统一管理
  settingsStore.toggleLeftNav();
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
    await ragStore.deleteFile(fileIdToDelete.value, folderId);
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
    showNotification(`删除文件失败: ${error.message || String(error)}`, 'error');
  } finally {
    // 关闭模态框
    showDeleteModal.value = false;
    // 重置要删除的文件ID
    fileIdToDelete.value = null;
  }
};

// 处理文件夹点击
const handleFolderClick = async (folder) => {
  console.log(`尝试加载文件夹: ${JSON.stringify(folder)}`);
  currentFolder.value = folder.name;
  isLoading.value = true;
  try {
    // 保存选中的文件夹到本地存储
    localStorage.setItem('ragSelectedFolder', JSON.stringify(folder));
    
    // 使用fileStore加载指定文件夹的文件
    const folderFiles = await fileStore.loadFilesInFolder(folder);
    // 更新store中的文件列表
    if (folderFiles && Array.isArray(folderFiles)) {
      fileStore.files = folderFiles.map((file) => ({
        id: generateId('file'),
        name: file.name,
        path: file.path || '',
        size: file.size || 0,
        type: file.type || (file.name ? file.name.split('.').pop()?.toLowerCase() : 'unknown'),
        uploadedAt: file.uploadedAt || Date.now()
      }));
    }
    
    // 打印文件列表用于调试
    console.log(`加载的文件列表: ${ragStore.files?.length || 0} 个文件`);
  } catch (error) {
    console.error('读取文件夹内容失败:', error);
    // 发生错误时清空文件列表
    ragStore.files = [];
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

// 处理窗口大小变化




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
  console.log('RagManagementContent组件挂载');
  
  // 初始加载文件夹列表
  loadFolders().then(() => {
    // 尝试恢复之前保存的选中状态
    const storedSelectedFolder = localStorage.getItem('ragSelectedFolder');
    if (storedSelectedFolder) {
      try {
        const folder = JSON.parse(storedSelectedFolder);
        selectedFolder.value = folder;
        currentFolder.value = folder.name;
        // 加载选中文件夹的内容
        handleFolderClick(folder);
      } catch (error) {
        console.error('解析存储的选中文件夹失败:', error);
        // 解析失败时重置状态
        selectedFolder.value = null;
        currentFolder.value = '';
        ragStore.files = [];
      }
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
  // 如果切换到了RAG管理视图，尝试恢复之前保存的选中状态
  if (event.detail && event.detail.contentType === 'ragManagement') {
    // 确保文件夹列表已加载
    if (folders.value.length === 0) {
      await loadFolders();
    }
    
    // 尝试从localStorage中获取之前保存的选中文件夹
    const storedSelectedFolder = localStorage.getItem('ragSelectedFolder');
    if (storedSelectedFolder) {
      try {
        const folder = JSON.parse(storedSelectedFolder);
        selectedFolder.value = folder;
        currentFolder.value = folder.name;
        // 自动加载选中文件夹的内容
        handleFolderClick(folder);
      } catch (error) {
        console.error('解析存储的选中文件夹失败:', error);
        // 解析失败时重置状态
        selectedFolder.value = null;
        currentFolder.value = '';
        ragStore.files = [];
      }
    } else {
      // 如果没有存储的选中状态，重置当前组件的状态
      selectedFolder.value = null;
      currentFolder.value = '';
      ragStore.files = [];
    }
  }
}
</script>

<style scoped>
/* 可以添加组件特定的样式 */
.panel-header {
  /* 移除底部边框 */
}



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