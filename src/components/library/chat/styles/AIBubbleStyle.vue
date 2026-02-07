<template>
  <div class="flex items-start max-w-[85%]">
    <!-- 头像 -->
    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
      <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707-.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
      </svg>
    </div>
    <div class="relative group">
      <!-- 模型名称 -->
      <div class="text-xs text-gray-500 dark:text-gray-400 mb-1 ml-1">{{ messageValue.model || 'Chato' }}</div>
      
      <!-- 思考内容 -->
      <div v-if="messageValue.thinking" class="relative mb-2">
        <div :class="[
          'bg-transparent border border-dashed border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 overflow-hidden transition-all duration-300 ease-in-out',
          'w-fit',
          'max-w-full'
        ]">
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-start gap-2 flex-1">
              <svg class="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707-.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
              <div 
                :class="[
                  'text-xs text-gray-500 dark:text-gray-400 leading-relaxed italic transition-all duration-300 ease-in-out overflow-hidden',
                  thinkingContentHeightClass
                ]"
                v-html="formatThinkingContent(messageValue.thinking)"
              ></div>
            </div>
            <button 
              @click="toggleThinkingExpanded" 
              class="flex-shrink-0 w-5 h-5 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-all duration-300 ease-in-out"
              :class="{ 'rotate-180': !isThinkingExpanded }"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 兼容旧格式的工具执行状态（当没有steps时显示） -->
      <div v-if="!messageValue.steps && messageValue.toolExecutions && messageValue.toolExecutions.length > 0" class="space-y-2">
        <ToolExecutionStatus 
          v-for="(tool, index) in messageValue.toolExecutions" 
          :key="index"
          :tool="tool"
          containerClass="w-fit max-w-full"
        />
      </div>
      
      <!-- 兼容旧格式的工具执行状态（当没有steps时显示） -->
      <div v-else-if="!messageValue.steps && (messageValue.status === 'tool_executing' || messageValue.status === 'tool_executed') && messageValue.currentTool" class="relative mb-2">
        <ToolExecutionStatus 
          :messageStatus="messageValue.status"
          :currentTool="messageValue.currentTool"
          :toolInput="messageValue.toolInput"
          containerClass="w-fit max-w-full"
        />
      </div>
      
      <!-- 智能体等待状态 -->
      <div v-if="messageValue.status === 'agent_waiting'" class="relative mb-2">
        <div :class="[
          'bg-transparent border border-dashed rounded-lg px-4 py-2 overflow-hidden transition-all duration-300 ease-in-out',
          'w-fit',
          'max-w-full',
          'border-purple-300 dark:border-purple-600'
        ]">
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-start gap-2 flex-1">
              <svg class="w-4 h-4 text-purple-500 dark:text-purple-400 mt-0.5 flex-shrink-0 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <div class="text-xs text-purple-500 dark:text-purple-400 leading-relaxed">
                <div class="font-medium">智能体处理中</div>
                <div class="mt-1 text-gray-500 dark:text-gray-400">正在执行智能体流程，请稍候...</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Agent消息 -->
      <AgentMessage 
        v-if="messageValue.steps && messageValue.steps.length > 0 || messageValue.message_type === 'agent' || messageValue.agent_step !== undefined"
        :message="message"
      />
      
      <!-- 普通AI消息 -->
      <NormalAIMessage 
        v-else
        :message="message"
        containerClass="mt-2"
      />
      
      <!-- 时间戳和操作按钮 -->
      <div v-if="!messageValue.isTyping && (formattedContent || messageValue.thinking || messageValue.error || messageValue.status === 'tool_executed' || messageValue.content || messageValue.text)" class="text-sm text-gray-500 dark:text-gray-400 mt-3 ml-3 flex items-center justify-between">
        <span>{{ formatTime(messageValue.timestamp || messageValue.time) }}</span>
        <div class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <Tooltip content="复制消息内容">
            <button class="copy-btn text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-full transition-all duration-200" @click="copyMessageContent">
              <i class="fa-solid fa-copy"></i>
            </button>
          </Tooltip>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Tooltip, ToolExecutionStatus } from '../../index.js'
import NormalAIMessage from '../AIChat/NormalAIMessage.vue'
import AgentMessage from '../AIChat/AgentMessage.vue'
import { formatTime } from '../../../../utils/time.js'
import { useChatBubble } from '../../../../composables/useChatBubble.js'
import { useChatBubbleUtils } from '../../../../composables/useChatBubbleUtils.js'

const props = defineProps({
  message: {
    type: [Object, Function],
    required: true,
    default: () => ({})
  }
})

// 使用公共聊天气泡逻辑
const { 
  messageValue, 
  formattedContent, 
  updateKey, 
  copyMessageContent,
  formatThinkingContent
} = useChatBubble(props)

// 使用聊天气泡工具函数
const { 
  isThinkingExpanded,
  toggleThinkingExpanded,
  thinkingContentHeightClass
} = useChatBubbleUtils(props)
</script>

<style scoped>
/* 确保操作按钮组的容器是相对定位，以便提示框可以绝对定位 */
.copy-btn {
  position: relative;
}

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

/* AI 聊天气泡样式 */
.ai-message-bubble {
  background-color: var(--chat-bubble-ai-bg);
  border: 1px solid var(--chat-bubble-ai-border);
  border-radius: var(--chat-bubble-ai-border-radius);
  box-shadow: var(--chat-bubble-ai-shadow);
  transition: all 0.3s ease;
}

.ai-message-bubble:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
}

/* 用户聊天气泡样式 */
.user-message-bubble {
  background-color: var(--chat-bubble-user-bg);
  color: var(--chat-bubble-user-color);
  border-radius: var(--chat-bubble-user-border-radius);
  box-shadow: var(--chat-bubble-user-shadow);
  transition: all 0.3s ease;
}

.user-message-bubble:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(79, 70, 229, 0.3);
}

/* 思考内容样式 */
.thinking-content {
  background-color: var(--thinking-bg);
  border-left: 4px solid var(--thinking-border);
  border-radius: var(--thinking-border-radius);
  padding: var(--thinking-padding);
  box-shadow: var(--thinking-shadow);
  margin: 8px 0;
  font-size: 14px;
}

/* 工具执行状态样式 */
.tool-execution-status {
  background-color: var(--tool-execution-bg);
  border: 1px solid var(--tool-execution-border);
  border-radius: var(--tool-execution-border-radius);
  padding: var(--tool-execution-padding);
  margin: 8px 0;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .ai-message-bubble {
    background-color: var(--dark-chat-bubble-ai-bg);
    border-color: var(--dark-chat-bubble-ai-border);
    box-shadow: var(--dark-chat-bubble-ai-shadow);
  }
  
  .user-message-bubble {
    background-color: var(--dark-chat-bubble-user-bg);
    color: var(--dark-chat-bubble-user-color);
    box-shadow: var(--dark-chat-bubble-user-shadow);
  }
  
  .thinking-content {
    background-color: var(--dark-thinking-bg);
    border-color: var(--dark-thinking-border);
  }
  
  .tool-execution-status {
    background-color: var(--dark-tool-execution-bg);
    border-color: var(--dark-tool-execution-border);
  }
  
  .chat-error {
    background-color: var(--dark-error-bg);
    border-color: var(--dark-error-border);
  }
}
</style>