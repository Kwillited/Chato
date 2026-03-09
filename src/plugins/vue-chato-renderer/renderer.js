import { marked } from 'marked'
import { highlightCode } from './highlighter.js'
import mermaid from 'mermaid'
import hljs from 'highlight.js/lib/core'

// 导出全局变量，供组件使用
globalThis.hljs = hljs
globalThis.mermaid = mermaid

/**
 * 创建 Chato Renderer 插件
 * @param {Object} config 配置选项
 * @returns {Object} 渲染实例
 */
export function createChatoRenderer(config) {
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
   * 渲染 Markdown 内容
   * @param {string} content Markdown 内容
   * @returns {string} 渲染后的 HTML
   */
  const render = (content) => {
    if (!content) return ''
    
    try {
      // 直接使用 marked 渲染内容
      // 数学公式处理已移至 MarkdownRender 组件中
      let html = marked(content)
      
      // 打印渲染结果
      console.log('Chato Renderer 渲染结果:', html)
      
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
      console.error('Chato Renderer 解析错误:', error)
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
