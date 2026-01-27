<template>
  <div id="mcpPanel" class="h-full flex flex-col">
    <PanelHeader title="MCP服务" />
    
    <!-- 移除原有的handleBackToChat方法，使用PanelHeader组件的默认行为 -->

    <!-- 上传区域 -->
    <div class="p-3">
      <label class="upload-button cursor-pointer block w-full text-center px-4 py-3 border border-dashed border-gray-300 rounded-lg hover:border-primary hover:bg-primary/5 transition-all duration-300 text-sm">
        <i class="fa-solid fa-upload mr-2"></i>
        上传MCP工具
        <input type="file" accept=".py,.json" class="hidden" @change="handleFileUpload" />
      </label>
    </div>

    <!-- 搜索框 -->
    <SearchBar v-model="searchQuery" placeholder="搜索工具..." />

    <div class="overflow-y-auto h-[calc(100%-165px)] scrollbar-thin">
      <div class="p-2 space-y-4">
        <!-- 工具分类标题 -->
        <div class="tool-category">
          <h3 class="text-xs font-medium text-gray-500 mb-2 px-2">已上传工具</h3>
          
          <!-- 过滤后的工具列表 -->
          <div v-if="filteredTools.length > 0">
            <div v-for="tool in filteredTools" :key="tool.id" class="tool-item p-3 rounded-lg bg-white border border-gray-100 dark:bg-dark-700 hover:border-primary hover:bg-primary/5 cursor-pointer transition-all duration-300 relative">
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <div class="flex items-center space-x-3">
                    <div :class="getToolIconClass(tool.type)" class="w-8 h-8 rounded-full flex items-center justify-center">
                      <i :class="getToolIcon(tool.type)"></i>
                    </div>
                    <div>
                      <p class="font-medium text-sm">{{ tool.name }}</p>
                      <p class="text-xs text-gray-500">{{ tool.description }}</p>
                    </div>
                  </div>
                </div>
                <ActionButton 
                  class="text-neutral-400 hover:text-red-500 p-1.5 rounded-full hover:bg-red-50 transition-colors"
                  @click.stop="handleDeleteTool(tool.id)"
                  icon="fa-trash"
                  title="删除此工具"
                />
              </div>
            </div>
          </div>
          <div v-else class="text-center p-4 text-xs text-gray-400">
            没有找到匹配的工具
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 确认删除工具模态框 -->
  <ConfirmationModal
    :visible="showDeleteModal"
    title="确认删除"
    :message="`确定要删除工具 '${currentDeleteToolName}' 吗？`"
    confirmText="确认删除"
    :loading="isDeletingTool"
    loadingText="删除中..."
    @confirm="handleDeleteToolConfirm"
    @close="showDeleteModal = false"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { showNotification } from '../../services/notificationUtils.js';
import { useSearch } from '../../composables/useSearch.js';
import ActionButton from '../common/ActionButton.vue';
import ConfirmationModal from '../common/ConfirmationModal.vue';
import PanelHeader from '../common/PanelHeader.vue';

// 确认删除模态框状态
const showDeleteModal = ref(false);
const currentDeleteToolId = ref(null);
const currentDeleteToolName = ref(null);
const isDeletingTool = ref(false);

// 工具列表数据
const tools = ref([
  { id: 1, name: '天气查询', description: '查询指定城市的天气信息', type: 'weather' },
  { id: 2, name: '多模型集成', description: '不同AI模型的统一调用', type: 'multiModel' },
  { id: 3, name: '文件处理', description: '文档分析和转换工具', type: 'fileProcessor' }
]);

// 使用搜索组合式函数
const { searchQuery, filteredTools } = useSearch({
  data: tools,
  searchFields: (tool) => [tool.name, tool.description]
});

// 组件挂载时的初始化
onMounted(() => {
  // 可以在这里加载MCP工具配置或状态
  loadMcpTools();
});

// 加载MCP工具
const loadMcpTools = async () => {
  try {
    // 这里可以添加实际的API调用来获取可用的MCP工具列表
    console.log('Loading MCP tools...');
    // 模拟加载过程
    // const response = await apiService.getMcpTools();
    // tools.value = response.data || [];
  } catch (error) {
    console.error('Failed to load MCP tools:', error);
    showNotification('加载MCP工具失败', 'error');
  }
}

