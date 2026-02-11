<template>
  <!-- 用户消息气泡 - 保持气泡样式 -->
  <UserBubbleStyle 
    :message="message"
    @editMessage="handleEditMessage"
  />
</template>

<script setup>
import { computed } from 'vue'
import UserBubbleStyle from './styles/UserBubbleStyle.vue'

const props = defineProps({
  message: {
    type: [Object, Function],
    required: true,
    default: () => ({})
  },
  chatStyle: {
    type: String,
    default: 'bubble'
  }
})

const emit = defineEmits(['editMessage'])

// 处理编辑消息事件
const handleEditMessage = (editData) => {
  emit('editMessage', editData)
}
</script>

<style scoped>
/* 全局样式已在外部引入 */
/* 这里可以添加组件特定的样式 */
</style>