<template>
  <div v-if="message" :id="id">
    <!-- 默认样式 -->
    <div v-if="chatStyle !== 'document'" class="flex" :class="{ 'justify-end': isUserMessage }">
      <!-- AI消息气泡 -->
      <AIChatBubble 
        v-if="!isUserMessage" 
        :message="message" 
        :chatStyle="chatStyle"
      />
      
      <!-- 用户消息气泡 -->
      <UserChatBubble 
        v-else 
        :message="message" 
        :chatStyle="chatStyle"
        @editMessage="handleEditMessage"
      />
    </div>
    
    <!-- 文档模式样式 -->
    <div v-else>
      <!-- AI消息气泡 - 使用文档样式 -->
      <div v-if="!isUserMessage" class="mb-4 w-full">
        <AIChatBubble 
          :message="message" 
          :chatStyle="chatStyle"
        />
      </div>
      
      <!-- 用户消息气泡 - 保持气泡样式 -->
      <div v-else class="flex justify-end mb-4 w-full">
        <UserChatBubble 
          :message="message" 
          :chatStyle="'bubble'"
          @editMessage="handleEditMessage"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AIChatBubble from '../library/chat/AIChatBubble.vue'
import UserChatBubble from '../library/chat/UserChatBubble.vue'

const props = defineProps({
  message: {
    type: [Object, Function], // 支持普通对象和ref包装的对象
    required: true,
    default: () => ({})
  },
  chatStyle: {
    type: String,
    default: 'bubble'
  },
  id: {
    type: String,
    default: ''
  }
})

// 访问ref包装的消息对象
const messageValue = computed(() => {
  // 如果是ref包装的对象，通过value访问，否则直接返回
  return props.message?.value || props.message || {}
})

// 判断是否为用户消息
const isUserMessage = computed(() => {
  return messageValue.value.role === 'user' || messageValue.value.isUser
})

// 编辑消息（用户消息）
const handleEditMessage = (editData) => {
  // 发射编辑事件给父组件处理
  emit('editMessage', editData)
}

// 定义发射事件
const emit = defineEmits(['editMessage'])
</script>

<style scoped>
/* 全局样式已在外部引入 */
/* 这里可以添加组件特定的样式 */

/* 错误提示样式 */
.chat-error {
  color: #ef4444;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}

/* markdown内容样式 */
.markdown-content {
  transition: color 0.3s ease;
}
</style>
