import { marked } from 'marked'
import hljs from '../../static/js/highlight-common.js'
import katex from 'katex'
import mermaid from 'mermaid'
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
    
    // 处理 Mermaid 图表
    if (actualLanguage === 'mermaid') {
      const mermaidId = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      return `
        <div class="code-container">
          <div class="code-header">
            <span class="code-language">mermaid</span>
            <div class="code-header-actions">
              <div class="mermaid-toggle-slider"
                data-mermaid-id="${mermaidId}"
                data-code-id="${codeBlockId}"
                title="切换视图"
              >
                <div class="slider-track">
                  <div class="slider-thumb">
                    <i class="fa-solid fa-chart-simple"></i>
                  </div>
                </div>

              </div>
              <button 
                class="copy-code-btn"
                data-code-block-id="${codeBlockId}"
                title="复制代码"
              >
                <i class="fa-solid fa-copy"></i>
              </button>
            </div>
          </div>
          <div class="mermaid-container">
            <pre class="mermaid" id="${mermaidId}">${actualCode}</pre>
            <pre class="mermaid-code" id="${codeBlockId}" style="display: none;"><code class="language-mermaid">${actualCode}</code></pre>
          </div>
        </div>
      `
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
    const blockMathRegex = /\$\$([\s\S]*?)\$\$/g
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
      // 先处理数学公式，避免 marked 转换换行符影响正则匹配
      let processedContent = content
      
      // 处理块级公式 $$...$$
      const blockMathRegex = /\$\$([\s\S]*?)\$\$/g
      processedContent = processedContent.replace(blockMathRegex, (match, formula) => {
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
      processedContent = processedContent.replace(inlineMathRegex, (match, formula) => {
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
      
      // 然后使用 marked 渲染剩余内容
      let html = marked(processedContent)
      
      // 延迟执行代码高亮和 Mermaid 渲染
      if (config.highlight) {
        setTimeout(() => {
          hljs.highlightAll()
          // 渲染 Mermaid 图表
          mermaid.init()
          // 绑定 Mermaid 切换按钮事件
          bindMermaidToggleEvents()
        }, 0)
      } else {
        // 即使没有代码高亮，也需要渲染 Mermaid 图表
        setTimeout(() => {
          mermaid.init()
          // 绑定 Mermaid 切换按钮事件
          bindMermaidToggleEvents()
        }, 0)
      }
      
      return html
    } catch (error) {
      console.error('Markdown 解析错误:', error)
      return content.replace(/\n/g, '<br>')
    }
  }
  
  /**
   * 绑定 Mermaid 切换滑块事件
   */
  const bindMermaidToggleEvents = () => {
    const toggleSliders = document.querySelectorAll('.mermaid-toggle-slider')
    toggleSliders.forEach(slider => {
      slider.addEventListener('click', () => {
        const mermaidId = slider.getAttribute('data-mermaid-id')
        const codeId = slider.getAttribute('data-code-id')
        const mermaidElement = document.getElementById(mermaidId)
        const codeElement = document.getElementById(codeId)
        
        if (mermaidElement && codeElement) {
          const isMermaidVisible = mermaidElement.style.display !== 'none'
          
          if (isMermaidVisible) {
            // 切换到代码视图
            mermaidElement.style.display = 'none'
            codeElement.style.display = 'block'
            // 更新滑块状态
            slider.classList.add('active')
            // 切换图标
            const icon = slider.querySelector('i')
            if (icon) {
              icon.className = 'fa-solid fa-code'
            }
          } else {
            // 切换到图表视图
            mermaidElement.style.display = 'block'
            codeElement.style.display = 'none'
            // 更新滑块状态
            slider.classList.remove('active')
            // 切换图标
            const icon = slider.querySelector('i')
            if (icon) {
              icon.className = 'fa-solid fa-chart-simple'
            }
          }
        }
      })
    })
  }

  return {
    render,
    marked,
    config
  }
}
