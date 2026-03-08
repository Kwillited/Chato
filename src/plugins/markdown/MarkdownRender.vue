<script>
import { ref, computed, watch, onMounted, h, defineComponent } from 'vue'
import { createMarkdownPlugin } from './renderer.js'
import CodeBlock from './components/CodeBlock.vue'

export default defineComponent({
  name: 'MarkdownRender',
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
    // 创建渲染实例
    const markdownRenderer = createMarkdownPlugin(props.config)

    // 缓存上次的内容和解析结果
    const lastContent = ref('')
    const cachedVNodes = ref([])

    // 解析 Markdown 为 VNode 树
    const parseMarkdownToVNodes = (content) => {
      if (!content) return []
      
      try {
        // 解析为 AST
        const ast = markdownRenderer.parseToAst(content)
        const vnodes = []
        
        ast.forEach((node, index) => {
          const nodeKey = `${node.type}-${index}`
          
          if (node.type === 'code') {
            // 使用 CodeBlock 组件，对于 mermaid 语言添加 isMermaid 属性
            vnodes.push(h(CodeBlock, {
              key: nodeKey,
              code: node.text,
              language: node.lang || 'plaintext',
              isMermaid: node.lang === 'mermaid'
            }))
          } else if (node.type === 'heading') {
            // 处理标题
            vnodes.push(h(`h${node.depth}`, { key: nodeKey }, node.text))
          } else if (node.type === 'paragraph') {
            // 处理段落
            vnodes.push(h('p', { key: nodeKey }, node.text))
          } else if (node.type === 'list') {
            // 处理列表
            const listItems = node.items.map((item, itemIndex) => {
              return h('li', { key: `${nodeKey}-item-${itemIndex}` }, item.text)
            })
            vnodes.push(h(node.ordered ? 'ol' : 'ul', { key: nodeKey }, listItems))
          } else if (node.type === 'blockquote') {
            // 处理引用
            vnodes.push(h('blockquote', { key: nodeKey }, node.text))
          } else if (node.type === 'hr') {
            // 处理水平线
            vnodes.push(h('hr', { key: nodeKey }))
          } else if (node.type === 'html') {
            // 处理 HTML
            // 创建一个临时容器来解析 HTML
            const parser = new DOMParser()
            const doc = parser.parseFromString(node.text, 'text/html')
            const root = doc.body
            
            // 递归转换 DOM 节点
            const convertNode = (domNode, nodeIndex) => {
              if (domNode.nodeType === Node.TEXT_NODE) {
                return domNode.textContent
              } else if (domNode.nodeType === Node.ELEMENT_NODE) {
                const props = {}
                
                // 处理属性
                for (let i = 0; i < domNode.attributes.length; i++) {
                  const attr = domNode.attributes[i]
                  props[attr.name] = attr.value
                }
                
                // 添加 key
                props.key = `${nodeKey}-html-${nodeIndex}`
                
                // 处理子节点
                const children = Array.from(domNode.childNodes).map((child, childIndex) => 
                  convertNode(child, `${nodeIndex}-${childIndex}`)
                ).filter(child => child !== null && child !== '')
                
                // 创建 VNode
                return h(domNode.tagName.toLowerCase(), props, children)
              }
              return null
            }
            
            // 转换根节点的所有子节点
            const children = Array.from(root.childNodes).map((child, index) => 
              convertNode(child, index)
            ).filter(child => child !== null && child !== '')
            vnodes.push(...children)
          } else if (node.type === 'text') {
            // 处理文本
            if (node.text.trim()) {
              vnodes.push(node.text)
            }
          }
          // 处理其他类型的节点...
        })
        
        return vnodes
      } catch (error) {
        console.warn('Markdown 解析失败:', error)
        // 解析失败时返回原始内容作为文本
        return [content]
      }
    }

    // 计算 VNode 树
    const vnodeTree = computed(() => {
      // 检查内容是否有变化
      if (props.content === lastContent.value && cachedVNodes.value.length > 0) {
        return h('div', { class: 'markdown-render' }, cachedVNodes.value)
      }
      
      // 内容变化或首次渲染，重新解析
      const vnodes = parseMarkdownToVNodes(props.content)
      cachedVNodes.value = vnodes
      lastContent.value = props.content
      
      return h('div', { class: 'markdown-render' }, vnodes)
    })

    // 组件挂载时处理
    onMounted(() => {
      // 初始渲染后处理
      setTimeout(() => {
        // 处理代码高亮
        if (props.config.highlight && typeof hljs !== 'undefined') {
          const codeElements = document.querySelectorAll('code[class^="language-"]')
          codeElements.forEach(element => {
            hljs.highlightElement(element)
          })
        }
      }, 0)
    })

    // 监听内容变化，处理代码高亮
    watch(() => props.content, () => {
      setTimeout(() => {
        // 处理代码高亮
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
    return this.vnodeTree || h('div', { class: 'markdown-render' })
  }
})
</script>

<style scoped>
.markdown-render {
  /* 基础样式 */
  line-height: 1.6;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  padding: 1em;
}
</style>

<style>
/* 导入全局 Markdown 样式 */
@import './styles/markdown-styles.css';
</style>