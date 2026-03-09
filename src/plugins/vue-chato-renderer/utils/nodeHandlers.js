import { h } from 'vue'
import CodeBlock from '../components/CodeBlock.vue'
import { processInlineTokens } from './tokenProcessor.js'

export const handleCodeNode = (node, index) => {
  const nodeKey = `${node.type}-${index}`
  return h(CodeBlock, {
    key: nodeKey,
    code: node.text,
    language: node.lang || 'plaintext',
    isMermaid: node.lang === 'mermaid'
  })
}

export const handleHeadingNode = (node, index) => {
  const nodeKey = `${node.type}-${index}`
  const headingContent = node.tokens ? processInlineTokens(node.tokens, nodeKey) : node.text
  return h(`h${node.depth}`, { key: nodeKey }, headingContent)
}

export const handleParagraphNode = (node, index) => {
  const nodeKey = `${node.type}-${index}`
  const onlyImages = node.tokens && Array.isArray(node.tokens) && 
    node.tokens.every(token => 
      token.type === 'image' || 
      (token.type === 'text' && token.text.trim() === '') ||
      token.type === 'br'
    );
  
  if (onlyImages) {
    const vnodes = []
    if (node.tokens && Array.isArray(node.tokens)) {
      node.tokens.forEach((token, tokenIndex) => {
        if (token.type === 'image') {
          const tokenKey = `${nodeKey}-token-${tokenIndex}`;
          vnodes.push(h('img', {
            key: tokenKey,
            src: token.href,
            alt: token.text || '',
            title: token.title,
            class: 'markdown-image'
          }))
        }
      });
    }
    return vnodes
  } else {
    const paragraphContent = node.tokens ? processInlineTokens(node.tokens, nodeKey) : node.text
    return h('p', { key: nodeKey }, paragraphContent)
  }
}

