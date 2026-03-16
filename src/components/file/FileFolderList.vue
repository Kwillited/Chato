<template>
  <div v-if="folders.length > 0" class="folders-list">
    <DragDropZone
      v-for="folder in folders"
      :key="folder.id || folder.path"
      container-class="relative"
      overlay-radius="rounded-lg"
      overlay-text="释放文件到此文件夹"
      sub-text=""
      icon-class="text-lg mb-0"
      main-text-class="text-xs"
      @drop="(files) => handleFolderDrop(files, folder)"
    >
      <div
        class="folder-item border border-gray-300 dark:border-gray-600 rounded-lg p-3 mb-2 cursor-pointer hover:bg-gray-200 dark:hover:bg-dark-500 transition-all duration-300"
        @dblclick="handleFolderDoubleClick(folder)"
        @click="handleFolderClick(folder)"
        :class="{
          'bg-gray-300 dark:bg-dark-400 border-gray-500 dark:border-gray-200': (localSelectedFolder ? localSelectedFolder.id === folder.id : selectedFolder && selectedFolder.id === folder.id)
        }"
      >
        <div class="folder-header flex items-center justify-between">
          <div class="folder-info flex items-center">
            <i class="fa-solid fa-folder text-gray-500 dark:text-gray-400 mr-2"></i>
            <span class="font-medium text-sm text-gray-700 dark:text-gray-300">{{ folder.name }}</span>
          </div>
          <Button
            shape="full"
            size="md"
            icon="fa-trash-can"
            tooltip="删除此知识库文件夹"
            @click.stop="handleDeleteFolder(folder)"
            class="text-gray-500 hover:text-red-500 text-sm"
          />
        </div>
      </div>
    </DragDropZone>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Button } from '../library/index.js';
import DragDropZone from '../common/DragDropZone.vue';
import { useFileStore } from '../../store/fileStore.js';

// 初始化stores
const fileStore = useFileStore();

defineProps({
  folders: {
    type: Array,
    default: () => []
  }
});

// 选中的文件夹 - 从fileStore获取
const selectedFolder = computed(() => fileStore.currentFolder);
// 本地选中状态，用于即时视觉反馈
const localSelectedFolder = ref(null);
// 用于区分单击和双击的定时器
let clickTimer = null;
// 上次点击的文件夹
let _lastClickedFolder = null;

// 处理文件夹拖拽放置
const handleFolderDrop = (files, folder) => {
  if (files && files.length > 0) {
    // 直接调用fileStore方法批量上传文件到指定文件夹
    fileStore.batchUploadFiles(files, folder.id);
  }
};

// 处理文件夹点击事件
const handleFolderClick = (folder) => {
  // 每次点击都处理选中状态切换
  let newSelectedFolder = null;
  if (selectedFolder.value && selectedFolder.value.id === folder.id) {
    newSelectedFolder = null;
  } else {
    newSelectedFolder = folder;
  }
  
  // 立即更新本地状态，提供即时视觉反馈
  // 这会立即取消之前选中的文件夹的激活状态
  localSelectedFolder.value = newSelectedFolder;
  
  // 清除之前的定时器
  if (clickTimer) {
    clearTimeout(clickTimer);
  }
  
  // 更新最后点击的文件夹
  _lastClickedFolder = folder;
  
  // 设置定时器处理事件发送（延迟以区分双击）
  clickTimer = setTimeout(() => {
    // 触发folderSelected事件，让FilePanel处理
    const event = new CustomEvent('folderSelected', { detail: newSelectedFolder });
    window.dispatchEvent(event);
    
    // 清除本地状态，让computed属性接管
    localSelectedFolder.value = null;
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
  
  // 清除本地选中状态
  localSelectedFolder.value = null;
  
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



// 组件挂载时从localStorage恢复选中状态
onMounted(() => {
  const savedFolder = localStorage.getItem('ragSelectedFolder');
  if (savedFolder) {
    try {
      const folder = JSON.parse(savedFolder);
      // 直接设置保存的文件夹对象到fileStore
      // 这样即使folders还没加载完成，也能正确恢复状态
      fileStore.currentFolder = folder;
    } catch (e) {
      console.error('Failed to parse saved folder:', e);
    }
  }
});

</script>

<style scoped>
/* 文件夹列表样式 */
.folders-list {
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
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* 文件夹头部样式 */
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