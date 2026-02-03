<template>
  <!-- MCP管理主内容区域 -->
  <div id="mcpMangerMainContent" class="flex-1 flex flex-col overflow-hidden bg-transparent dark:bg-transparent">
    <!-- 顶部导航 -->
    <div class="panel-header p-3 flex flex-wrap items-center justify-between gap-4 transition-all duration-300">
      <!-- 左侧区域：搜索框 -->
      <div class="flex-1 min-w-0">
        <!-- 搜索框 -->
        <div class="relative w-full min-w-[200px]">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索MCP工具..."
            class="w-full pl-10 pr-4 py-1 border border-gray-300 rounded-[15px] focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            @input="handleSearch"
          >
          <i class="fa-solid fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
        </div>
      </div>
      
      <!-- 中间标题 -->
      <div class="hidden md:flex items-center">
        <h2 class="text-lg font-bold text-dark dark:text-white">MCP工具管理</h2>
        <span class="text-sm text-gray-500 ml-2">({{filteredTools.length}}个工具)</span>
      </div>
      
      <!-- 右侧按钮区域 -->
      <div class="flex items-center space-x-4">
        <!-- 上传工具按钮 -->
        <Button 
          shape="full"
          size="md"
          icon="fa-upload" 
          tooltip="上传MCP工具"
          @click="handleUploadClick"
        />
        
        <!-- 刷新按钮 -->
        <Button 
          shape="full"
          size="md"
          icon="fa-arrows-rotate" 
          tooltip="刷新工具列表"
          @click="refreshTools"
        />
      </div>
    </div>
    
    <!-- 移动端标题 -->
    <div class="md:hidden p-3 text-center">
      <h2 class="text-lg font-bold text-dark dark:text-white">MCP工具管理</h2>
      <span class="text-sm text-gray-500">({{filteredTools.length}}个工具)</span>
    </div>
    
    <!-- 工具列表/网格容器 -->
    <div class="flex-1 overflow-y-auto p-4">
      
      <!-- 工具列表视图 -->
      <div class="w-full h-full flex">
        <!-- 工具列表 -->
        <div class="card p-4 depth-1 hover:depth-2 transition-all duration-300 h-full max-w-2xl flex flex-col">
          <!-- 标题和搜索框 -->
          <div class="mb-4 flex-shrink-0 flex items-center space-x-4">
            <h3 class="text-sm font-semibold">MCP 工具列表</h3>
            <div class="relative flex-1">
              <input
                type="text"
                v-model="searchQuery"
                placeholder="搜索工具..."
                class="w-full pl-8 pr-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                @input="handleSearch"
              >
              <i class="fa-solid fa-search absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"></i>
            </div>
          </div>
          <div class="space-y-2 overflow-y-auto overflow-x-hidden flex-1">
            <div v-for="tool in filteredTools" :key="tool.id" 
                 class="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow p-3 cursor-pointer flex items-center justify-between relative">
              <!-- 左侧：工具图标和信息 -->
              <div class="flex items-center space-x-3">
                <!-- 工具图标 -->
                <div :class="getToolIconClass(tool.type)" class="w-10 h-10 rounded-full flex items-center justify-center">
                  <i :class="getToolIcon(tool.type)"></i>
                </div>
                <!-- 工具信息 -->
                <div class="flex-1 min-w-0">
                  <!-- 工具名 -->
                  <div class="text-sm font-medium truncate" :title="tool.description">{{ tool.name }}</div>
                </div>
              </div>
              <!-- 右侧：操作按钮 -->
              <div class="flex items-center space-x-2">
                <Button 
                  shape="full"
                  size="sm"
                  icon="fa-eye" 
                  tooltip="查看详情"
                  class="text-gray-500 hover:text-primary w-6 h-6 p-1"
                />
                <Button 
                  shape="full"
                  size="sm"
                  icon="fa-trash" 
                  tooltip="删除"
                  @click.stop="handleDeleteTool(tool.id)"
                  class="text-gray-500 hover:text-red-500 w-6 h-6 p-1"
                />
              </div>
            </div>
            
            <!-- 空状态 -->
            <div v-if="filteredTools.length === 0 && !isLoading" class="flex flex-col items-center justify-center h-64 text-gray-500">
              <i class="fa-solid fa-toolbox text-4xl mb-4"></i>
              <p>暂无MCP工具</p>
              <p class="text-sm mt-2">点击上传按钮添加新的MCP工具</p>
            </div>
            
            <!-- 加载状态 -->
            <div v-if="isLoading" class="flex flex-col items-center justify-center h-64 text-gray-500">
              <div class="w-10 h-10 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
              <p>加载中...</p>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { showNotification } from '../utils/notificationUtils.js';
