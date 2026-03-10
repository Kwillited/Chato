import { marked } from 'marked'

/**
 * Markdown 渲染器
 * 负责基础 Markdown 解析和渲染
 */
export class MarkdownRenderer {
  constructor(config = {}) {
    this.config = {
      breaks: true,
      gfm: true,
      highlight: true,
      ...config
    }
    this.renderer = new marked.Renderer()
    this.setupRenderer()
  }

  /**
   * 设置渲染器
   */
  setupRenderer() {
    // 设置 marked 配置
    marked.setOptions({
      renderer: this.renderer,
      breaks: this.config.breaks,
      gfm: this.config.gfm
    })
  }

  /**
   * 渲染 Markdown 内容
   * @param {string} content Markdown 内容
   * @returns {string} 渲染后的 HTML
   */
  render(content) {
    if (!content) return ''
    
    try {
      return marked(content)
    } catch (error) {
      console.error('Markdown 渲染错误:', error)
      return content.replace(/\n/g, '<br>')
    }
  }

  /**
   * 获取 marked 实例
   * @returns {Object} marked 实例
   */
  getMarked() {
    return marked
  }

  /**
   * 获取配置
   * @returns {Object} 配置选项
   */
  getConfig() {
    return this.config
  }
}

/**
 * 创建 Markdown 渲染器实例
 * @param {Object} config 配置选项
 * @returns {MarkdownRenderer} 渲染器实例
 */
export function createMarkdownRenderer(config) {
  return new MarkdownRenderer(config)
}
