import { inject } from 'vue'

/**
 * Markdown 渲染组合式函数
 * @returns {Object} Markdown 渲染相关方法
 */
export function useMarkdown() {
  const markdown = inject('markdown')
  
  /**
   * 渲染 Markdown 内容
   * @param {string} content Markdown 内容
   * @returns {string} 渲染后的 HTML
   */
  const renderMarkdown = (content) => {
    if (markdown) {
      return markdown.render(content)
    }
    
    // 降级处理
    return content
  }
  
  return {
    renderMarkdown,
    markdown
  }
}
