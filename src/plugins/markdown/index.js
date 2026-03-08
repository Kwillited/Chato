import { createMarkdownPlugin } from './renderer.js'
import { registerHighlighter } from './highlighter.js'
import { setupCopyHandler } from './copyHandler.js'
import MarkdownRender from './MarkdownRender.vue'

/**
 * Markdown 渲染插件
 * 提供统一的 Markdown 渲染功能，包括代码高亮和复制功能
 */
export default {
  install(app, options = {}) {
    // 初始化配置
    const config = {
      breaks: true,
      gfm: true,
      highlight: true,
      copy: true,
      ...options
    }
    
    // 注册代码高亮
    if (config.highlight) {
      registerHighlighter()
    }
    
    // 设置复制功能
    if (config.copy) {
      setupCopyHandler()
    }
    
    // 创建渲染实例
    const markdown = createMarkdownPlugin(config)
    
    // 全局注册
    app.config.globalProperties.$markdown = markdown
    app.provide('markdown', markdown)
    
    // 全局注册组件
    app.component('MarkdownRender', MarkdownRender)
    
    console.log('Markdown 插件已初始化')
  }
}

// 导出组件，支持直接导入
export { MarkdownRender }
