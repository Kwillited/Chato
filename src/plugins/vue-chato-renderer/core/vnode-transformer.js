import { h } from 'vue'
import CodeBlock from '../components/CodeBlock.vue'
import { processMathFormulasInText } from '../extensions/math-formula.js'
import { parseHtmlString, convertElementToVNode } from '../utils/dom-utils.js'
import { createStructureAnalyzer } from './structure-analyzer.js'

/**
 * VNode 转换器
 * 负责将 AST 节点转换为 Vue VNode，支持增量构建
 */
export class VNodeTransformer {
  constructor() {
    this.inlineRules = this.setupInlineRules()
    this.cache = {
      vnodes: [],
      version: 0,
      structure: null
    }
    this.structureAnalyzer = createStructureAnalyzer()
  }

  /**
   * 设置内联标签处理规则
   * @returns {Object} 内联标签处理规则
   */
  setupInlineRules() {
    return {
      strong: (token, key) => {
        // 根据原始文本判断是下划线还是加粗
        if (token.raw && token.raw.startsWith('__') && token.raw.endsWith('__')) {
          return h('u', { key }, this.processInlineTokens(token.tokens, key))
        } else {
          return h('strong', { key }, this.processInlineTokens(token.tokens, key))
        }
      },
      em: (token, key) => h('em', { key }, this.processInlineTokens(token.tokens, key)),
      u: (token, key) => h('u', { key }, this.processInlineTokens(token.tokens, key)),
      link: (token, key) => h('a', {
        key,
        href: token.href,
        target: '_blank',
        rel: 'noopener noreferrer'
      }, this.processInlineTokens(token.tokens, key)),
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
      del: (token, key) => h('del', { key }, this.processInlineTokens(token.tokens, key)),
      text: (token) => token.text
    }
  }

  /**
   * 处理数学公式文本
   * @param {string} text 文本内容
   * @param {string} tokenKey 令牌键
   * @returns {Array} 处理后的 VNode 数组
   */
  processMathFormulaText(text, tokenKey) {
    const processedParts = processMathFormulasInText(text)
    const result = []
    
    if (processedParts.length > 1 || (processedParts.length === 1 && processedParts[0].includes('katex'))) {
      // 如果文本被处理过，添加处理后的 VNode
      processedParts.forEach((part, partIndex) => {
        if (typeof part === 'string' && part.includes('katex')) {
          // 处理 KaTeX 生成的 HTML，转换为 VNode
          try {
            const htmlElement = parseHtmlString(part)
            if (htmlElement) {
              // 转换 HTML 为 VNode
              const childVNodes = Array.from(htmlElement.childNodes).map((child, childIndex) => 
                convertElementToVNode(child, `${tokenKey}-katex-${partIndex}-${childIndex}`)
              ).filter(child => child !== null && child !== '')
              // 直接添加转换后的 VNode，不添加额外的 span 包裹
              result.push(...childVNodes)
            } else {
              // 解析失败时降级为原始 HTML
              result.push(h('span', {
                key: `${tokenKey}-katex-${partIndex}`,
                innerHTML: part
              }))
            }
          } catch (error) {
            console.error('KaTeX HTML 转换错误:', error)
            // 出错时降级为原始 HTML
            result.push(h('span', {
              key: `${tokenKey}-katex-${partIndex}`,
              innerHTML: part
            }))
          }
        } else {
          result.push(part)
        }
      })
    } else {
      result.push(text)
    }
    
    return result
  }

