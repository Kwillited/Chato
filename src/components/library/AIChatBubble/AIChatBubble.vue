<template>
  <!-- 文档模式样式 -->
  <div v-if="chatStyleDocument" class="w-full group">
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
    
    <!-- 消息内容气泡 -->
    <div v-if="formattedContent || messageValue.error || messageValue.isTyping" class="rounded-lg px-5 py-4 overflow-hidden w-full">
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
    <div v-if="!messageValue.isTyping && (formattedContent || messageValue.thinking || messageValue.error)" class="text-sm text-gray-500 dark:text-gray-400 mt-2 flex items-center justify-between px-5">
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
  
  <!-- 默认气泡样式 -->
  <div v-else class="flex items-start max-w-[85%]">
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
      
      <!-- 消息内容气泡 -->
      <div v-if="formattedContent || messageValue.error || messageValue.isTyping" :class="[
        messageValue.event === 'on_chat_model_stream' 
          ? 'bg-blue-50 dark:bg-blue-900/20 rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-blue-800/30 overflow-hidden'
          : 'bg-white dark:bg-dark-bg-tertiary rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-dark-border overflow-hidden',
        'w-fit',
        'max-w-full'
      ]">
        <!-- 事件类型标签 -->
        <div v-if="messageValue.event" class="text-xs text-blue-500 dark:text-blue-400 mb-1 font-medium">
          {{ getEventLabel(messageValue.event) }}
        </div>
        
        <div class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="formattedContent" :key="updateKey"></div>
        
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
      
      <!-- 时间戳和操作按钮 -->
      <div v-if="!messageValue.isTyping && (formattedContent || messageValue.thinking || messageValue.error)" class="text-sm text-gray-500 dark:text-gray-400 mt-3 ml-3 flex items-center justify-between">
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
import { ref, computed } from 'vue'
import { Tooltip } from '../index.js'
import Loading from '../../common/Loading.vue'
// 导入公共工具函数
import { formatTime } from '../../../utils/time.js'
// 导入聊天气泡公共逻辑
import { useChatBubble } from '../../../composables/useChatBubble.js'

const props = defineProps({
  message: {
    type: [Object, Function], // 支持普通对象和ref包装的对象
    required: true,
    default: () => ({})
  },
  chatStyleDocument: {
    type: Boolean,
    default: false
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
import { watch, onMounted, nextTick } from 'vue'

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

// 获取事件类型标签
const getEventLabel = (event) => {
  const eventLabels = {
    'on_chat_model_stream': 'AI 模型流',
    'on_chat_model_end': 'AI 模型结束',
    'text': '文本消息',
    'tool_call': '工具调用',
    'tool_response': '工具响应'
  }
  return eventLabels[event] || event
}
</script>

<style scoped>
/* 深色模式切换过渡效果 */
.bg-white.dark\:bg-gray-800,
.dark\:border.dark\:border-gray-700,
.markdown-content {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

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