<template>
  <div class="chato-renderer-content">
    <!-- 内容将通过 render 函数动态生成 -->
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, h, defineComponent } from 'vue'
import { createChatoRenderer } from './renderer.js'
import { 
  handleCodeNode, 
  handleHeadingNode, 
  handleParagraphNode, 
  handleListNode, 
  handleBlockquoteNode, 
  handleHrNode, 
  handleHtmlNode, 
  handleTableNode, 
  handleTextNode 
} from './utils/nodeHandlers.js'

export default defineComponent({
  name: 'ChatoRenderer',
  props: {
    content: {
      type: String,
      default: ''
    },
    config: {
      type: Object,
      default: () => ({
        breaks: true,
        gfm: true,
        highlight: true,
        copy: true
      })
    }
  },
  setup(props) {
    const markdownRenderer = createChatoRenderer(props.config)
    const lastContent = ref('')
    const cachedVNodes = ref([])

    const parseMarkdownToVNodes = (content) => {
      if (!content) return []
      
      try {
        const ast = markdownRenderer.parseToAst(content)
        const vnodes = []
        
        ast.forEach((node, index) => {
          let nodeVNodes = []
          
          switch (node.type) {
            case 'code':
              nodeVNodes = [handleCodeNode(node, index)]
              break
            case 'heading':
              nodeVNodes = [handleHeadingNode(node, index)]
              break
            case 'paragraph':
              nodeVNodes = handleParagraphNode(node, index)
              break
            case 'list':
              nodeVNodes = [handleListNode(node, index)]
              break
            case 'blockquote':
              nodeVNodes = [handleBlockquoteNode(node, index)]
              break
            case 'hr':
              nodeVNodes = [handleHrNode(node, index)]
              break
            case 'html':
              nodeVNodes = handleHtmlNode(node, index)
              break
            case 'table':
              nodeVNodes = [handleTableNode(node, index)]
              break
            case 'text':
              const textNode = handleTextNode(node, index)
              if (textNode) nodeVNodes = [textNode]
              break
          }
          
          vnodes.push(...nodeVNodes)
        })
        
        return vnodes
      } catch (error) {
        console.warn('Chato Renderer 解析失败:', error)
        return [content]
      }
    }

    const vnodeTree = computed(() => {
      if (props.content === lastContent.value && cachedVNodes.value.length > 0) {
        return h('div', { class: 'chato-renderer-content' }, cachedVNodes.value)
      }
      
      const vnodes = parseMarkdownToVNodes(props.content)
      cachedVNodes.value = vnodes
      lastContent.value = props.content
      
      return h('div', { class: 'chato-renderer-content' }, vnodes)
    })

    onMounted(() => {
      setTimeout(() => {
        if (props.config.highlight && typeof hljs !== 'undefined') {
          const codeElements = document.querySelectorAll('code[class^="language-"]')
          codeElements.forEach(element => {
            hljs.highlightElement(element)
          })
        }
      }, 0)
    })

    watch(() => props.content, () => {
      setTimeout(() => {
        if (props.config.highlight && typeof hljs !== 'undefined') {
          const codeElements = document.querySelectorAll('code[class^="language-"]')
          codeElements.forEach(element => {
            hljs.highlightElement(element)
          })
        }
      }, 0)
    })

    return {
      vnodeTree
    }
  },
  render() {
    return this.vnodeTree || h('div', { class: 'chato-renderer-content' })
  }
})
</script>

<style scoped>
.chato-renderer-content {
  line-height: var(--line-height-base);
  font-family: var(--font-family-base);
  padding: 1em;
}
</style>

<style>
@import './styles/variables.css';
@import './styles/markdown-styles.css';
</style>
