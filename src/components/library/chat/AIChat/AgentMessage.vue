<template>
  <!-- 基于step的消息内容气泡 -->
  <div v-if="messageValue.steps && messageValue.steps.length > 0" class="space-y-3 mt-2">
    <div 
      v-for="step in messageValue.steps" 
      :key="step.agent_step" 
      :class="stepBubbleClasses"
    >
      <!-- 步骤标签 -->
      <div class="text-xs text-blue-500 dark:text-blue-400 mb-2 font-medium">
        步骤 {{ step.agent_step }}: {{ getNodeLabel(step.node) }}
      </div>
      
      <!-- 思考内容 -->
      <div v-if="step.thinking" class="relative mb-3">
        <div class="bg-transparent border border-dashed border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 overflow-hidden transition-all duration-300 ease-in-out w-full">
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-start gap-2 flex-1">
              <svg class="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707-.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
              <div 
                :class="[
                  'text-xs text-gray-500 dark:text-gray-400 leading-relaxed italic transition-all duration-300 ease-in-out overflow-hidden',
                  step.thinkingCompleted ? 'max-h-10' : ''
                ]"
                v-html="step.thinking"
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 步骤的工具执行状态 -->
      <ToolExecutionStatus 
        v-for="(tool, index) in step.toolExecutions" 
        :key="index"
        :tool="tool"
        :containerClass="`w-fit max-w-full mt-3${index > 0 ? ' mt-2' : ''}`"
      />
      
      <!-- 步骤内容 -->
      <div v-if="step.content" class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="step.content"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ToolExecutionStatus } from '../../index.js'
import { useChatBubble } from '../../../../composables/useChatBubble.js'

const props = defineProps({
  message: {
    type: [Object, Function],
    required: true,
    default: () => ({})
  },
  containerClass: {
    type: String,
    default: ''
  }
})

// 使用公共聊天气泡逻辑
const { 
  messageValue
} = useChatBubble(props)

// 计算步骤气泡样式类
const stepBubbleClasses = computed(() => {
  return [
    messageValue.value.event === 'on_chat_model_stream' 
      ? 'bg-blue-50 dark:bg-blue-900/20 rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-blue-800/30 overflow-hidden'
      : 'bg-gray-200 dark:bg-dark-500 rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-dark-border overflow-hidden',
    'w-fit',
    'max-w-full',
    props.containerClass
  ]
})

// 获取节点类型标签
const getNodeLabel = (node) => {
  const nodeLabels = {
    'think': '思考',
    'analyze': '分析',
    'execute_tools': '执行工具',
    'default': '默认'
  }
  return nodeLabels[node] || node
}
</script>

<style scoped>
/* 步骤气泡样式 */
</style>