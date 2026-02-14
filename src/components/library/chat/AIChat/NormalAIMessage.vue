<template>
  <!-- 传统消息内容气泡（兼容旧格式） -->
  <div 
    v-if="messageContent || localMessageValue.error || localMessageValue.isTyping"
    :class="bubbleClasses"
  >
    <!-- 事件类型标签 -->
    <div v-if="localMessageValue.event" class="text-xs text-blue-500 dark:text-blue-400 mb-1 font-medium">
      {{ getEventLabel(localMessageValue.event) }}
    </div>
    
    <div class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="parsedContent" :key="updateKey"></div>
    
    <!-- 错误状态显示 -->
    <div v-if="localMessageValue.error" class="chat-error mt-2">
      <i class="fa-solid fa-circle-exclamation text-red-500 mr-1"></i>
      <span>{{ localMessageValue.error }}</span>
    </div>
    
    <!-- 打字动画 -->
    <Loading 
      v-if="localMessageValue.isTyping" 
      type="typing" 
      size="small" 
      color="var(--text-color-secondary, #9ca3af)" 
      containerClass="mt-2"
      v-memo="[localMessageValue.isTyping]"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import { Loading } from '../../index.js'
import { useChatBubbleUtils } from '../../../../composables/useChatBubbleUtils.js'

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

// 直接处理消息对象
const localMessageValue = computed(() => {
  const message = props.message?.value || props.message || {}
  return {
    id: message.id || '',
    role: message.role || 'ai',
    content: message.content || message.text || '',
    timestamp: message.timestamp || Date.now(),
    error: message.error || '',
    isTyping: message.isTyping || false,
    lastUpdate: message.lastUpdate || Date.now(),
    event: message.event || '',
    ...message
  }
})

// 获取消息内容
const messageContent = computed(() => {
  return localMessageValue.value.content || localMessageValue.value.text || ''
})

// 用于触发更新的key值
const updateKey = computed(() => {
  return `${messageContent.value.length}-${localMessageValue.value.lastUpdate || Date.now()}`
})

// 使用marked函数解析Markdown
const parsedContent = computed(() => {
  const content = messageContent.value
  if (!content) return ''
  
  try {
    console.log('解析Markdown内容:', content);
    const result = marked(content);
    console.log('解析结果:', result);
    return result;
  } catch (error) {
    console.error('解析Markdown错误:', error);
    return content.replace(/\n/g, '<br>');
  }
});

// 使用聊天气泡工具函数
const { 
  getEventLabel
} = useChatBubbleUtils({ message: props.message })

// 计算气泡样式类
const bubbleClasses = computed(() => {
  return [
    localMessageValue.value.event === 'on_chat_model_stream' 
      ? 'bg-blue-50 dark:bg-blue-900/20 rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-blue-800/30 overflow-hidden'
      : 'bg-gray-200 dark:bg-dark-500 rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-dark-border overflow-hidden',
    'w-fit',
    'max-w-full',
    props.containerClass
  ]
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