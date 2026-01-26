<template>
  <!-- MCP工具列表侧边栏组件 -->
  <Sidebar type="left" class="mcp-tool-sidebar">
    <template #content>
      <div class="mcp-tool-panel">
        <!-- 标题和搜索 -->
        <div class="p-4 border-b border-gray-100 dark:border-dark-700">
          <h3 class="text-lg font-bold mb-3 text-gray-800 dark:text-white">MCP工具</h3>
          <div class="relative">
            <input 
              type="text" 
              placeholder="搜索工具..." 
              class="w-full pl-9 pr-4 py-2 rounded-lg bg-gray-50 dark:bg-dark-800 border border-gray-200 dark:border-dark-700 text-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              v-model="searchQuery"
            >
            <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">🔍</span>
          </div>
        </div>
        
        <!-- 工具分类列表 -->
        <div class="tool-list overflow-y-auto">
          <div v-for="category in filteredCategories" :key="category.id" class="tool-category mb-4">
            <h4 class="text-sm font-semibold px-4 py-2 bg-gray-50 dark:bg-dark-800 text-gray-700 dark:text-gray-300 border-b border-gray-100 dark:border-dark-700">
              {{ category.name }}
            </h4>
            
            <div class="space-y-1">
              <div 
                v-for="tool in category.tools" 
                :key="tool.id"
                class="tool-item p-3 mx-2 my-1 rounded-lg cursor-pointer transition-all"
                :class="{ 
                  'bg-blue-50 dark:bg-dark-600 border border-blue-200 dark:border-blue-900': selectedToolId === tool.id, 
                  'hover:bg-gray-100 dark:hover:bg-dark-700': selectedToolId !== tool.id 
                }"
                @click="selectTool(tool.id)"
              >
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-lg bg-gray-200 dark:bg-dark-700 flex items-center justify-center text-lg">
                    {{ tool.icon }}
                  </div>
                  <div class="flex flex-col min-w-0">
                    <span class="font-medium text-gray-800 dark:text-white truncate">{{ tool.name }}</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                      {{ tool.description }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="filteredCategories.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-8 px-4">
            <p>没有找到匹配的工具</p>
            <p class="text-xs mt-1">请尝试调整搜索关键词</p>
          </div>
        </div>
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import { ref, computed } from 'vue';
import Sidebar from '../../shared/ui/layout/Sidebar.vue';

// 搜索查询
const searchQuery = ref('');
// 选中的工具ID
const selectedToolId = ref(null);

// MCP工具数据
const toolCategories = ref([
  {
    id: 1,
    name: '数据分析',
    tools: [
      {
        id: 101,
        name: '数据可视化',
        description: '生成各种数据图表',
        icon: '📊'
      },
      {
        id: 102,
        name: '统计分析',
        description: '进行统计计算和分析',
        icon: '📈'
      },
      {
        id: 103,
        name: '数据清洗',
        description: '清理和预处理数据',
        icon: '🧹'
      }
    ]
  },
  {
    id: 2,
    name: '开发工具',
    tools: [
      {
        id: 201,
        name: '代码生成',
        description: '根据需求生成代码',
        icon: '💻'
      },
      {
        id: 202,
        name: '代码审查',
        description: '检查代码质量和问题',
        icon: '🔍'
      },
      {
        id: 203,
        name: 'API测试',
        description: '测试和验证API',
        icon: '🔌'
      },
      {
        id: 204,
        name: '数据库工具',
        description: '数据库管理和操作',
        icon: '🗄️'
      }
    ]
  },
  {
    id: 3,
    name: '文档处理',
    tools: [
      {
        id: 301,
        name: '文档生成',
        description: '自动生成各类文档',
        icon: '📄'
      },
      {
        id: 302,
        name: '文档翻译',
        description: '多语言文档翻译',
        icon: '🌐'
      },
      {
        id: 303,
        name: '文档摘要',
        description: '生成文档摘要',
        icon: '📝'
      }
    ]
  },
  {
    id: 4,
    name: '系统管理',
    tools: [
      {
        id: 401,
        name: '日志分析',
        description: '分析系统日志',
        icon: '📋'
      },
      {
        id: 402,
        name: '性能监控',
        description: '监控系统性能',
        icon: '📊'
      },
      {
        id: 403,
        name: '安全扫描',
        description: '系统安全扫描',
        icon: '🔒'
      }
    ]
  }
]);

// 过滤工具分类
const filteredCategories = computed(() => {
  if (!searchQuery.value) return toolCategories.value;
  
  const query = searchQuery.value.toLowerCase();
  return toolCategories.value
    .map(category => {
      const filteredTools = category.tools.filter(tool => 
        tool.name.toLowerCase().includes(query) || 
        tool.description.toLowerCase().includes(query)
      );
      return { ...category, tools: filteredTools };
    })
    .filter(category => category.tools.length > 0);
});

// 选择工具
const selectTool = (toolId) => {
  selectedToolId.value = toolId;
  // 可以触发工具详情或使用逻辑
};
</script>

<style scoped>
.mcp-tool-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tool-list {
  flex: 1;
  overflow-y: auto;
}

.tool-category {
  /* 工具分类样式 */
}

.tool-item {
  /* 工具项基础样式 */
}

.tool-list::-webkit-scrollbar {
  width: 4px;
}
</style>