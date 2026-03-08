<template>
  <div class="code-container">
    <div class="code-header">
      <span class="code-language">{{ language }}</span>
      <button 
        class="copy-code-btn"
        :data-code-block-id="codeBlockId"
        title="复制代码"
        @click="copyCode"
      >
        <i class="fa-solid fa-copy"></i>
      </button>
    </div>
    <pre><code :class="`language-${language}`" :id="codeBlockId">{{ code }}</code></pre>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  code: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'plaintext'
  }
})

const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

const copyCode = () => {
  navigator.clipboard.writeText(props.code)
}

// 处理代码高亮
const handleHighlight = () => {
  if (typeof hljs !== 'undefined') {
    const codeElement = document.getElementById(codeBlockId)
    if (codeElement) {
      hljs.highlightElement(codeElement)
    }
  }
}

onMounted(() => {
  // 延迟处理，确保 DOM 已更新
  setTimeout(handleHighlight, 100)
})

// 当代码变化时重新高亮
watch(() => props.code, () => {
  setTimeout(handleHighlight, 100)
})
</script>

<style scoped>
.code-container {
  margin: 1em 0;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f5f5;
  padding: 0.5em 1em;
  border-bottom: 1px solid #e0e0e0;
}

.code-language {
  font-size: 0.85em;
  font-weight: 600;
  color: #666;
}

.copy-code-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25em;
  border-radius: 4px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.copy-code-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

pre {
  background-color: #f5f5f5;
  margin: 0;
  padding: 1em;
  overflow-x: auto;
}

code {
  background-color: transparent;
  padding: 0;
  font-family: 'Courier New', Courier, monospace;
}
</style>