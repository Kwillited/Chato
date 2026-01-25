<template>
  <div v-if="folders.length > 0" class="folders-list mt-3">
    <h3 class="text-sm font-medium text-gray-700 dark:text-white mb-2 px-2">知识库文件夹 ({{ folders.length }})</h3>
    <div v-for="folder in folders" :key="folder.id || folder.path"
      class="folder-item bg-gray-50 border border-gray-300 dark:bg-dark-bg-tertiary dark:border-gray-600 rounded-lg p-3 mb-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-dark-bg-secondary transition-all duration-300"
      @dragover.prevent="handleFolderDragOver($event, folder)"
      @dragleave.prevent="handleFolderDragLeave"
      @drop.prevent="handleFolderDrop($event, folder)"
      @dblclick="handleFolderDoubleClick(folder)"
      @click="handleFolderClick(folder)"
      :class="{
        // 拖拽状态样式优化
        'border-primary bg-blue-50 dark:border-blue-400 dark:bg-blue-900/20 ring-2 ring-blue-200 dark:ring-blue-800/50 transform scale-[1.02]': draggingFolder === folder,
        'bg-gray-200 dark:bg-dark-bg-secondary border-gray-500 dark:border-gray-200': selectedFolder === folder && draggingFolder !== folder
      }"
    >
      <div class="folder-header flex items-center justify-between">
        <div class="folder-info flex items-center">
          <i class="fa-solid fa-folder text-gray-500 dark:text-gray-400 mr-2"></i>
          <span class="font-medium text-sm text-gray-700 dark:text-gray-300">{{ folder.name }}</span>
          <!-- 优化上传提示信息 -->
          <div v-if="draggingFolder === folder" class="ml-2 text-xs font-semibold text-primary bg-primary/10 dark:bg-primary/20 px-2 py-0.5 rounded-full animate-pulse">
            <i class="fa-solid fa-upload mr-1 text-xs"></i>释放以上传
          </div>
        </div>
        <Button
          icon="fa-trash-can"
          tooltip="删除此知识库文件夹"
          @click.stop="handleDeleteFolder(folder)"
          class="text-gray-500 hover:text-red-500 text-sm"
          variant="secondary"
          size="md"
          shape="full"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Button from '../../../shared/ui/Button.vue';
import { useFileManagement } from '../../composables/useFileManagement.js';

// 使用文件管理组合函数
const { batchUploadFiles } = useFileManagement();

defineProps({
  folders: {
    type: Array,
    default: () => []
  }
});

// 当前悬停的文件夹
const draggingFolder = ref(null);
// 选中的文件夹
const selectedFolder = ref(null);
// 用于区分单击和双击的定时器
let clickTimer = null;
// 上次点击的文件夹
let _lastClickedFolder = null;

// 处理文件夹拖拽悬停
const handleFolderDragOver = (event, folder) => {
  event.preventDefault();
  event.stopPropagation();
  draggingFolder.value = folder;
};

// 处理文件夹拖拽离开 - 优化以避免闪烁
  const handleFolderDragLeave = (event) => {
    // 获取当前鼠标位置
    const rect = event.currentTarget.getBoundingClientRect();
    // 使用requestAnimationFrame在下一帧检查鼠标位置
    requestAnimationFrame(() => {
      // 检查鼠标是否仍在文件夹元素的边界内
      const mouseX = event.clientX;
      const mouseY = event.clientY;
      
      // 如果鼠标仍然在文件夹元素的边界内，则不清除拖拽状态
      if (mouseX >= rect.left && mouseX <= rect.right && mouseY >= rect.top && mouseY <= rect.bottom) {
        return; // 鼠标仍在文件夹内，保持拖拽状态
      }
      
      // 鼠标确实离开了文件夹区域
      draggingFolder.value = null;
    });
  };
  
  // 处理文件夹拖拽放置
  const handleFolderDrop = async (event, folder) => {
    draggingFolder.value = null;
    const files = Array.from(event.dataTransfer.files);
    
    if (files && files.length > 0) {
      // 使用组合函数批量上传文件到指定文件夹
      await batchUploadFiles(files, folder.id);
    }
  };

// 处理文件夹点击事件
const handleFolderClick = (folder) => {
  // 每次点击都处理选中状态切换
  // 立即处理选中状态切换
  if (selectedFolder.value === folder) {
    selectedFolder.value = null;
  } else {
    selectedFolder.value = folder;
  }
  
  // 清除之前的定时器
  if (clickTimer) {
    clearTimeout(clickTimer);
  }
  
  // 更新最后点击的文件夹
  _lastClickedFolder = folder;
  
  // 设置定时器处理事件发送（延迟以区分双击）
  clickTimer = setTimeout(() => {
    // 触发folderSelected事件，让FilePanel处理
    const event = new CustomEvent('folderSelected', { detail: selectedFolder.value });
    window.dispatchEvent(event);
    
    clickTimer = null;
  }, 300); // 300ms是一个常用的双击判断阈值
};

// 处理文件夹双击事件
const handleFolderDoubleClick = (folder) => {
  // 清除单击定时器，防止触发事件发送
  if (clickTimer) {
    clearTimeout(clickTimer);
    clickTimer = null;
  }
  
  // 重置上次点击的文件夹
  _lastClickedFolder = null;
  
  // 触发folderDoubleClick事件，让FilePanel处理
  const event = new CustomEvent('folderDoubleClick', { detail: folder });
  window.dispatchEvent(event);
};

// 处理删除文件夹
const handleDeleteFolder = (folder) => {
  // 触发deleteFolder事件，让FilePanel处理
  const event = new CustomEvent('deleteFolder', { detail: folder });
  window.dispatchEvent(event);
};


</script>

<style scoped>
/* 文件夹列表样式 */
.folders-list {
  margin-top: 12px;
}

.folders-list h3 {
  font-size: 13px;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 8px;
  padding: 0 8px;
}

.dark .folders-list h3 {
  color: white;
}

.folder-item {
  transition: all 0.2s ease;
}

.folder-item:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.folder-item.cursor-pointer {
  transition: all 0.2s ease;
}

.folder-item.cursor-pointer:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* 拖拽上传样式 */
.folder-item.border-primary {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
  background-color: #eff6ff;
}/* 文件夹头部样式 */
.folder-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 28px;
  line-height: 28px;
}

/* 文件夹信息区域 */
.folder-info {
  display: flex;
  align-items: center;
}
</style>