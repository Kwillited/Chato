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

    // 内联标签处理规则
    const inlineRules = {
      strong: (token, key) => h('u', { key }, processInlineTokens(token.tokens, key)),
      em: (token, key) => h('em', { key }, processInlineTokens(token.tokens, key)),
      link: (token, key) => h('a', {
        key,
        href: token.href,
        target: '_blank',
        rel: 'noopener noreferrer'
      }, processInlineTokens(token.tokens, key)),
      code: (token, key) => h('code', { key, class: 'inline-code' }, token.text),
      codespan: (token, key) => h('code', { key, class: 'inline-code' }, token.text),
      image: (token, key) => h('span', { key, class: 'image-wrapper' }, [
        // 加载中状态
        h('span', { class: 'image-loading' }, [
          h('i', { class: 'fa-solid fa-spinner fa-spin' }),
          h('span', '加载中...')
        ]),
        // 图片元素
        h('img', {
          src: token.href,
          alt: token.text || '',
          title: token.title,
          class: 'markdown-image',
          onLoad: (event) => {
            // 加载成功，隐藏加载中状态
            event.target.previousElementSibling.style.display = 'none';
            event.target.style.display = 'block';
          },
          onError: (event) => {
            // 加载失败，隐藏加载中状态，显示错误状态
            event.target.previousElementSibling.style.display = 'none';
            event.target.style.display = 'none';
            event.target.nextElementSibling.style.display = 'flex';
          }
        }),
        // 加载失败状态
        h('span', { class: 'image-error' }, [
          h('i', { class: 'fa-solid fa-image' }),
          h('span', '图片加载失败')
        ])
      ]),
      del: (token, key) => h('del', { key }, processInlineTokens(token.tokens, key)),
      text: (token) => token.text
    }

    // 处理内联标签
    const processInlineTokens = (tokens, parentKey) => {
      if (!tokens || !Array.isArray(tokens)) return []
      
      return tokens.map((token, index) => {
        const tokenKey = `${parentKey}-token-${index}`
        const rule = inlineRules[token.type]
        
        if (rule) {
          return rule(token, tokenKey)
        } else {
          return token.text || ''
        }
      })
    }

    // 解析 Markdown 为 VNode 树
    const parseMarkdownToVNodes = (content) => {
      if (!content) return []
      
      try {
        // 解析为 AST
        const ast = markdownRenderer.parseToAst(content)
        // 打印 AST 结果
        console.log('Markdown AST:', ast)
        console.log('Markdown AST 结构:', JSON.stringify(ast, null, 2))
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
            const headingContent = node.tokens ? processInlineTokens(node.tokens, nodeKey) : node.text
            vnodes.push(h(`h${node.depth}`, { key: nodeKey }, headingContent))
          } else if (node.type === 'paragraph') {
            // 检查段落是否只包含图片
            const onlyImages = node.tokens && Array.isArray(node.tokens) && 
              node.tokens.every(token => 
                token.type === 'image' || 
                (token.type === 'text' && token.text.trim() === '') ||
                token.type === 'br'
              );
            
            if (onlyImages) {
              // 只包含图片，直接渲染图片
              if (node.tokens && Array.isArray(node.tokens)) {
                node.tokens.forEach((token, tokenIndex) => {
                  if (token.type === 'image') {
                    const tokenKey = `${nodeKey}-token-${tokenIndex}`;
                    const imageVNode = inlineRules.image(token, tokenKey);
                    vnodes.push(imageVNode);
                  }
                });
              }
            } else {
              // 包含其他内容，创建p标签
              const paragraphContent = node.tokens ? processInlineTokens(node.tokens, nodeKey) : node.text
              vnodes.push(h('p', { key: nodeKey }, paragraphContent))
            }
          } else if (node.type === 'list') {
            // 处理列表
            const listItems = node.items.map((item, itemIndex) => {
              const itemKey = `${nodeKey}-item-${itemIndex}`
              const itemChildren = []
              
              if (item.tokens && Array.isArray(item.tokens)) {
                item.tokens.forEach((token, tokenIndex) => {
                  const tokenKey = `${itemKey}-token-${tokenIndex}`
                  
                  if (token.type === 'checkbox') {
                    // 处理任务列表的复选框
                    itemChildren.push(h('input', {
                      key: tokenKey,
                      type: 'checkbox',
                      checked: token.checked,
                      disabled: true, // 只读模式
                      class: 'task-checkbox'
                    }))
                    // 添加空格
                    itemChildren.push(' ')
                  } else if (token.type === 'text') {
                    // 处理文本
                    if (token.text) {
                      itemChildren.push(token.text)
                    }
                  } else if (token.type === 'paragraph') {
                    // 处理段落
                    if (token.tokens) {
                      const paragraphContent = processInlineTokens(token.tokens, tokenKey)
                      itemChildren.push(...paragraphContent)
                    } else if (token.text) {
                      itemChildren.push(token.text)
                    }
                  } else if (token.type === 'list') {
                    // 处理嵌套列表
                    const nestedListItems = token.items.map((nestedItem, nestedIndex) => {
                      const nestedItemKey = `${tokenKey}-item-${nestedIndex}`
                      const nestedItemChildren = []
                      
                      if (nestedItem.tokens && Array.isArray(nestedItem.tokens)) {
                        nestedItem.tokens.forEach((nestedToken, nestedTokenIndex) => {
                          const nestedTokenKey = `${nestedItemKey}-token-${nestedTokenIndex}`
                          
                          if (nestedToken.type === 'checkbox') {
                            // 处理嵌套任务列表的复选框
                            nestedItemChildren.push(h('input', {
                              key: nestedTokenKey,
                              type: 'checkbox',
                              checked: nestedToken.checked,
                              disabled: true, // 只读模式
                              class: 'task-checkbox'
                            }))
                            // 添加空格
                            nestedItemChildren.push(' ')
                          } else if (nestedToken.type === 'text') {
                            // 处理文本
                            if (nestedToken.text) {
                              nestedItemChildren.push(nestedToken.text)
                            }
                          } else if (nestedToken.type === 'paragraph') {
                            // 处理嵌套列表中的段落
                            if (nestedToken.tokens) {
                              const nestedParagraphContent = processInlineTokens(nestedToken.tokens, nestedTokenKey)
                              nestedItemChildren.push(...nestedParagraphContent)
                            } else if (nestedToken.text) {
                              nestedItemChildren.push(nestedToken.text)
                            }
                          }
                        })
                      }
                      
                      return h('li', { key: nestedItemKey }, nestedItemChildren)
                    })
                    
                    itemChildren.push(h(token.ordered ? 'ol' : 'ul', { key: tokenKey }, nestedListItems))
                  }
                })
              }
              
              return h('li', { key: itemKey }, itemChildren)
            })
            vnodes.push(h(node.ordered ? 'ol' : 'ul', { key: nodeKey, class: 'task-list' }, listItems))
          } else if (node.type === 'blockquote') {
            // 处理引用
            const blockquoteChildren = []
            
            if (node.tokens && Array.isArray(node.tokens)) {
              node.tokens.forEach((token, tokenIndex) => {
                const tokenKey = `${nodeKey}-token-${tokenIndex}`
                
                if (token.type === 'paragraph') {
                  // 处理引用中的段落
                  const paragraphContent = token.tokens ? processInlineTokens(token.tokens, tokenKey) : token.text
                  blockquoteChildren.push(h('p', { key: tokenKey }, paragraphContent))
                } else if (token.type === 'blockquote') {
                  // 处理嵌套引用
                  const nestedBlockquoteChildren = []
                  
                  if (token.tokens && Array.isArray(token.tokens)) {
                    token.tokens.forEach((nestedToken, nestedIndex) => {
                      const nestedTokenKey = `${tokenKey}-nested-${nestedIndex}`
                      
                      if (nestedToken.type === 'paragraph') {
                        const nestedParagraphContent = nestedToken.tokens ? processInlineTokens(nestedToken.tokens, nestedTokenKey) : nestedToken.text
                        nestedBlockquoteChildren.push(h('p', { key: nestedTokenKey }, nestedParagraphContent))
                      } else {
                        const nestedContent = processInlineTokens([nestedToken], nestedTokenKey)
                        nestedBlockquoteChildren.push(...nestedContent)
                      }
                    })
                  } else if (token.text) {
                    nestedBlockquoteChildren.push(token.text)
                  }
                  
                  blockquoteChildren.push(h('blockquote', { key: tokenKey }, nestedBlockquoteChildren))
                } else {
                  // 处理其他类型的内容
                  const content = processInlineTokens([token], tokenKey)
                  blockquoteChildren.push(...content)
                }
              })
            } else if (node.text) {
              blockquoteChildren.push(node.text)
            }
            
            vnodes.push(h('blockquote', { key: nodeKey }, blockquoteChildren))
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
          } else if (node.type === 'table') {
            // 处理表格
            console.log('表格节点:', node)
            console.log('表格节点结构:', JSON.stringify(node, null, 2))
            const tableKey = `${nodeKey}`
            
            // 创建表格元素
            const tableChildren = []
            
            // 处理表头
            if (node.header && node.header.length > 0) {
              console.log('表头数据:', node.header)
              const theadChildren = []
              const headerRow = h('tr', { key: `${tableKey}-header-row` }, 
                node.header.map((cell, cellIndex) => {
                  const cellContent = cell.tokens ? processInlineTokens(cell.tokens, `${tableKey}-header-${cellIndex}`) : cell.text
                  return h('th', { key: `${tableKey}-header-${cellIndex}` }, cellContent)
                })
              )
              theadChildren.push(headerRow)
              tableChildren.push(h('thead', { key: `${tableKey}-thead` }, theadChildren))
            }
            
            // 处理表体 - 检查可能的属性名
            if (node.cells && node.cells.length > 0) {
              console.log('表体数据 (cells):', node.cells)
              const tbodyChildren = []
              node.cells.forEach((row, rowIndex) => {
                const rowChildren = row.map((cell, cellIndex) => {
                  const cellContent = cell.tokens ? processInlineTokens(cell.tokens, `${tableKey}-cell-${rowIndex}-${cellIndex}`) : cell.text
                  return h('td', { key: `${tableKey}-cell-${rowIndex}-${cellIndex}` }, cellContent)
                })
                tbodyChildren.push(h('tr', { key: `${tableKey}-row-${rowIndex}` }, rowChildren))
              })
              tableChildren.push(h('tbody', { key: `${tableKey}-tbody` }, tbodyChildren))
            } else if (node.body && node.body.length > 0) {
              console.log('表体数据 (body):', node.body)
              const tbodyChildren = []
              node.body.forEach((row, rowIndex) => {
                const rowChildren = row.map((cell, cellIndex) => {
                  const cellContent = cell.tokens ? processInlineTokens(cell.tokens, `${tableKey}-cell-${rowIndex}-${cellIndex}`) : cell.text
                  return h('td', { key: `${tableKey}-cell-${rowIndex}-${cellIndex}` }, cellContent)
                })
                tbodyChildren.push(h('tr', { key: `${tableKey}-row-${rowIndex}` }, rowChildren))
              })
              tableChildren.push(h('tbody', { key: `${tableKey}-tbody` }, tbodyChildren))
            } else if (node.rows && node.rows.length > 0) {
              console.log('表体数据 (rows):', node.rows)
              const tbodyChildren = []
              node.rows.forEach((row, rowIndex) => {
                const rowChildren = row.map((cell, cellIndex) => {
                  const cellContent = cell.tokens ? processInlineTokens(cell.tokens, `${tableKey}-cell-${rowIndex}-${cellIndex}`) : cell.text
                  return h('td', { key: `${tableKey}-cell-${rowIndex}-${cellIndex}` }, cellContent)
                })
                tbodyChildren.push(h('tr', { key: `${tableKey}-row-${rowIndex}` }, rowChildren))
              })
              tableChildren.push(h('tbody', { key: `${tableKey}-tbody` }, tbodyChildren))
            } else {
              console.log('未找到表体数据，节点结构:', node)
            }
            
            vnodes.push(h('table', { key: tableKey, class: 'markdown-table' }, tableChildren))
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

/* 图片容器样式 */
.image-wrapper {
  position: relative;
  display: inline-block;
  margin: 0.5em 0;
  min-width: 150px;
  min-height: 150px;
}

/* 图片样式 */
.markdown-image {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  display: none; /* 初始隐藏，加载成功后显示 */
}

/* 加载中状态样式 */
.image-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 150px;
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
  text-align: center;
  box-sizing: border-box;
}

.image-loading i {
  font-size: 2em;
  margin-bottom: 0.5em;
  color: #999;
}

.image-loading span {
  font-size: 0.9em;
}

/* 加载失败状态样式 */
.image-error {
  position: absolute;
  top: 0;
  left: 0;
  width: 150px;
  height: 150px;
  display: none; /* 初始隐藏，加载失败后显示 */
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
  text-align: center;
  box-sizing: border-box;
}

.image-error i {
  font-size: 2em;
  margin-bottom: 0.5em;
  color: #999;
}

.image-error span {
  font-size: 0.9em;
}
</style>

<style>
/* 导入全局 Markdown 样式 */
@import './styles/markdown-styles.css';
</style>