import { marked } from 'marked'
import hljs from '../../static/js/highlight-common.js'
import { highlightCode } from './highlighter.js'
import katex from 'katex'
import mermaid from 'mermaid'
import 'katex/dist/katex.min.css'

// 导出全局变量，供组件使用
globalThis.hljs = hljs
globalThis.mermaid = mermaid

/**
 * 创建 Markdown 渲染插件
 * @param {Object} config 配置选项
 * @returns {Object} 渲染实例
 */
export function createMarkdownPlugin(config) {
  // 配置渲染器
  const renderer = new marked.Renderer()
  
  // 自定义代码块渲染
  renderer.code = function(code, language) {
    // 处理可能的AST节点
    let actualCode = code
    let actualLanguage = language
    
    if (typeof code === 'object' && code !== null) {
      if (code.type === 'code') {
        actualCode = code.text || code.raw || ''
        actualLanguage = code.lang || language
      } else {
        actualCode = JSON.stringify(code, null, 2)
      }
    } else if (typeof code !== 'string') {
      actualCode = String(code)
    }
    
    // 简化代码块渲染，返回原始代码
    return actualCode
  }
  
  // 设置 marked 配置
  marked.setOptions({
    renderer: renderer,
    breaks: config.breaks,
    gfm: config.gfm
  })
  
  /**
   * 处理数学公式
   * @param {string} content Markdown 内容
   * @returns {string} 处理后的内容
   */
  const processMathFormulas = (content) => {
    // 处理块级公式 $$...$$
    const blockMathRegex = /\$\$([\s\S]*?)\$\$/g
    let result = content.replace(blockMathRegex, (match, formula) => {
      try {
        return '<div class="math-block">' + katex.renderToString(formula.trim(), {
          throwOnError: false,
          displayMode: true
        }) + '</div>'
      } catch (error) {
        console.error('KaTeX 块级公式渲染错误:', error)
        return match
      }
    })
    
    // 处理行内公式 $...$
    const inlineMathRegex = /\$(.*?)\$/g
    result = result.replace(inlineMathRegex, (match, formula) => {
      try {
        return katex.renderToString(formula.trim(), {
          throwOnError: false,
          displayMode: false
        })
      } catch (error) {
        console.error('KaTeX 行内公式渲染错误:', error)
        return match
      }
    })
    
    return result
  }
  

  
  /**
   * 渲染 Markdown 内容
   * @param {string} content Markdown 内容
   * @returns {string} 渲染后的 HTML
   */
  const render = (content) => {
    if (!content) return ''
    
    try {
      // 先处理数学公式，避免 marked 转换换行符影响正则匹配
      let processedContent = processMathFormulas(content)
      
      // 然后使用 marked 渲染剩余内容
      let html = marked(processedContent)
      
      // 打印 marked 解释后的内容
      console.log('Marked 渲染结果:', html)
      
      // 立即执行代码高亮和 Mermaid 渲染
      // 使用 requestAnimationFrame 确保 DOM 已更新但不会阻塞渲染
      requestAnimationFrame(() => {
        if (config.highlight) {
          // 清除所有代码块的高亮标记，避免重复高亮警告
          const codeElements = document.querySelectorAll('code[class^="language-"]')
          codeElements.forEach(element => {
            delete element.dataset.highlighted
          })
          
          highlightCode()
        }
      })
      
      return html
    } catch (error) {
      console.error('Markdown 解析错误:', error)
      return content.replace(/\n/g, '<br>')
    }
  }
  


  /**
   * 解析 Markdown 为 AST
   * @param {string} content Markdown 内容
   * @returns {Array} 解析后的 AST
   */
  const parseToAst = (content) => {
    if (!content) return []
    return marked.lexer(content)
  }

  return {
    render,
    parseToAst,
    marked,
    config
  }
}
