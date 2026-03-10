import mermaid from 'mermaid'

/**
 * Mermaid 渲染器
 * 负责处理 Mermaid 图表的渲染
 */
export class MermaidRenderer {
  /**
   * 渲染 Mermaid 图表
   * @param {string} code Mermaid 代码
   * @returns {Promise<string>} 渲染后的 SVG 字符串
   */
  async render(code) {
    if (!code) return ''
    
    try {
      // 清理代码
      const cleanedCode = this.cleanCode(code)
      
      // 验证代码语法
      await mermaid.parse(cleanedCode)
      
      // 生成稳定的 ID
      const id = this.generateStableId(cleanedCode)
      
      // 渲染图表
      const result = await mermaid.render(id, cleanedCode)
      return result.svg
    } catch (error) {
      console.error('Mermaid 渲染错误:', error)
      return ''
    }
  }

  /**
   * 清理 Mermaid 代码
   * @param {string} code Mermaid 代码
   * @returns {string} 清理后的代码
   */
  cleanCode(code) {
    let cleaned = code.trim()
    
    // 移除代码块标记
    if (cleaned.startsWith('```mermaid')) {
      cleaned = cleaned.substring('```mermaid'.length)
    }
    if (cleaned.endsWith('```')) {
      cleaned = cleaned.substring(0, cleaned.length - 3)
    }
    
    return cleaned.trim()
  }

  /**
   * 生成稳定的 ID
   * @param {string} code Mermaid 代码
   * @returns {string} 稳定的 ID
   */
  generateStableId(code) {
    let hash = 0
    for (let i = 0; i < code.length; i++) {
      const char = code.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // 转换为 32 位整数
    }
    return `mermaid-${Math.abs(hash)}`
  }

  /**
   * 检查是否为 Mermaid 代码
   * @param {string} code 代码
   * @param {string} language 语言
   * @returns {boolean} 是否为 Mermaid 代码
   */
  isMermaidCode(code, language) {
    return language === 'mermaid' || code.trim().startsWith('```mermaid')
  }
}

/**
 * 创建 Mermaid 渲染器实例
 * @returns {MermaidRenderer} 渲染器实例
 */
export function createMermaidRenderer() {
  return new MermaidRenderer()
}
