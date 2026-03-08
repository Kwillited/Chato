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
    
    // 处理 Mermaid 图表
    if (actualLanguage === 'mermaid') {
      const mermaidId = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      const containerId = `mermaid-container-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
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
          <div class="mermaid-container" id="${containerId}">
            <pre class="mermaid" id="${mermaidId}">${actualCode}</pre>
          </div>
          <pre class="mermaid-code" id="${codeBlockId}" style="display: none;"><code class="language-plaintext">${actualCode}</code></pre>
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
   * 渐进式渲染 Mermaid 图表
   * @param {string} containerId 容器元素 ID
   * @param {string} code Mermaid 代码
   */
  const renderMermaidProgressive = (containerId, code) => {
    // 检查容器是否存在的函数
    const checkContainer = () => {
      const container = document.getElementById(containerId)
      if (container) {
        // 容器存在，开始渲染
        startRendering(container, code)
      } else {
        // 容器不存在，继续检查（最多检查 10 次，每次间隔 50ms）
        if (checkContainer.attempts < 10) {
          checkContainer.attempts++
          setTimeout(checkContainer, 50)
        }
      }
    }
    
    // 初始化检查次数
    checkContainer.attempts = 0
    
    // 开始检查
    checkContainer()
    
    // 开始渲染函数
    function startRendering(container, code) {
      // 清理代码，移除 Markdown 代码块 delimiters
      let cleanedCode = code.trim()
      // 移除开头的 ```mermaid
      if (cleanedCode.startsWith('```mermaid')) {
        cleanedCode = cleanedCode.substring('```mermaid'.length)
      }
      // 移除结尾的 ```
      if (cleanedCode.endsWith('```')) {
        cleanedCode = cleanedCode.substring(0, cleanedCode.length - 3)
      }
      cleanedCode = cleanedCode.trim()
      
      // 分割代码行
      const lines = cleanedCode.split('\n').filter(line => line.trim() !== '')
      if (lines.length === 0) return
      
      // 初始化渲染
      let currentCode = ''
      let lineIndex = 0
      let isRendering = false
      
      // 渐进式渲染函数
      const renderNextLine = () => {
        if (lineIndex < lines.length && !isRendering) {
          // 添加下一行代码到缓冲区
          currentCode += lines[lineIndex] + '\n'
          lineIndex++
          
          // 异步验证语法正确性
          setTimeout(() => {
            try {
              const parseResult = mermaid.parse(currentCode)
              if (parseResult) {
                // 语法正确，进行渲染
                isRendering = true
                
                // 生成唯一 ID
                const renderId = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
                
                // 使用 mermaid.render 方法进行渲染
                mermaid.render(renderId, currentCode)
                  .then(result => {
                    // 渲染成功，更新容器
                    container.innerHTML = result.svg
                    isRendering = false
                    // 继续渲染下一行
                    setTimeout(renderNextLine, 0)
                  })
                  .catch(error => {
                    console.error('Mermaid 渲染错误:', error)
                    isRendering = false
                    // 继续渲染下一行
                    setTimeout(renderNextLine, 0)
                  })
              } else {
                // 语法不正确时，继续处理下一行
                isRendering = false
                // 继续渲染下一行
                setTimeout(renderNextLine, 0)
              }
            } catch (error) {
              // 语法验证错误是预期的，不打印错误信息
              isRendering = false
              // 继续渲染下一行
              setTimeout(renderNextLine, 0)
            }
          }, 0)
        }
      }
      
      // 开始渐进式渲染
      renderNextLine()
    }
  }
  
  /**
   * 渲染所有 Mermaid 图表
   */
  const renderMermaidCharts = () => {
    const codeContainers = document.querySelectorAll('.code-container')
    codeContainers.forEach(container => {
      const mermaidContainer = container.querySelector('.mermaid-container')
      const mermaidCode = container.querySelector('.mermaid-code code')
      
      if (mermaidContainer && mermaidCode && !mermaidContainer.dataset.rendered) {
        const code = mermaidCode.textContent
        // 标记为已渲染，避免重复渲染
        mermaidContainer.dataset.rendered = 'true'
        // 立即处理 Mermaid 渲染
        renderMermaidProgressive(mermaidContainer.id, code)
      }
    })
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
        
        // 渲染 Mermaid 图表
        renderMermaidCharts()
        
        // 绑定 Mermaid 切换按钮事件
        bindMermaidToggleEvents()
      })
      
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
        const codeId = slider.getAttribute('data-code-id')
        const codeContainer = slider.closest('.code-container')
        const mermaidContainer = codeContainer.querySelector('.mermaid-container')
        const codeElement = document.getElementById(codeId)
        
        if (mermaidContainer && codeElement) {
          const isMermaidVisible = mermaidContainer.style.display !== 'none'
          
          if (isMermaidVisible) {
            // 切换到代码视图
            mermaidContainer.style.display = 'none'
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
            mermaidContainer.style.display = 'block'
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
