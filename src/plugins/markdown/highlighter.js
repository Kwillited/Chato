import hljs from '../../static/js/highlight-common.js'

/**
 * 注册代码高亮功能
 */
export function registerHighlighter() {
  // 确保代码高亮库已加载
  if (typeof hljs !== 'undefined') {
    // 可以在这里添加自定义语言或配置
    console.log('Markdown 代码高亮已注册')
  } else {
    console.warn('代码高亮库未加载')
  }
}

/**
 * 执行代码高亮
 */
export function highlightCode() {
  if (typeof hljs !== 'undefined') {
    hljs.highlightAll()
  }
}
