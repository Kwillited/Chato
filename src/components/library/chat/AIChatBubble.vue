<template>
  <!-- 文档模式样式 -->
  <AIDocumentStyle 
    v-if="chatStyle === 'document'"
    :message="message"
  />
  
  <!-- 默认气泡样式 -->
  <AIBubbleStyle 
    v-else
    :message="message"
  />
</template>

<script setup>
import AIBubbleStyle from './styles/AIBubbleStyle.vue'
import AIDocumentStyle from './styles/AIDocumentStyle.vue'

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
</script>

<style scoped>
/* 全局样式已在外部引入 */
/* 这里可以添加组件特定的样式 */
</style>