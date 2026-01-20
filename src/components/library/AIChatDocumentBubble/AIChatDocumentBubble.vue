<template>
  <div class="w-full max-w-2xl bg-transparent dark:bg-transparent rounded-xl p-4 overflow-hidden">
    <div class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="formattedContent"></div>
    
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
    />
  </div>
</template>

<script setup>
import Loading from '../../common/Loading.vue'
// 导入聊天气泡公共逻辑
import { useChatBubble } from '../../../composables/useChatBubble.js'

const props = defineProps({
  message: {
    type: [Object, Function], // 支持普通对象和ref包装的对象
    required: true,
    default: () => ({})
  }
})

// 使用公共聊天气泡逻辑
const { 
  messageValue, 
  formattedContent 
} = useChatBubble(props)
</script>

<style scoped>
/* 深色模式切换过渡效果 */
.bg-transparent.dark\:bg-transparent,
.markdown-content {
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 错误提示样式 */
.chat-error {
  color: #ef4444;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}
</style>