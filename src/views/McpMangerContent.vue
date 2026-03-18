<template>
  <!-- MCP管理主内容区域 -->
  <div id="mcpMangerMainContent" class="flex-1 flex flex-col overflow-hidden bg-transparent dark:bg-transparent">

    
    <!-- 移动端标题 -->
    <div class="md:hidden p-3 text-center">
      <h2 class="text-lg font-bold text-dark dark:text-white">MCP工具管理</h2>
      <span class="text-sm text-gray-500">({{filteredTools.length}}个工具)</span>
    </div>
    
    <div class="flex-1 flex flex-col p-4 gap-4 overflow-hidden">
      
      <!-- 配置管理卡片（上面的卡片） -->
      <Card class="p-4 flex flex-col">
        <!-- 标题 -->
        <h3 class="text-sm font-semibold mb-4">配置管理</h3>
        
        <!-- 响应式布局容器 -->
        <div class="flex flex-col md:flex-row gap-4 flex-1">
          <!-- 上传JSON文件（左侧） -->
          <div class="flex-1 flex flex-col">
            <h4 class="text-xs font-medium text-gray-500 mb-2 flex items-center justify-between h-8">
              上传JSON配置文件
              <div class="flex space-x-1 opacity-0">
                <div class="w-16 h-6"></div>
                <div class="w-16 h-6"></div>
                <div class="w-16 h-6"></div>
              </div>
            </h4>
            <div 
              class="flex-1 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer flex flex-col items-center justify-center"
              @click="triggerJsonUpload"
              @dragover.prevent="handleDragOver"
              @dragenter.prevent="handleDragEnter"
              @dragleave.prevent="handleDragLeave"
              @drop.prevent="handleDrop"
              :class="{ 'border-primary bg-primary-50 dark:bg-primary-900/20': isDragging }"
            >
              <i class="fa-solid fa-file-json text-gray-400 text-2xl mb-2"></i>
              <p class="text-xs text-gray-500 mb-2">{{ isDragging ? '释放文件以上传' : '点击或拖拽文件到此处' }}</p>
              <p class="text-xs text-gray-400">支持 .json 文件</p>
              <input 
                type="file" 
                ref="jsonFileInput" 
                class="hidden" 
                accept=".json" 
                @change="handleJsonUpload"
              >
            </div>
          </div>
          
          <!-- 配置输入（右侧） -->
          <div class="flex-1 flex flex-col">
            <h4 class="text-xs font-medium text-gray-500 mb-2 flex items-center justify-between h-8">
              手动输入配置
              <div class="flex space-x-1">
                <Button 
                  shape="rounded"
                  size="sm"
                  class="flex-1 whitespace-nowrap"
                  @click="saveConfig"
                  :loading="isSavingConfig"
                  content="保存"
                />
                <Button 
                  shape="rounded"
                  size="sm"
                  class="flex-1 whitespace-nowrap"
                  @click="clearConfig"
                  content="清空"
                />
                <Button 
                  shape="rounded"
                  size="sm"
                  class="flex-1 whitespace-nowrap"
                  @click="exportConfig"
                  content="导出"
                />
              </div>
            </h4>
            <textarea 
    v-model="configInput"
    :placeholder="configInput ? '' : '输入JSON配置，例如：{key: value}'"
    class="w-full min-h-24 p-3 rounded-lg focus:outline-none text-sm font-mono config-textarea"
  ></textarea>
          </div>
        </div>
      </Card>
      
      <!-- 下方左右卡片 -->
      <div class="flex-1 flex flex-col md:flex-row gap-4 overflow-hidden">
        <!-- 工具列表卡片（左侧） -->
        <Card class="p-4 flex-1 min-w-[300px] flex flex-col overflow-hidden">
          <!-- 标题和搜索框 -->
          <div class="mb-4 flex-shrink-0 flex flex-col space-y-2">
            <div class="flex items-center">
              <h3 class="text-sm font-semibold">MCP 工具列表</h3>
            </div>
            <!-- 搜索框 -->
            <div class="relative flex-1">
              <input
                type="text"
                v-model="searchQuery"
                placeholder="搜索工具..."
                class="w-full pl-8 pr-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
              >
              <i class="fa-solid fa-search absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"></i>
            </div>
          </div>
          <div class="space-y-2 overflow-y-auto flex-1 scrollbar-thin">
            <div v-for="tool in filteredTools" :key="tool.id" 
                 class="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow p-3 cursor-pointer flex items-center justify-between relative"
                 @click="selectTool(tool)">
                 <div class="absolute inset-0 rounded-lg" :class="{'ring-2 ring-primary ring-opacity-50': selectedTool && selectedTool.id === tool.id}"></div>
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
            </div>
            
            <!-- 空状态 -->
            <div v-if="filteredTools.length === 0 && !isLoading" class="flex flex-col items-center justify-center h-full text-gray-500">
              <i class="fa-solid fa-toolbox text-4xl mb-4"></i>
              <p>暂无MCP工具</p>
              <p class="text-sm mt-2">点击上传按钮添加新的MCP工具</p>
            </div>
            
            <!-- 加载状态 -->
            <div v-if="isLoading">
              <SkeletonLoader type="tools" :count="5" />
            </div>
          </div>
        </Card>
        
        <!-- 工具详情卡片（右侧） -->
        <Card class="p-4 flex-1 min-w-[300px] flex flex-col overflow-hidden">
          <!-- 标题 -->
          <div class="mb-4 flex-shrink-0">
            <h3 class="text-sm font-semibold">工具详情</h3>
          </div>
          
          <!-- 未选择工具状态 -->
          <div v-if="!selectedTool" class="flex-1 flex flex-col items-center justify-center text-gray-400">
            <i class="fa-solid fa-info-circle text-2xl mb-2"></i>
            <p class="text-xs">请从左侧列表选择一个工具查看详情</p>
          </div>
          
          <!-- 工具详情内容 -->
          <div v-else class="flex-1 space-y-4 overflow-y-auto scrollbar-thin">
            <!-- 工具基本信息 -->
            <div>
              <h4 class="text-xs font-medium text-gray-500 mb-2">基本信息</h4>
              <div class="bg-gray-50 dark:bg-dark-800 rounded-lg p-3">
                <div class="flex items-center space-x-3 mb-3">
                  <div :class="getToolIconClass(selectedTool.type)" class="w-10 h-10 rounded-full flex items-center justify-center">
                    <i :class="getToolIcon(selectedTool.type)"></i>
                  </div>
                  <div>
                    <p class="text-sm font-medium">{{ selectedTool.name }}</p>
                    <p class="text-xs text-gray-500">{{ selectedTool.type || 'custom' }}</p>
                  </div>
                </div>
                <div class="text-xs text-gray-600 dark:text-gray-400">
                  <p class="mb-1">{{ selectedTool.description || '暂无描述' }}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
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
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showNotification } from '../utils/notificationUtils.js';
import { Button, Card } from '../components/library/index.js';
import ConfirmationModal from '../components/common/ConfirmationModal.vue';
import SkeletonLoader from '../components/common/SkeletonLoader.vue';
import { useSettingsStore } from '../store/settingsStore.js';
import { useRouteState } from '../composables/useRouteState';
import { eventBus } from '../services/eventBus.js';
import { apiService } from '../services/apiService.js';

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

