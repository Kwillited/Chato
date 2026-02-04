<template>
  <!-- 传统消息内容气泡（兼容旧格式） -->
  <div 
    v-if="formattedContent || messageValue.error || messageValue.isTyping"
    :class="bubbleClasses"
  >
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
</template>

<script setup>
import { computed } from 'vue'
import { Loading } from '../../index.js'
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
  formattedContent, 
  updateKey,
  copyMessageContent
} = useChatBubble(props)

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
/* 错误提示样式 */
.chat-error {
  color: #ef4444;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}
</style>