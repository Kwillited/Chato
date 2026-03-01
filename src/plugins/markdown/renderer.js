import { marked } from 'marked'
import hljs from '../../static/js/highlight-common.js'
import katex from 'katex'
import 'katex/dist/katex.min.css'

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
    
    const displayLanguage = actualLanguage && actualLanguage !== 'text' ? actualLanguage : 'plaintext'
    const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    return `
      <div class="code-container">
        <div class="code-header">
          <span class="code-language">${displayLanguage}</span>
          <button 
            class="copy-code-btn"
            data-code-block-id="${codeBlockId}"
            title="复制代码"
          >
            <i class="fa-solid fa-copy"></i>
          </button>
        </div>
        <pre><code class="language-${displayLanguage}" id="${codeBlockId}">${actualCode}</code></pre>
      </div>
    `
  }
  
  // 设置 marked 配置
  marked.setOptions({
    renderer: renderer,
    breaks: config.breaks,
    gfm: config.gfm
  })
  
  /**
   * 渲染数学公式
   * @param {string} html 渲染后的 HTML
   * @returns {string} 处理后的 HTML
   */
  const renderMathInElement = (html) => {
    // 处理行内公式 $...$
    const inlineMathRegex = /\$(.*?)\$/g
    let result = html.replace(inlineMathRegex, (match, formula) => {
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
    
    // 处理块级公式 $$...$$
    const blockMathRegex = /\$\$(.*?)\$\$/gs
    result = result.replace(blockMathRegex, (match, formula) => {
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
      let html = marked(content)
      
      // 处理数学公式
      html = renderMathInElement(html)
      
      // 延迟执行代码高亮
      if (config.highlight) {
        setTimeout(() => {
          hljs.highlightAll()
        }, 0)
      }
      
      return html
    } catch (error) {
      console.error('Markdown 解析错误:', error)
      return content.replace(/\n/g, '<br>')
    }
  }
  
  return {
    render,
    marked,
    config
  }
}