// 配置管理相关
const configInput = ref('');
const jsonFileInput = ref(null);
const isSavingConfig = ref(false);
const isDragging = ref(false);

// 工具详情相关
const selectedTool = ref(null);
// 使用 useRouteState 管理 currentServer 状态
const { state: currentServer, setState: setCurrentServer } = useRouteState('server', '');
// 路由对象
const route = useRoute();

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

// 刷新工具列表
const refreshTools = async () => {
  // 先设置加载状态
  isLoading.value = true;
  // 清空工具列表，避免显示旧内容
  tools.value = [];
  try {
    let url = '/mcp/tools';
    if (currentServer.value) {
      url = `/mcp/tools/${currentServer.value}`;
    }
    // 调用API获取MCP工具列表
    const data = await apiService.get(url);
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

// 根据服务器名称获取工具列表
const loadToolsByServer = async (serverName) => {
  currentServer.value = serverName;
  // 先清空工具列表，避免显示旧内容
  tools.value = [];
  await refreshTools();
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

// 触发JSON文件上传
const triggerJsonUpload = () => {
  jsonFileInput.value?.click();
};

// 处理JSON文件内容
const processJsonFile = (content) => {
  try {
    // 检查内容是否为空
    if (!content || !content.trim()) {
      showNotification('JSON文件为空', 'error');
      return false;
    }
    
    // 验证是否为有效的JSON
    JSON.parse(content);
    // 设置到配置输入框
    configInput.value = content;
    showNotification('JSON文件加载成功', 'success');
    return true;
  } catch (error) {
    let errorMessage = '无效的JSON文件';
    if (error instanceof SyntaxError) {
      if (error.message.includes('Unexpected end of JSON input')) {
        errorMessage = 'JSON文件不完整或为空';
      } else if (error.message.includes('Unexpected token')) {
        errorMessage = 'JSON格式错误：' + error.message;
      }
    }
    showNotification(errorMessage, 'error');
    console.error('Invalid JSON file:', error);
    return false;
  }
};

// 拖拽相关方法
const handleDragEvent = (event) => {
  event.preventDefault();
  isDragging.value = true;
};

const handleDragOver = handleDragEvent;
const handleDragEnter = handleDragEvent;

const handleDragLeave = (event) => {
  event.preventDefault();
  isDragging.value = false;
};

const handleDrop = (event) => {
  event.preventDefault();
  isDragging.value = false;
  
  const files = event.dataTransfer.files;
  if (files && files.length > 0) {
    const file = files[0];
    if (file.name.toLowerCase().endsWith('.json')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        processJsonFile(e.target.result);
      };
      reader.onerror = () => {
        showNotification('文件读取失败', 'error');
      };
      reader.readAsText(file);
    } else {
      showNotification('请上传JSON文件', 'error');
    }
  }
};

// 处理JSON文件上传
const handleJsonUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  try {
    const reader = new FileReader();
    reader.onload = (e) => {
      processJsonFile(e.target.result);
    };
    reader.onerror = () => {
      showNotification('文件读取失败', 'error');
    };
    reader.readAsText(file);
  } catch (error) {
    console.error('Failed to upload JSON file:', error);
    showNotification('文件上传失败', 'error');
  } finally {
    // 重置文件输入，允许重复上传同一个文件
    event.target.value = '';
  }
};

// 保存配置
const saveConfig = async () => {
  try {
    isSavingConfig.value = true;
    
    // 检查配置是否为空
    const isEmptyConfig = !configInput.value.trim();
    
    // 如果配置不为空，验证JSON格式
    if (!isEmptyConfig) {
      try {
        JSON.parse(configInput.value);
      } catch (error) {
        showNotification('无效的JSON格式', 'error');
        return;
      }
    }
    
    // 获取当前完整配置
    const currentConfig = await apiService.get('/mcp/config');
    
    // 构建请求体
    let requestBody;
    if (currentServer.value) {
      // 只更新当前服务器的配置
      requestBody = { ...currentConfig };
      if (isEmptyConfig) {
        // 清空当前服务器配置
        delete requestBody[currentServer.value];
      } else {
        // 解析配置，提取服务器配置
        const parsedConfig = JSON.parse(configInput.value);
        // 提取当前服务器的配置（即使配置中包含其他服务器，也只使用当前服务器的）
        if (parsedConfig[currentServer.value]) {
          requestBody[currentServer.value] = parsedConfig[currentServer.value];
        }
      }
    } else {
      // 更新完整配置
      requestBody = isEmptyConfig ? {} : JSON.parse(configInput.value);
    }
    
    const result = await apiService.post('/mcp/config', requestBody);
    showNotification(result.message || (isEmptyConfig ? '配置已清空' : '配置保存成功'), 'success');
    console.log('Saved config:', result.config);
    
    // 发送事件通知其他组件配置已更新
    eventBus.emit('mcpConfigUpdated');
    console.log('MCP config updated event emitted');
  } catch (error) {
    console.error('Failed to save config:', error);
    showNotification(error.message || '配置保存失败', 'error');
  } finally {
    isSavingConfig.value = false;
  }
};

// 清空配置
const clearConfig = async () => {
  configInput.value = '';
  // 自动保存空配置，以清空后端配置文件
  await saveConfig();
};

// 导出配置
const exportConfig = () => {
  if (!configInput.value.trim()) {
    showNotification('没有可导出的配置', 'warning');
    return;
  }
  
  try {
    // 验证JSON格式
    JSON.parse(configInput.value);
    
    // 创建Blob对象
    const blob = new Blob([configInput.value], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // 创建下载链接
    const a = document.createElement('a');
    a.href = url;
    a.download = `mcp-config-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    
    // 释放URL对象
    URL.revokeObjectURL(url);
    
    showNotification('配置导出成功', 'success');
  } catch (error) {
    console.error('Failed to export config:', error);
    showNotification('配置导出失败，无效的JSON格式', 'error');
  }
};

// 选择工具
const selectTool = (tool) => {
  selectedTool.value = tool;
  console.log('Selected tool:', tool.name);
};

// 从后端获取当前的MCP配置
const fetchCurrentConfig = async () => {
  try {
    // 计算配置文件路径: H:\ChaTo\backend\config\mcp_config.json
    // 由于前端无法直接读取本地文件，我们需要通过API获取
    // 注意：这里假设后端已经提供了获取配置文件的API
    // 如果没有，我们可以在后端添加一个API端点
    
    // 使用 apiService 获取配置
    const config = await apiService.get('/mcp/config');
    if (currentServer.value) {
      // 显示包含服务器名的完整结构
      const serverConfig = config[currentServer.value];
      if (serverConfig) {
        const configWithServerName = {
          [currentServer.value]: serverConfig
        };
        configInput.value = JSON.stringify(configWithServerName, null, 2);
      } else {
        configInput.value = '';
      }
    } else {
      // 显示完整配置
      configInput.value = JSON.stringify(config, null, 2);
    }
  } catch (error) {
    console.error('获取配置失败:', error);
    // 如果API调用失败，尝试从后端的默认配置中获取
    console.log('获取配置失败，使用默认值');
  }
};

// 组件挂载时加载工具和配置
onMounted(async () => {
  console.log('McpMangerContent组件挂载');
  // 根据当前服务器状态加载工具列表
  if (currentServer.value) {
    await loadToolsByServer(currentServer.value);
  } else {
    // 加载所有MCP工具
    await refreshTools();
  }
  await fetchCurrentConfig();
});

// 监听 currentServer 变化，加载工具列表和配置
watch(currentServer, async (newServerName) => {
  console.log('服务器名称变化:', newServerName);
  if (newServerName) {
    await loadToolsByServer(newServerName);
  } else {
    // 加载所有MCP工具
    await refreshTools();
  }
  // 重新获取配置，显示当前服务器的配置
  await fetchCurrentConfig();
});
</script>

<style scoped>
/* 组件特定样式 - 遵循项目整体风格 */



/* 配置输入textarea样式 */
.config-textarea {
  border: 1px solid #d1d5db !important;
  background-color: white !important;
  color: #374151 !important;
  outline: none !important;
  box-shadow: none !important;
}

.dark .config-textarea {
  border: 1px solid #4b5563 !important;
  background-color: #1f2937 !important;
  color: white !important;
}

.config-textarea:focus {
  border: 1px solid #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

.dark .config-textarea:focus {
  border: 1px solid #3b82f6 !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
}
</style>