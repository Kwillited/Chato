<template>
  <div class="markdown-content" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'
import { useMarkdown } from '../composables/useMarkdown.js'

const props = defineProps({
  content: {
    type: String,
    default: ''
  }
})

const { renderMarkdown } = useMarkdown()

const renderedContent = computed(() => {
  return renderMarkdown(props.content)
})
</script>

<style scoped>
/* 组件特定样式可以在这里添加 */
</style>