// 使用PanelHeader组件的默认返回行为

// 处理文件上传
const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  try {
    // 检查文件类型
    if (!['.py', '.json'].some(ext => file.name.toLowerCase().endsWith(ext))) {
      showNotification('请上传Python (.py) 或 JSON (.json) 文件', 'error');
      return;
    }
    
    // 创建FormData并添加文件
    const formData = new FormData();
    formData.append('toolFile', file);
    
    // 显示上传中通知
    showNotification('正在上传工具...', 'success');
    
    // 这里可以添加实际的上传API调用
    // const response = await apiService.uploadMcpTool(formData);
    
    // 模拟上传成功
    setTimeout(() => {
      // 为新上传的工具生成ID和默认信息
      const newToolId = Date.now();
      const fileExtension = file.name.split('.').pop().toLowerCase();
      
      tools.value.push({
        id: newToolId,
        name: file.name.replace(`.${fileExtension}`, ''),
        description: `${fileExtension.toUpperCase()} 工具`,
        type: 'custom'
      });
      
      showNotification('工具上传成功', 'success');
      
      // 清空文件输入
      event.target.value = '';
    }, 1000);
    
  } catch (error) {
    console.error('Failed to upload MCP tool:', error);
    showNotification('工具上传失败', 'error');
  }
};

// 处理删除工具 - 显示确认模态框
const handleDeleteTool = (toolId) => {
  // 查找要删除的工具
  const tool = tools.value.find(t => t.id === toolId);
  if (tool) {
    // 设置要删除的工具信息
    currentDeleteToolId.value = toolId;
    currentDeleteToolName.value = tool.name;
    // 显示确认模态框
    showDeleteModal.value = true;
  }
};

// 处理确认删除工具
const handleDeleteToolConfirm = async () => {
  if (!currentDeleteToolId.value) return;
  
  try {
    isDeletingTool.value = true;
    
    // 这里可以添加实际的删除API调用
    // await apiService.deleteMcpTool(currentDeleteToolId.value);
    
    // 从本地列表中删除工具
    const index = tools.value.findIndex(tool => tool.id === currentDeleteToolId.value);
    if (index !== -1) {
      const deletedTool = tools.value.splice(index, 1)[0];
      showNotification(`${deletedTool.name} 已删除`, 'success');
    }
    
    // 关闭模态框
    showDeleteModal.value = false;
  } catch (error) {
    console.error('Failed to delete MCP tool:', error);
    showNotification('工具删除失败', 'error');
  } finally {
    isDeletingTool.value = false;
  }
};

// 获取工具图标类
const getToolIconClass = (toolType) => {
  const iconClasses = {
    'weather': 'bg-blue-100 text-blue-500',
    'multiModel': 'bg-purple-100 text-purple-500',
    'fileProcessor': 'bg-green-100 text-green-500',
    'custom': 'bg-orange-100 text-orange-500'
  };
  return iconClasses[toolType] || 'bg-gray-100 text-gray-500';
};

// 获取工具图标
const getToolIcon = (toolType) => {
  const icons = {
    'weather': 'fa-solid fa-cloud-sun',
    'multiModel': 'fa-solid fa-brain',
    'fileProcessor': 'fa-solid fa-file-lines',
    'custom': 'fa-solid fa-code'
  };
  return icons[toolType] || 'fa-solid fa-toolbox';
};
</script>

<style scoped>
/* 组件特定样式 - 遵循项目整体风格 */
.tool-category {
  margin-bottom: 1rem;
}

.tool-item {
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: all 0.2s ease;
}

.tool-item:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.recent-tool-item {
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.btn-secondary {
  background: none;
  border: none;
  cursor: pointer;
  outline: none;
}

.upload-button {
  transition: all 0.2s ease;
}

/* 动画效果 */
.tool-item {
  transition: all 0.2s ease;
}

/* 确保滚动条样式与项目整体一致 */
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 20px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.7);
}
</style>