  /**
   * 处理内联标签
   * @param {Array} tokens 内联令牌
   * @param {string} parentKey 父节点键
   * @returns {Array} 处理后的 VNode 数组
   */
  processInlineTokens(tokens, parentKey) {
    if (!tokens || !Array.isArray(tokens)) return []
    
    // 合并连续的文本节点和转义节点，以便处理跨节点的数学公式
    const mergedTokens = []
    let currentText = ''
    
    tokens.forEach((token, index) => {
      if (token.type === 'text' || token.type === 'br' || token.type === 'escape') {
        if (token.type === 'escape') {
          // 对于转义节点，使用 raw 来保留反斜杠
          currentText += token.raw || ''
        } else {
          currentText += token.text || '\n'
        }
      } else {
        if (currentText) {
          mergedTokens.push({ type: 'text', text: currentText })
          currentText = ''
        }
        mergedTokens.push(token)
      }
    })
    
    if (currentText) {
      mergedTokens.push({ type: 'text', text: currentText })
    }
    
    const result = []
    
    mergedTokens.forEach((token, index) => {
      const tokenKey = `${parentKey}-token-${index}`
      const rule = this.inlineRules[token.type]
      
      if (rule) {
        if (token.type === 'text' && (token.text.includes('$$') || token.text.includes('$') || token.text.includes('\\(') || token.text.includes('\\['))) {
          // 处理包含数学公式的文本
          result.push(...this.processMathFormulaText(token.text, tokenKey))
        } else {
          result.push(rule(token, tokenKey))
        }
      } else {
        if (token.text && (token.text.includes('$$') || token.text.includes('$') || token.text.includes('\\(') || token.text.includes('\\['))) {
          // 处理包含数学公式的文本
          result.push(...this.processMathFormulaText(token.text, tokenKey))
        } else {
          result.push(token.text || '')
        }
      }
    })
    
    return result
  }



  /**
   * 处理列表项的令牌
   * @param {Array} tokens 令牌数组
   * @param {string} itemKey 列表项键
   * @returns {Array} 处理后的子节点数组
   */
  processListItemTokens(tokens, itemKey) {
    const children = []
    
    if (tokens && Array.isArray(tokens)) {
      tokens.forEach((token, tokenIndex) => {
        const tokenKey = `${itemKey}-token-${tokenIndex}`
        
        if (token.type === 'checkbox') {
          // 处理任务列表的复选框
          children.push(h('input', {
            key: tokenKey,
            type: 'checkbox',
            checked: token.checked,
            disabled: true, // 只读模式
            class: 'task-checkbox'
          }))
          // 添加空格
          children.push(' ')
        } else if (token.type === 'text') {
          // 处理文本，直接使用 processInlineTokens 的返回值
          if (token.text) {
            const textContent = this.processInlineTokens(token.tokens, tokenKey)
            children.push(h('p', { 
              key: tokenKey,
              class: 'markdown-paragraph'
            }, textContent))
          }
        } else if (token.type === 'paragraph') {
          // 处理段落，直接使用 processInlineTokens 的返回值
          if (token.tokens) {
            const paragraphContent = this.processInlineTokens(token.tokens, tokenKey)
            children.push(h('p', { 
              key: tokenKey,
              class: 'markdown-paragraph'
            }, paragraphContent))
          } else if (token.text) {
            children.push(h('p', { 
              key: tokenKey,
              class: 'markdown-paragraph'
            }, token.text))
          }
        } else if (token.type === 'list') {
          // 处理嵌套列表
          const nestedListItems = token.items.map((nestedItem, nestedIndex) => {
            const nestedItemKey = `${tokenKey}-item-${nestedIndex}`
            const nestedItemChildren = this.processListItemTokens(nestedItem.tokens, nestedItemKey)
            return h('li', { key: nestedItemKey }, nestedItemChildren)
          })
          
          children.push(h(token.ordered ? 'ol' : 'ul', { key: tokenKey }, nestedListItems))
        }
      })
    }
    
    return children
  }