export const handleListNode = (node, index) => {
  const nodeKey = `${node.type}-${index}`
  const listItems = node.items.map((item, itemIndex) => {
    const itemKey = `${nodeKey}-item-${itemIndex}`
    const itemChildren = []
    
    if (item.tokens && Array.isArray(item.tokens)) {
      item.tokens.forEach((token, tokenIndex) => {
        const tokenKey = `${itemKey}-token-${tokenIndex}`
        
        if (token.type === 'checkbox') {
          itemChildren.push(h('input', {
            key: tokenKey,
            type: 'checkbox',
            checked: token.checked,
            disabled: true,
            class: 'task-checkbox'
          }))
          itemChildren.push(' ')
        } else if (token.type === 'text') {
          if (token.text) {
            const textContent = processInlineTokens(token.tokens, tokenKey)
            itemChildren.push(h('p', { 
              key: tokenKey,
              class: 'ds-markdown-paragraph'
            }, textContent))
          }
        } else if (token.type === 'paragraph') {
          if (token.tokens) {
            const paragraphContent = processInlineTokens(token.tokens, tokenKey)
            itemChildren.push(h('p', { 
              key: tokenKey,
              class: 'ds-markdown-paragraph'
            }, paragraphContent))
          } else if (token.text) {
            itemChildren.push(h('p', { 
              key: tokenKey,
              class: 'ds-markdown-paragraph'
            }, token.text))
          }
        } else if (token.type === 'list') {
          const nestedListItems = token.items.map((nestedItem, nestedIndex) => {
            const nestedItemKey = `${tokenKey}-item-${nestedIndex}`
            const nestedItemChildren = []
            
            if (nestedItem.tokens && Array.isArray(nestedItem.tokens)) {
              nestedItem.tokens.forEach((nestedToken, nestedTokenIndex) => {
                const nestedTokenKey = `${nestedItemKey}-token-${nestedTokenIndex}`
                
                if (nestedToken.type === 'checkbox') {
                  nestedItemChildren.push(h('input', {
                    key: nestedTokenKey,
                    type: 'checkbox',
                    checked: nestedToken.checked,
                    disabled: true,
                    class: 'task-checkbox'
                  }))
                  nestedItemChildren.push(' ')
                } else if (nestedToken.type === 'text') {
                  if (nestedToken.text) {
                    const nestedTextContent = processInlineTokens(nestedToken.tokens, nestedTokenKey)
                    nestedItemChildren.push(h('p', { 
                      key: nestedTokenKey,
                      class: 'ds-markdown-paragraph'
                    }, nestedTextContent))
                  }
                } else if (nestedToken.type === 'paragraph') {
                  if (nestedToken.tokens) {
                    const nestedParagraphContent = processInlineTokens(nestedToken.tokens, nestedTokenKey)
                    nestedItemChildren.push(h('p', { 
                      key: nestedTokenKey,
                      class: 'ds-markdown-paragraph'
                    }, nestedParagraphContent))
                  } else if (nestedToken.text) {
                    nestedItemChildren.push(h('p', { 
                      key: nestedTokenKey,
                      class: 'ds-markdown-paragraph'
                    }, nestedToken.text))
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
  return h(node.ordered ? 'ol' : 'ul', { key: nodeKey, class: 'task-list' }, listItems)
}

export const handleBlockquoteNode = (node, index) => {
  const nodeKey = `${node.type}-${index}`
  const blockquoteChildren = []
  
  if (node.tokens && Array.isArray(node.tokens)) {
    node.tokens.forEach((token, tokenIndex) => {
      const tokenKey = `${nodeKey}-token-${tokenIndex}`
      
      if (token.type === 'paragraph') {
        const paragraphContent = token.tokens ? processInlineTokens(token.tokens, tokenKey) : token.text
        blockquoteChildren.push(h('p', { key: tokenKey }, paragraphContent))
      } else if (token.type === 'blockquote') {
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
        const content = processInlineTokens([token], tokenKey)
        blockquoteChildren.push(...content)
      }
    })
  } else if (node.text) {
    blockquoteChildren.push(node.text)
  }
  
  return h('blockquote', { key: nodeKey }, blockquoteChildren)
}

export const handleHrNode = (node, index) => {
  const nodeKey = `${node.type}-${index}`
  return h('hr', { key: nodeKey })
}

export const handleHtmlNode = (node, index) => {
  const nodeKey = `${node.type}-${index}`
  const parser = new DOMParser()
  const doc = parser.parseFromString(node.text, 'text/html')
  const root = doc.body
  
  const convertNode = (domNode, nodeIndex) => {
    if (domNode.nodeType === Node.TEXT_NODE) {
      return domNode.textContent
    } else if (domNode.nodeType === Node.ELEMENT_NODE) {
      const props = {}
      
      for (let i = 0; i < domNode.attributes.length; i++) {
        const attr = domNode.attributes[i]
        props[attr.name] = attr.value
      }
      
      props.key = `${nodeKey}-html-${nodeIndex}`
      
      const children = Array.from(domNode.childNodes).map((child, childIndex) => 
        convertNode(child, `${nodeIndex}-${childIndex}`)
      ).filter(child => child !== null && child !== '')
      
      return h(domNode.tagName.toLowerCase(), props, children)
    }
    return null
  }
  
  const children = Array.from(root.childNodes).map((child, index) => 
    convertNode(child, index)
  ).filter(child => child !== null && child !== '')
  return children
}

export const handleTableNode = (node, index) => {
  const nodeKey = `${node.type}-${index}`
  const tableKey = `${nodeKey}`
  
  const tableChildren = []
  
  if (node.header && node.header.length > 0) {
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
  
  if (node.cells && node.cells.length > 0) {
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
    const tbodyChildren = []
    node.rows.forEach((row, rowIndex) => {
      const rowChildren = row.map((cell, cellIndex) => {
        const cellContent = cell.tokens ? processInlineTokens(cell.tokens, `${tableKey}-cell-${rowIndex}-${cellIndex}`) : cell.text
        return h('td', { key: `${tableKey}-cell-${rowIndex}-${cellIndex}` }, cellContent)
      })
      tbodyChildren.push(h('tr', { key: `${tableKey}-row-${rowIndex}` }, rowChildren))
    })
    tableChildren.push(h('tbody', { key: `${tableKey}-tbody` }, tbodyChildren))
  }
  
  return h('table', { key: tableKey, class: 'markdown-table' }, tableChildren)
}

export const handleTextNode = (node, index) => {
  if (node.text.trim()) {
    return node.text
  }
  return null
}
