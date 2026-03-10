<template>
  <!-- AI 消息内容气泡 -->
  <div v-if="hasContentToShow || messageValue.error || messageValue.isTyping" :class="bubbleClasses">
    <!-- 步骤标签 -->
    <div v-if="getNodeLabel(messageValue.node)" class="text-xs text-blue-500 dark:text-blue-400 mb-2 font-medium">
      步骤 {{ messageValue.agent_step }}: {{ getNodeLabel(messageValue.node) }}
    </div>
    
    <!-- 事件类型标签 -->
    <div v-else-if="messageValue.event" class="text-xs text-blue-500 dark:text-blue-400 mb-1 font-medium">
      {{ getEventLabel(messageValue.event) }}
    </div>
    
    <div v-if="contentWithoutTools" class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed">
      <VueChatoRenderer :content="contentWithoutTools" />
    </div>
    
    <!-- 错误状态显示 -->
    <div v-if="messageValue.error" class="chat-error mt-2">
      <i class="fa-solid fa-circle-exclamation text-red-500 mr-1"></i>
      <span>{{ messageValue.error }}</span>
    </div>
    
    <!-- 打字动画 -->
    <Loading 
      v-if="messageValue.isTyping" 
      type="typing" 
      size="small" 
      color="var(--text-color-secondary, #9ca3af)" 
      containerClass="mt-2"
      v-memo="[messageValue.isTyping]"
    />
  </div>
  
  <!-- 步骤的工具执行状态 -->
  <ToolExecutionStatus 
    v-for="(tool, index) in parsedToolExecutions" 
    :key="index"
    :tool="tool"
    :containerClass="`w-fit max-w-full mt-3${index > 0 ? ' mt-2' : ''}`"
  />
  
  <!-- 工具调用计划 -->
  <ToolCallPlan 
    v-if="messageValue.toolCalls && messageValue.toolCalls.length > 0"
    :toolCalls="messageValue.toolCalls"
    :containerClass="`w-fit max-w-full mt-3`"
  />
</template>

<script setup>
import { computed } from 'vue'
import { Loading, ToolExecutionStatus, ToolCallPlan } from '../../index.js'
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
  messageValue,
  getEventLabel,
  getNodeLabel,
  parseToolExecutions,
  extractNonToolContent
} = useChatBubble(props)

// 获取消息内容
const messageContent = computed(() => {
  return messageValue.value.content || messageValue.value.text || ''
})

// 用于触发更新的key值
const updateKey = computed(() => {
  return `${messageContent.value.length}-${messageValue.value.lastUpdate || Date.now()}`
})

// 检查是否有智能体相关内容
const hasAgentContent = computed(() => {
  return messageValue.value.agent_step !== undefined
})

// 计算气泡样式类
const bubbleClasses = computed(() => {
  return [
    messageValue.value.event === 'on_chat_model_stream' 
      ? 'bg-blue-50 dark:bg-blue-900/20 rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-blue-800/30 overflow-hidden'
      : 'bg-gray-200 dark:bg-dark-500 rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-dark-border overflow-hidden',
    'w-fit',
    'max-w-full',
    props.containerClass
  ]
})

// 解析工具执行信息
const parsedToolExecutions = computed(() => {
  // 检查是否已有工具执行记录
  if (messageValue.value.toolExecutions && messageValue.value.toolExecutions.length > 0) {
    return messageValue.value.toolExecutions
  }
  
  // 尝试从内容中解析工具执行信息
  const content = messageValue.value.content || ''
  return parseToolExecutions(content)
})

// 移除工具执行信息后的纯内容
const contentWithoutTools = computed(() => {
  const content = messageValue.value.content || ''
  return extractNonToolContent(content)
})

// 检查是否有实际内容需要显示
const hasContentToShow = computed(() => {
  const trimmedContent = messageContent.value.trim()
  const hasNonToolContent = contentWithoutTools.value.trim()
  return trimmedContent && hasNonToolContent
})


</script>

<style scoped>
/* 错误提示样式 */
.chat-error {
  color: var(--error-color);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  background-color: var(--error-bg);
  border: 1px solid var(--error-border);
  border-radius: 6px;
  padding: 8px 12px;
  margin-top: 8px;
}

/* 事件标签样式 */
.event-label {
  color: #4f46e5;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .event-label {
    color: #a5b4fc;
  }
  
  .chat-error {
    background-color: var(--dark-error-bg);
    border-color: var(--dark-error-border);
  }
}
</style>