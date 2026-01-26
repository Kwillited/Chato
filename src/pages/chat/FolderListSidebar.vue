<template>
  <!-- 文件夹列表侧边栏组件 -->
  <Sidebar type="left" class="folder-list-sidebar">
    <template #content>
      <div class="folder-panel p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-800 dark:text-white">文件夹</h3>
          <button class="text-sm px-2 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors">
            + 新建
          </button>
        </div>
        
        <!-- 文件夹树结构 -->
        <div class="folder-tree">
          <div v-for="folder in folders" :key="folder.id" class="folder-item mb-2">
            <div 
              class="flex items-center gap-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-dark-700 cursor-pointer transition-colors"
              @click="toggleFolder(folder.id)"
            >
              <span class="text-gray-600 dark:text-gray-400">
                {{ folder.expanded ? '▼' : '▶' }}
              </span>
              <span class="text-gray-700 dark:text-gray-300">{{ folder.name }}</span>
              <span class="text-xs text-gray-500 dark:text-gray-400">({{ folder.itemCount }})</span>
            </div>
            
            <!-- 子文件夹/内容 -->
            <div 
              v-if="folder.expanded" 
              class="ml-6 mt-1 space-y-1"
            >
              <div 
                v-for="subItem in folder.items" 
                :key="subItem.id"
                class="flex items-center gap-2 p-1.5 rounded hover:bg-gray-50 dark:hover:bg-dark-800 cursor-pointer transition-colors text-sm"
              >
                <span class="text-gray-500 dark:text-gray-400">{{ getFileIcon(subItem.type) }}</span>
                <span class="text-gray-600 dark:text-gray-400">{{ subItem.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import { ref } from 'vue';
import Sidebar from '../../shared/ui/layout/Sidebar.vue';

// 文件夹数据
const folders = ref([
  {
    id: 1,
    name: '我的对话',
    expanded: true,
    itemCount: 5,
    items: [
      { id: 101, name: '项目讨论', type: 'chat' },
      { id: 102, name: '技术咨询', type: 'chat' },
      { id: 103, name: '学习笔记', type: 'chat' },
      { id: 104, name: '会议纪要', type: 'chat' },
      { id: 105, name: '待办事项', type: 'chat' }
    ]
  },
  {
    id: 2,
    name: '项目文件夹',
    expanded: false,
    itemCount: 3,
    items: [
      { id: 201, name: '项目A', type: 'folder' },
      { id: 202, name: '项目B', type: 'folder' },
      { id: 203, name: '项目C', type: 'folder' }
    ]
  },
  {
    id: 3,
    name: '归档',
    expanded: false,
    itemCount: 8,
    items: [
      { id: 301, name: '2024年对话', type: 'folder' },
      { id: 302, name: '已完成项目', type: 'folder' }
    ]
  }
]);

// 方法
const toggleFolder = (folderId) => {
  const folder = folders.value.find(f => f.id === folderId);
  if (folder) {
    folder.expanded = !folder.expanded;
  }
};

const getFileIcon = (type) => {
  switch (type) {
    case 'chat': return '💬';
    case 'folder': return '📁';
    default: return '📄';
  }
};
</script>

<style scoped>
.folder-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.folder-tree {
  flex: 1;
  overflow-y: auto;
}

.folder-item {
  /* 文件夹项样式 */
}

.folder-tree::-webkit-scrollbar {
  width: 4px;
}
</style>