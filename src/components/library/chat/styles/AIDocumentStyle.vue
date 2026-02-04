<template>
  <!-- 文档模式样式 -->
  <div class="w-full group">
    <!-- 思考内容 -->
    <div v-if="messageValue.thinking" class="relative mb-3">
      <div class="bg-transparent border border-dashed border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 overflow-hidden transition-all duration-300 ease-in-out w-full">
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
    
    <!-- 基于step的工具执行状态会在步骤内部渲染 -->
    
    <!-- 兼容旧格式的工具执行状态（当没有steps时显示） -->
    <div v-if="!messageValue.steps && messageValue.toolExecutions && messageValue.toolExecutions.length > 0" class="space-y-3">
      <ToolExecutionStatus 
        v-for="(tool, index) in messageValue.toolExecutions" 
        :key="index"
        :tool="tool"
        containerClass="w-full"
      />
    </div>
    
    <!-- 兼容旧格式的工具执行状态（当没有steps时显示） -->
    <div v-else-if="!messageValue.steps && (messageValue.status === 'tool_executing' || messageValue.status === 'tool_executed') && messageValue.currentTool" class="relative mb-3">
      <ToolExecutionStatus 
        :messageStatus="messageValue.status"
        :currentTool="messageValue.currentTool"
        :toolInput="messageValue.toolInput"
        containerClass="w-full"
      />
    </div>
    
    <!-- 智能体等待状态 -->
    <div v-if="messageValue.status === 'agent_waiting'" class="relative mb-3">
      <div class="bg-transparent border border-dashed border-purple-300 dark:border-purple-600 rounded-lg px-4 py-2 overflow-hidden transition-all duration-300 ease-in-out w-full">
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
    <div v-if="messageValue.steps && messageValue.steps.length > 0 || messageValue.message_type === 'agent'" class="space-y-4 mt-3">
      <div 
        v-for="step in messageValue.steps" 
        :key="step.step" 
        class="rounded-lg px-5 py-4 overflow-hidden w-full"
      >
        <!-- 步骤标签 -->
        <div class="text-xs text-blue-500 dark:text-blue-400 mb-2 font-medium">
          步骤 {{ step.step }}: {{ getNodeLabel(step.node) }}
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
          :containerClass="`w-full mt-3${index > 0 ? ' mt-2' : ''}`"
        />
        
        <!-- 步骤内容 -->
        <div v-if="step.content" class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="step.content"></div>
      </div>
    </div>
    
    <!-- 普通AI消息 -->
    <div v-else-if="formattedContent || messageValue.error || messageValue.isTyping" class="rounded-lg px-5 py-4 overflow-hidden w-full mt-3">
      <div class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="formattedContent" :key="updateKey"></div>
      
      <!-- 错误状态显示 -->
      <div v-if="messageValue.error" class="chat-error mt-2">
        <i class="fa-solid fa-circle-exclamation text-red-500 mr-1"></i>
        <span>{{ messageValue.error }}</span>
      </div>
      
      <!-- 旋转动画 -->
      <Loading 
        v-if="messageValue.isTyping" 
        type="spin" 
        size="small" 
        color="var(--text-color-secondary, #9ca3af)" 
        containerClass="mt-2"
      />
    </div>
    
    <!-- 模型名称、时间戳和操作按钮 -->
    <div v-if="!messageValue.isTyping && (formattedContent || messageValue.thinking || messageValue.error || messageValue.status === 'tool_executed')" class="text-sm text-gray-500 dark:text-gray-400 mt-2 flex items-center justify-between px-5">
      <span>
        <!-- 模型名称+时间 -->
        {{ messageValue.model || 'Chato' }} - {{ formatTime(messageValue.timestamp || messageValue.time) }}
      </span>
      <div class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <Tooltip content="复制消息内容">
          <button class="copy-btn text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-full transition-all duration-200" @click="copyMessageContent">
            <i class="fa-solid fa-copy"></i>
          </button>
        </Tooltip>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { Tooltip, ToolExecutionStatus, Loading } from '../../index.js'
import { useChatBubble } from '../../../../composables/useChatBubble.js'
import { formatTime } from '../../../../utils/time.js'

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

// 思考内容展开状态 - 流式渲染时默认展开，历史消息默认折叠
const isThinkingExpanded = ref(false)

// 初始化时检查思考内容
const initThinkingExpanded = () => {
  // 检查消息中的思考内容和状态
  const message = props.message?.value || props.message || {}
  // 历史消息默认折叠，流式渲染默认展开
  if (message.thinking) {
    // 只有当消息状态是 "streaming" 时才默认展开
    // 其他所有情况（包括历史消息）都默认折叠
    if (message.status === 'streaming') {
      isThinkingExpanded.value = true
    } else {
      isThinkingExpanded.value = false
    }
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 使用 nextTick 确保消息数据已经完全加载
  nextTick(() => {
    initThinkingExpanded()
  })
})

// 监听消息变化，检查思考内容完成标志
watch(() => props.message, (newMessage) => {
  // 检查新消息中的思考内容完成标志
  const message = newMessage?.value || newMessage || {}
  if (message.thinkingCompleted === true) {
    isThinkingExpanded.value = false
  }
  // 检查新消息状态和思考内容
  if (message.thinking) {
    // 只有流式渲染的消息才展开
    if (message.status === 'streaming') {
      isThinkingExpanded.value = true
    } else {
      isThinkingExpanded.value = false
    }
  }
}, { deep: true })

// 切换思考内容展开/折叠状态
const toggleThinkingExpanded = () => {
  isThinkingExpanded.value = !isThinkingExpanded.value
}

// 计算思考内容的高度类名
const thinkingContentHeightClass = computed(() => {
  return isThinkingExpanded.value ? '' : 'max-h-10'
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
/* 确保操作按钮组的容器是相对定位，以便提示框可以绝对定位 */
.copy-btn {
  position: relative;
}

/* 错误提示样式 */
.chat-error {
  color: #ef4444;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}
</style>