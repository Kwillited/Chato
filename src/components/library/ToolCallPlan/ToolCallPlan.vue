<template>
  <div v-if="toolCalls && toolCalls.length > 0" :class="[
    'bg-transparent border border-dashed rounded-lg px-6 py-4 overflow-hidden transition-all duration-300 ease-in-out',
    containerClass,
    borderClass
  ]">
    <div class="flex items-start gap-3">
      <svg class="w-5 h-5 text-blue-500 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707-.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
      </svg>
      <div class="flex-1">
        <div class="text-sm text-blue-500 dark:text-blue-400 font-medium mb-3">
          工具调用计划
        </div>
        <div v-for="(toolCall, index) in toolCalls" :key="index" class="text-sm text-gray-600 dark:text-gray-300 mb-3">
          <div class="font-medium">工具: {{ toolCall.name }}</div>
          <div v-if="toolCall.args" class="mt-2 text-gray-500 dark:text-gray-400">
            参数: {{ formatArgs(toolCall.args) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  toolCalls: {
    type: Array,
    default: () => []
  },
  containerClass: {
    type: String,
    default: ''
  },
  borderClass: {
    type: String,
    default: 'border-blue-300 dark:border-blue-600'
  }
})

const formatArgs = (args) => {
  if (typeof args === 'object') {
    return JSON.stringify(args)
  }
  return args
}
</script>

<style scoped>
/* 深色模式切换过渡效果 */
.border-dashed {
  transition: border-color 0.3s ease;
}
</style>