  /**
   * 转换单个 AST 节点为 VNode
   * @param {Object} node AST 节点
   * @param {string} nodeKey 节点键
   * @returns {VNode|Array} VNode 或 VNode 数组
   */
  convertNodeToVNode(node, nodeKey) {
    if (!node) return null

    if (node.type === 'code') {
      // 使用 CodeBlock 组件，对于 mermaid 语言添加 isMermaid 属性
      return h(CodeBlock, {
        key: nodeKey,
        code: node.text,
        language: node.lang || 'plaintext',
        isMermaid: node.lang === 'mermaid'
      })
    } else if (node.type === 'heading') {
      // 处理标题
      const headingContent = node.tokens ? this.processInlineTokens(node.tokens, nodeKey) : node.text
      return h(`h${node.depth}`, { key: nodeKey }, headingContent)
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
        const imageVNodes = []
        if (node.tokens && Array.isArray(node.tokens)) {
          node.tokens.forEach((token, tokenIndex) => {
            if (token.type === 'image') {
              const tokenKey = `${nodeKey}-token-${tokenIndex}`;
              const imageVNode = this.inlineRules.image(token, tokenKey);
              imageVNodes.push(imageVNode);
            }
          });
        }
        return imageVNodes
      } else {
        // 包含其他内容，创建p标签
        const paragraphContent = node.tokens ? this.processInlineTokens(node.tokens, nodeKey) : node.text
        return h('p', { key: nodeKey }, paragraphContent)
      }
    } else if (node.type === 'list') {
      // 处理列表
      const listItems = node.items.map((item, itemIndex) => {
        const itemKey = `${nodeKey}-item-${itemIndex}`
        const itemChildren = this.processListItemTokens(item.tokens, itemKey)
        return h('li', { key: itemKey }, itemChildren)
      })
      return h(node.ordered ? 'ol' : 'ul', { key: nodeKey, class: 'task-list' }, listItems)
    } else if (node.type === 'blockquote') {
      // 处理引用
      const blockquoteChildren = []
      
      if (node.tokens && Array.isArray(node.tokens)) {
        node.tokens.forEach((token, tokenIndex) => {
          const tokenKey = `${nodeKey}-token-${tokenIndex}`
          
          if (token.type === 'paragraph') {
            // 处理引用中的段落
            const paragraphContent = token.tokens ? this.processInlineTokens(token.tokens, tokenKey) : token.text
            blockquoteChildren.push(h('p', { key: tokenKey }, paragraphContent))
          } else if (token.type === 'blockquote') {
            // 处理嵌套引用
            const nestedBlockquoteChildren = []
            
            if (token.tokens && Array.isArray(token.tokens)) {
              token.tokens.forEach((nestedToken, nestedIndex) => {
                const nestedTokenKey = `${tokenKey}-nested-${nestedIndex}`
                
                if (nestedToken.type === 'paragraph') {
                  const nestedParagraphContent = nestedToken.tokens ? this.processInlineTokens(nestedToken.tokens, nestedTokenKey) : nestedToken.text
                  nestedBlockquoteChildren.push(h('p', { key: nestedTokenKey }, nestedParagraphContent))
                } else {
                  const nestedContent = this.processInlineTokens([nestedToken], nestedTokenKey)
                  nestedBlockquoteChildren.push(...nestedContent)
                }
              })
            } else if (token.text) {
              nestedBlockquoteChildren.push(token.text)
            }
            
            blockquoteChildren.push(h('blockquote', { key: tokenKey }, nestedBlockquoteChildren))
          } else {
            // 处理其他类型的内容
            const content = this.processInlineTokens([token], tokenKey)
            blockquoteChildren.push(...content)
          }
        })
      } else if (node.text) {
        blockquoteChildren.push(node.text)
      }
      
      return h('blockquote', { key: nodeKey }, blockquoteChildren)
    } else if (node.type === 'hr') {
      // 处理水平线
      return h('hr', { key: nodeKey })
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
      return children
    } else if (node.type === 'table') {
      // 处理表格
      const tableKey = `${nodeKey}`
      
      // 创建表格元素
      const tableChildren = []
      
      // 处理表头
      if (node.header && node.header.length > 0) {
        const theadChildren = []
        const headerRow = h('tr', { key: `${tableKey}-header-row` }, 
          node.header.map((cell, cellIndex) => {
            const cellContent = cell.tokens ? this.processInlineTokens(cell.tokens, `${tableKey}-header-${cellIndex}`) : cell.text
            return h('th', { key: `${tableKey}-header-${cellIndex}` }, cellContent)
          })
        )
        theadChildren.push(headerRow)
        tableChildren.push(h('thead', { key: `${tableKey}-thead` }, theadChildren))
      }
      
      // 处理表体 - 检查可能的属性名
      if (node.cells && node.cells.length > 0) {
        const tbodyChildren = []
        node.cells.forEach((row, rowIndex) => {
          const rowChildren = row.map((cell, cellIndex) => {
            const cellContent = cell.tokens ? this.processInlineTokens(cell.tokens, `${tableKey}-cell-${rowIndex}-${cellIndex}`) : cell.text
            return h('td', { key: `${tableKey}-cell-${rowIndex}-${cellIndex}` }, cellContent)
          })
          tbodyChildren.push(h('tr', { key: `${tableKey}-row-${rowIndex}` }, rowChildren))
        })
        tableChildren.push(h('tbody', { key: `${tableKey}-tbody` }, tbodyChildren))
      } else if (node.body && node.body.length > 0) {
        const tbodyChildren = []
        node.body.forEach((row, rowIndex) => {
          const rowChildren = row.map((cell, cellIndex) => {
            const cellContent = cell.tokens ? this.processInlineTokens(cell.tokens, `${tableKey}-cell-${rowIndex}-${cellIndex}`) : cell.text
            return h('td', { key: `${tableKey}-cell-${rowIndex}-${cellIndex}` }, cellContent)
          })
          tbodyChildren.push(h('tr', { key: `${tableKey}-row-${rowIndex}` }, rowChildren))
        })
        tableChildren.push(h('tbody', { key: `${tableKey}-tbody` }, tbodyChildren))
      } else if (node.rows && node.rows.length > 0) {
        const tbodyChildren = []
        node.rows.forEach((row, rowIndex) => {
          const rowChildren = row.map((cell, cellIndex) => {
            const cellContent = cell.tokens ? this.processInlineTokens(cell.tokens, `${tableKey}-cell-${rowIndex}-${cellIndex}`) : cell.text
            return h('td', { key: `${tableKey}-cell-${rowIndex}-${cellIndex}` }, cellContent)
          })
          tbodyChildren.push(h('tr', { key: `${tableKey}-row-${rowIndex}` }, rowChildren))
        })
        tableChildren.push(h('tbody', { key: `${tableKey}-tbody` }, tbodyChildren))
      }
      
      return h('table', { key: tableKey, class: 'markdown-table' }, tableChildren)
    } else if (node.type === 'text') {
      // 处理文本
      if (node.text.trim()) {
        return node.text
      }
    }

    return null
  }

  /**
   * 转换 AST 为 VNode 树
   * @param {Array} ast AST 节点数组
   * @returns {Array} VNode 数组
   */
  transform(ast) {
    if (!ast || !Array.isArray(ast)) return []
    
    // 分析 AST 结构
    const structure = this.structureAnalyzer.analyzeFromAst(ast)
    
    const vnodes = []
    
    // 根据结构生成 VNode
    structure.blocks.forEach((block, index) => {
      const node = block.node
      if (node) {
        // 直接转换节点，利用 AST 位置不变的特性
        const nodeKey = `${node.type}-${index}`
        const vnode = this.convertNodeToVNode(node, nodeKey)
        
        if (vnode) {
          if (Array.isArray(vnode)) {
            vnodes.push(...vnode)
          } else {
            vnodes.push(vnode)
          }
        }
      }
    })
    
    // 更新缓存
    this.cache.vnodes = vnodes
    this.cache.structure = structure
    this.cache.version++
    
    return vnodes
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.cache = {
      vnodes: [],
      version: 0,
      structure: null
    }
  }
}

/**
 * 创建 VNode 转换器实例
 * @returns {VNodeTransformer} 转换器实例
 */
export function createVNodeTransformer() {
  return new VNodeTransformer()
}
