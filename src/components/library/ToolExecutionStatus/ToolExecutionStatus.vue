<template>
  <!-- 直接渲染工具执行状态内容，移除外层的 div.relative -->
  <div v-if="tool" :class="[
    'bg-transparent border border-dashed rounded-lg px-4 py-2 overflow-hidden transition-all duration-300 ease-in-out',
    containerClass,
    tool.status === 'executing' 
      ? 'border-blue-300 dark:border-blue-600'
      : 'border-green-300 dark:border-green-600'
  ]">
    <div class="flex items-start justify-between gap-2">
      <div class="flex items-start gap-2 flex-1">
        <svg v-if="tool.status === 'executing'" class="w-4 h-4 text-blue-500 dark:text-blue-400 mt-0.5 flex-shrink-0 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        <svg v-else class="w-4 h-4 text-green-500 dark:text-green-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div :class="[
          'text-xs leading-relaxed transition-all duration-300 ease-in-out overflow-hidden',
          tool.status === 'executing' 
            ? 'text-blue-500 dark:text-blue-400'
            : 'text-green-500 dark:text-green-400'
        ]">
          <div class="font-medium">
            {{ tool.status === 'executing' ? '执行工具' : '工具执行成功' }}: {{ tool.name }}
          </div>
          <div v-if="tool.input" class="mt-1 text-gray-500 dark:text-gray-400">
            参数: {{ JSON.stringify(tool.input) }}
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 兼容旧格式的工具执行状态，移除外层的 div.relative -->
  <div v-else-if="messageStatus && currentTool" :class="[
    'bg-transparent border border-dashed rounded-lg px-4 py-2 overflow-hidden transition-all duration-300 ease-in-out',
    containerClass,
    messageStatus === 'tool_executing' 
      ? 'border-blue-300 dark:border-blue-600'
      : 'border-green-300 dark:border-green-600'
  ]">
    <div class="flex items-start justify-between gap-2">
      <div class="flex items-start gap-2 flex-1">
        <svg v-if="messageStatus === 'tool_executing'" class="w-4 h-4 text-blue-500 dark:text-blue-400 mt-0.5 flex-shrink-0 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        <svg v-else class="w-4 h-4 text-green-500 dark:text-green-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div :class="[
          'text-xs leading-relaxed transition-all duration-300 ease-in-out overflow-hidden',
          messageStatus === 'tool_executing' 
            ? 'text-blue-500 dark:text-blue-400'
            : 'text-green-500 dark:text-green-400'
        ]">
          <div class="font-medium">
            {{ messageStatus === 'tool_executing' ? '执行工具' : '工具执行成功' }}: {{ currentTool }}
          </div>
          <div v-if="toolInput" class="mt-1 text-gray-500 dark:text-gray-400">
            参数: {{ JSON.stringify(toolInput) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  tool: {
    type: Object,
    default: null
  },
  messageStatus: {
    type: String,
    default: null
  },
  currentTool: {
    type: String,
    default: null
  },
  toolInput: {
    type: Object,
    default: null
  },
  containerClass: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
/* 深色模式切换过渡效果 */
.border-dashed {
  transition: border-color 0.3s ease;
}
</style>