import { Button } from '../components/library/index.js';
import ConfirmationModal from '../components/common/ConfirmationModal.vue';
import { useSettingsStore } from '../store/settingsStore.js';

// 状态管理
const settingsStore = useSettingsStore();

// 搜索相关
const searchQuery = ref('');

// 工具列表数据
const tools = ref([]);
const isLoading = ref(false);

// 确认删除模态框状态
const showDeleteModal = ref(false);
const currentDeleteToolId = ref(null);
const currentDeleteToolName = ref(null);
const isDeletingTool = ref(false);

// 计算属性：过滤工具
const filteredTools = computed(() => {
  let result = tools.value;
  
  // 根据搜索查询过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(tool => 
      tool.name.toLowerCase().includes(query) || 
      (tool.description && tool.description.toLowerCase().includes(query)) ||
      (tool.type && tool.type.toLowerCase().includes(query))
    );
  }
  
  return result;
});

// 处理搜索
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
};

// 刷新工具列表
const refreshTools = async () => {
  isLoading.value = true;
  try {
    // 调用API获取MCP工具列表
    const response = await fetch('/api/mcp/tools');
    if (!response.ok) {
      throw new Error('获取MCP工具失败');
    }
    const data = await response.json();
    tools.value = data || [];
  } catch (error) {
    console.error('刷新工具列表失败:', error);
    showNotification(`刷新工具列表失败: ${error.message || String(error)}`, 'error');
    tools.value = [];
  } finally {
    // 使用nextTick确保数据更新完成后再隐藏加载状态
    await nextTick();
    isLoading.value = false;
  }
};

// 处理上传工具
const handleUploadClick = async () => {
  try {
    // 创建原生文件选择器
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.py,.json';
    
    // 使用Promise处理文件选择事件
    const filesPromise = new Promise((resolve) => {
      input.onchange = (e) => {
        resolve(Array.from(e.target.files));
      };
    });
    
    // 触发文件选择器
    input.click();
    
    // 等待用户选择文件
    const selectedFiles = await filesPromise;
    
    if (selectedFiles && selectedFiles.length > 0) {
      // 处理文件上传
      for (const file of selectedFiles) {
        await uploadTool(file);
      }
      
      // 上传完成后刷新工具列表
      await refreshTools();
    }
  } catch (error) {
    console.error('上传工具失败:', error);
    showNotification(`上传工具失败: ${error.message || String(error)}`, 'error');
  }
};

// 上传单个工具
const uploadTool = async (file) => {
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
    // const response = await fetch('/api/mcp/upload', {
    //   method: 'POST',
    //   body: formData
    // });
    
    // 模拟上传成功
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    showNotification('工具上传成功', 'success');
    
  } catch (error) {
    console.error('上传工具失败:', error);
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
    // await fetch(`/api/mcp/tools/${currentDeleteToolId.value}`, {
    //   method: 'DELETE'
    // });
    
    // 从本地列表中删除工具
    const index = tools.value.findIndex(tool => tool.id === currentDeleteToolId.value);
    if (index !== -1) {
      const deletedTool = tools.value.splice(index, 1)[0];
      showNotification(`${deletedTool.name} 已删除`, 'success');
    }
    
    // 关闭模态框
    showDeleteModal.value = false;
  } catch (error) {
    console.error('删除工具失败:', error);
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

// 组件挂载时加载工具
onMounted(() => {
  console.log('McpMangerContent组件挂载');
  refreshTools();
});
</script>

<style scoped>
/* 组件特定样式 - 遵循项目整体风格 */

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