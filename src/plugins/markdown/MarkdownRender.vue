<script>
import { ref, computed, watch, onMounted, h, defineComponent } from 'vue'
import { createMarkdownPlugin } from './renderer.js'
import MermaidCodeBlock from './components/MermaidCodeBlock.vue'
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

    // 解析 Markdown 为 VNode 树
    const parseMarkdownToVNodes = (content) => {
      if (!content) return []
      
      try {
        // 解析为 AST
        const ast = markdownRenderer.parseToAst(content)
        const vnodes = []
        
        ast.forEach(node => {
          if (node.type === 'code') {
            if (node.lang === 'mermaid') {
              // 使用 MermaidCodeBlock 组件
              vnodes.push(h(MermaidCodeBlock, { code: node.text }))
            } else {
              // 使用 CodeBlock 组件
              vnodes.push(h(CodeBlock, {
                code: node.text,
                language: node.lang || 'plaintext'
              }))
            }
          } else if (node.type === 'heading') {
            // 处理标题
            vnodes.push(h(`h${node.depth}`, node.text))
          } else if (node.type === 'paragraph') {
            // 处理段落
            vnodes.push(h('p', node.text))
          } else if (node.type === 'list') {
            // 处理列表
            const listItems = node.items.map(item => {
              return h('li', item.text)
            })
            vnodes.push(h(node.ordered ? 'ol' : 'ul', listItems))
          } else if (node.type === 'blockquote') {
            // 处理引用
            vnodes.push(h('blockquote', node.text))
          } else if (node.type === 'hr') {
            // 处理水平线
            vnodes.push(h('hr'))
          } else if (node.type === 'html') {
            // 处理 HTML
            // 创建一个临时容器来解析 HTML
            const parser = new DOMParser()
            const doc = parser.parseFromString(node.text, 'text/html')
            const root = doc.body
            
            // 递归转换 DOM 节点
            const convertNode = (domNode) => {
              if (domNode.nodeType === Node.TEXT_NODE) {
                return domNode.textContent
              } else if (domNode.nodeType === Node.ELEMENT_NODE) {
                const props = {}
                
                // 处理属性
                for (let i = 0; i < domNode.attributes.length; i++) {
                  const attr = domNode.attributes[i]
                  props[attr.name] = attr.value
                }
                
                // 处理子节点
                const children = Array.from(domNode.childNodes).map(convertNode).filter(child => child !== null && child !== '')
                
                // 创建 VNode
                return h(domNode.tagName.toLowerCase(), props, children)
              }
              return null
            }
            
            // 转换根节点的所有子节点
            const children = Array.from(root.childNodes).map(convertNode).filter(child => child !== null && child !== '')
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
      const vnodes = parseMarkdownToVNodes(props.content)
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

/* 可以添加更多样式 */
.markdown-render h1,
.markdown-render h2,
.markdown-render h3 {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

.markdown-render p {
  margin-bottom: 1em;
}

.markdown-render ul,
.markdown-render ol {
  margin-bottom: 1em;
  padding-left: 2em;
}

.markdown-render blockquote {
  border-left: 4px solid #ddd;
  padding-left: 1em;
  margin: 1em 0;
  color: #666;
}

.markdown-render hr {
  border: none;
  border-top: 1px solid #ddd;
  margin: 1.5em 0;
}
</style>