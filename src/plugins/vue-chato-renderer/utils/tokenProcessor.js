import { h } from 'vue'
import { inlineRules } from '../config/inlineRules.js'
import { processMathFormulasInText } from './mathFormulaProcessor.js'
import { parseHtmlString, convertElementToVNode } from './htmlProcessor.js'

export const processInlineTokens = (tokens, parentKey) => {
  if (!tokens || !Array.isArray(tokens)) return []
  
  const mergedTokens = []
  let currentText = ''
  
  tokens.forEach((token, index) => {
    if (token.type === 'text' || token.type === 'br' || token.type === 'escape') {
      if (token.type === 'escape') {
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
    const rule = inlineRules[token.type]
    
    if (rule) {
      if (token.type === 'text' && (token.text.includes('$$') || token.text.includes('$') || token.text.includes('\\(') || token.text.includes('\\['))) {
        const processedParts = processMathFormulasInText(token.text)
        if (processedParts.length > 1 || (processedParts.length === 1 && processedParts[0].includes('katex'))) {
          processedParts.forEach((part, partIndex) => {
            if (typeof part === 'string' && part.includes('katex')) {
              try {
                const htmlElement = parseHtmlString(part)
                if (htmlElement) {
                  const childVNodes = Array.from(htmlElement.childNodes).map((child, childIndex) => 
                    convertElementToVNode(child, `${tokenKey}-katex-${partIndex}-${childIndex}`)
                  ).filter(child => child !== null && child !== '')
                  result.push(...childVNodes)
                } else {
                  result.push(h('span', {
                    key: `${tokenKey}-katex-${partIndex}`,
                    innerHTML: part
                  }))
                }
              } catch (error) {
                console.error('KaTeX HTML 转换错误:', error)
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
          result.push(rule(token, tokenKey))
        }
      } else {
        result.push(rule(token, tokenKey))
      }
    } else {
      if (token.text && (token.text.includes('$$') || token.text.includes('$') || token.text.includes('\\(') || token.text.includes('\\['))) {
        const processedParts = processMathFormulasInText(token.text)
        if (processedParts.length > 1 || (processedParts.length === 1 && processedParts[0].includes('katex'))) {
          processedParts.forEach((part, partIndex) => {
            if (typeof part === 'string' && part.includes('katex')) {
              try {
                const htmlElement = parseHtmlString(part)
                if (htmlElement) {
                  const childVNodes = Array.from(htmlElement.childNodes).map((child, childIndex) => 
                    convertElementToVNode(child, `${tokenKey}-katex-${partIndex}-${childIndex}`)
                  ).filter(child => child !== null && child !== '')
                  result.push(...childVNodes)
                } else {
                  result.push(h('span', {
                    key: `${tokenKey}-katex-${partIndex}`,
                    innerHTML: part
                  }))
                }
              } catch (error) {
                console.error('KaTeX HTML 转换错误:', error)
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
          result.push(token.text || '')
        }
      } else {
        result.push(token.text || '')
      }
    }
  })
  
  return result
}
