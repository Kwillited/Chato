import { createMarkdownRenderer } from './core/markdown-renderer.js'
import { registerHighlighter } from './extensions/code-highlighter.js'
import { setupCopyHandler, copyToClipboard, copyMarkdown } from './extensions/copy-feature.js'
import VueChatoRenderer from './VueChatoRenderer.vue'

// 创建复制功能对象
const copyUtils = {
  copyToClipboard,
  copyMarkdown
}

/**
 * Vue-Chato-Renderer 渲染插件
 * 提供统一的 Markdown 渲染功能，包括代码高亮和复制功能
 */
export default {
  async install(app, options = {}) {
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
      await registerHighlighter()
    }
    
    // 设置复制功能
    if (config.copy) {
      setupCopyHandler()
    }
    
    // 创建渲染实例
    const markdown = createMarkdownRenderer(config)
    
    // 全局注册
    app.config.globalProperties.$vueChatoRenderer = markdown
    app.provide('vueChatoRenderer', markdown)
    
    // 提供复制功能
    app.config.globalProperties.$copyUtils = copyUtils
    app.provide('copyUtils', copyUtils)
    
    // 全局注册组件
    app.component('VueChatoRenderer', VueChatoRenderer)
    
    console.log('Vue-Chato-Renderer 插件已初始化')
  }
}

// 导出组件和复制功能，支持直接导入
export { VueChatoRenderer, copyToClipboard, copyMarkdown, copyUtils }
