<template>
  <!-- 处理有agent_step的消息 -->
  <div v-if="messageValue.agent_step !== undefined" class="mt-2">
    <!-- 步骤标签 -->
    <div v-if="getNodeLabel(messageValue.node)" class="text-xs text-blue-500 dark:text-blue-400 mb-2 font-medium">
      步骤 {{ messageValue.agent_step }}: {{ getNodeLabel(messageValue.node) }}
    </div>
    
    <!-- 消息内容 -->
      <div v-if="contentWithoutTools" :class="stepBubbleClasses">
        <div class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="parsedContent"></div>
      </div>
      
      <!-- 步骤的工具执行状态 -->
      <ToolExecutionStatus 
        v-for="(tool, index) in parsedToolExecutions" 
        :key="index"
        :tool="tool"
        :containerClass="`w-fit max-w-full mt-3${index > 0 ? ' mt-2' : ''}`"
      />
      
      <!-- 工具调用计划 -->
      <div v-if="messageValue.toolCalls && messageValue.toolCalls.length > 0" class="mt-3">
        <div class="bg-transparent border border-dashed border-blue-300 dark:border-blue-600 rounded-lg px-4 py-2 overflow-hidden transition-all duration-300 ease-in-out w-fit max-w-full">
          <div class="flex items-start gap-2">
            <svg class="w-4 h-4 text-blue-500 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707-.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            <div class="flex-1">
              <div class="text-xs text-blue-500 dark:text-blue-400 font-medium mb-2">
                工具调用计划
              </div>
              <div v-for="(toolCall, index) in messageValue.toolCalls" :key="index" class="text-xs text-gray-600 dark:text-gray-300 mb-2">
                <div class="font-medium">工具: {{ toolCall.name }}</div>
                <div v-if="toolCall.args" class="mt-1 text-gray-500 dark:text-gray-400">
                  参数: {{ toolCall.args }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ToolExecutionStatus } from '../../index.js'
import { useChatBubble } from '../../../../composables/useChatBubble.js'
import { useMarkdown } from '../../../../composables/useMarkdown.js'

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

// 使用聊天气泡工具函数
const { 
  getNodeLabel,
  parseToolExecutions,
  extractNonToolContent
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

// 使用Markdown组合式函数
const { renderMarkdown } = useMarkdown()

// 解析Markdown内容
const parsedContent = computed(() => {
  const content = contentWithoutTools.value
  if (!content) return ''
  
  try {
    console.log('AgentMessage解析Markdown内容:', content);
    // 使用Markdown插件解析
    const result = renderMarkdown(content);
    console.log('AgentMessage解析结果:', result);
    return result;
  } catch (error) {
    console.error('AgentMessage解析Markdown错误:', error);
    return content.replace(/\n/g, '<br>');
  }
});
</script>

<style scoped>
/* 步骤气泡样式 */
</style>