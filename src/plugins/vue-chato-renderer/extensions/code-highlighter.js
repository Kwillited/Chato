import hljs from 'highlight.js/lib/core'
import 'highlight.js/styles/github.css'
import 'highlight.js/styles/github-dark.css'

// 语言配置数组
const languages = [
  { name: 'xml', module: () => import('highlight.js/lib/languages/xml') },
  { name: 'bash', module: () => import('highlight.js/lib/languages/bash') },
  { name: 'c', module: () => import('highlight.js/lib/languages/c') },
  { name: 'cpp', module: () => import('highlight.js/lib/languages/cpp') },
  { name: 'csharp', module: () => import('highlight.js/lib/languages/csharp') },
  { name: 'css', module: () => import('highlight.js/lib/languages/css') },
  { name: 'markdown', module: () => import('highlight.js/lib/languages/markdown') },
  { name: 'diff', module: () => import('highlight.js/lib/languages/diff') },
  { name: 'ruby', module: () => import('highlight.js/lib/languages/ruby') },
  { name: 'go', module: () => import('highlight.js/lib/languages/go') },
  { name: 'graphql', module: () => import('highlight.js/lib/languages/graphql') },
  { name: 'ini', module: () => import('highlight.js/lib/languages/ini') },
  { name: 'java', module: () => import('highlight.js/lib/languages/java') },
  { name: 'javascript', module: () => import('highlight.js/lib/languages/javascript') },
  { name: 'json', module: () => import('highlight.js/lib/languages/json') },
  { name: 'kotlin', module: () => import('highlight.js/lib/languages/kotlin') },
  { name: 'less', module: () => import('highlight.js/lib/languages/less') },
  { name: 'lua', module: () => import('highlight.js/lib/languages/lua') },
  { name: 'makefile', module: () => import('highlight.js/lib/languages/makefile') },
  { name: 'perl', module: () => import('highlight.js/lib/languages/perl') },
  { name: 'objectivec', module: () => import('highlight.js/lib/languages/objectivec') },
  { name: 'php', module: () => import('highlight.js/lib/languages/php') },
  { name: 'php-template', module: () => import('highlight.js/lib/languages/php-template') },
  { name: 'plaintext', module: () => import('highlight.js/lib/languages/plaintext') },
  { name: 'python', module: () => import('highlight.js/lib/languages/python') },
  { name: 'python-repl', module: () => import('highlight.js/lib/languages/python-repl') },
  { name: 'r', module: () => import('highlight.js/lib/languages/r') },
  { name: 'rust', module: () => import('highlight.js/lib/languages/rust') },
  { name: 'scss', module: () => import('highlight.js/lib/languages/scss') },
  { name: 'shell', module: () => import('highlight.js/lib/languages/shell') },
  { name: 'sql', module: () => import('highlight.js/lib/languages/sql') },
  { name: 'swift', module: () => import('highlight.js/lib/languages/swift') },
  { name: 'yaml', module: () => import('highlight.js/lib/languages/yaml') },
  { name: 'typescript', module: () => import('highlight.js/lib/languages/typescript') },
  { name: 'vbnet', module: () => import('highlight.js/lib/languages/vbnet') },
  { name: 'wasm', module: () => import('highlight.js/lib/languages/wasm') }
]

// 注册语言（按需加载）
export async function registerLanguages() {
  for (const lang of languages) {
    try {
      const module = await lang.module()
      hljs.registerLanguage(lang.name, module.default)
    } catch (error) {
      console.warn(`注册语言 ${lang.name} 失败:`, error)
    }
  }
}

// 立即注册常用语言（同步加载）
import xml from 'highlight.js/lib/languages/xml'
import javascript from 'highlight.js/lib/languages/javascript'
import css from 'highlight.js/lib/languages/css'
import json from 'highlight.js/lib/languages/json'
import markdown from 'highlight.js/lib/languages/markdown'
import plaintext from 'highlight.js/lib/languages/plaintext'

hljs.registerLanguage('xml', xml)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('css', css)
hljs.registerLanguage('json', json)
hljs.registerLanguage('markdown', markdown)
hljs.registerLanguage('plaintext', plaintext)

/**
 * 代码高亮器
 * 负责代码高亮功能
 */
export class CodeHighlighter {
  /**
   * 初始化代码高亮
   */
  init() {
    if (typeof hljs !== 'undefined') {
      console.log('CodeHighlighter 已初始化')
    } else {
      console.warn('代码高亮库未加载')
    }
  }

  /**
   * 高亮所有代码块
   */
  highlightAll() {
    if (typeof hljs !== 'undefined') {
      // 移除所有代码元素的 data-highlighted 属性，确保重新高亮
      const codeElements = document.querySelectorAll('code[class^="language-"]')
      codeElements.forEach(element => {
        if (element.dataset.highlighted) {
          delete element.dataset.highlighted
        }
      })
      hljs.highlightAll()
    }
  }

  /**
   * 高亮单个代码元素
   * @param {HTMLElement} element 代码元素
   */
  highlightElement(element) {
    if (typeof hljs !== 'undefined' && element) {
      // 移除 data-highlighted 属性，确保重新高亮
      if (element.dataset.highlighted) {
        delete element.dataset.highlighted
      }
      hljs.highlightElement(element)
    }
  }

  /**
   * 高亮代码字符串
   * @param {string} code 代码字符串
   * @param {string} language 语言
   * @returns {string} 高亮后的 HTML
   */
  highlight(code, language) {
    if (typeof hljs !== 'undefined') {
      return hljs.highlight(code, { language }).value
    }
    return code
  }

  /**
   * 获取 highlight.js 实例
   * @returns {Object} highlight.js 实例
   */
  getHljs() {
    return hljs
  }
}

/**
 * 单例实例
 */
let highlighterInstance = null

/**
 * 创建代码高亮器实例
 * @returns {CodeHighlighter} 高亮器实例
 */
export function createCodeHighlighter() {
  if (!highlighterInstance) {
    highlighterInstance = new CodeHighlighter()
  }
  return highlighterInstance
}

/**
 * 注册代码高亮功能
 */
export async function registerHighlighter() {
  if (!highlighterInstance) {
    highlighterInstance = new CodeHighlighter()
    highlighterInstance.init()
    // 注册所有语言
    await registerLanguages()
  }
  return highlighterInstance
}

/**
 * 执行代码高亮
 */
export function highlightCode() {
  const highlighter = createCodeHighlighter()
  highlighter.highlightAll()
}
