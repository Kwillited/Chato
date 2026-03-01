import { marked } from 'marked'
import hljs from '../../static/js/highlight-common.js'

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
   * 渲染 Markdown 内容
   * @param {string} content Markdown 内容
   * @returns {string} 渲染后的 HTML
   */
  const render = (content) => {
    if (!content) return ''
    
    try {
      const html = marked(content)
      
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
