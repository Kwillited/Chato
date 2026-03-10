import { marked } from 'marked'

/**
 * AST 解析器
 * 负责将 Markdown 解析为 AST 结构，支持增量解析和缓存
 */
export class AstParser {
  constructor() {
    // 缓存机制
    this.cache = {
      text: '',
      ast: []
    }
  }

  /**
   * 解析 Markdown 为 AST
   * @param {string} content Markdown 内容
   * @returns {Array} 解析后的 AST
   */
  parse(content) {
    if (!content) {
      this.cache = {
        text: '',
        ast: [],
        version: 0
      }
      return []
    }

    try {
      if (content.startsWith(this.cache.text) && this.cache.text !== '') {
        // 增量解析：内容是缓存内容的扩展
        return this.incrementalParse(content)
      } else {
        // 全量解析：内容与缓存不同或首次解析
        const ast = marked.lexer(content)
        this.updateCache(content, ast)
        return ast
      }
    } catch (error) {
      console.error('AST 解析错误:', error)
      return []
    }
  }

  /**
   * 增量解析
   * @param {string} newContent 新的内容
   * @returns {Array} 解析后的 AST
   */
  incrementalParse(newContent) {
    // 对于复杂的 Markdown 结构，使用全量解析
    const newAst = marked.lexer(newContent)
    
    // 更新缓存
    this.updateCache(newContent, newAst)
    return newAst
  }

  /**
   * 更新缓存
   * @param {string} content 内容
   * @param {Array} ast AST
   */
  updateCache(content, ast) {
    this.cache = {
      text: content,
      ast: ast
    }
  }

  /**
   * 获取缓存的 AST
   * @returns {Array} 缓存的 AST
   */
  getCachedAst() {
    return this.cache.ast
  }

  /**
   * 获取缓存的文本
   * @returns {string} 缓存的文本
   */
  getCachedText() {
    return this.cache.text
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.cache = {
      text: '',
      ast: [],
      version: 0
    }
  }

  /**
   * 遍历 AST 节点
   * @param {Array} ast AST 节点数组
   * @param {Function} callback 回调函数
   */
  traverse(ast, callback) {
    if (!Array.isArray(ast)) return
    
    ast.forEach((node, index) => {
      callback(node, index, ast)
      
      // 递归遍历子节点
      if (node.tokens && Array.isArray(node.tokens)) {
        this.traverse(node.tokens, callback)
      }
      
      if (node.items && Array.isArray(node.items)) {
        node.items.forEach(item => {
          if (item.tokens && Array.isArray(item.tokens)) {
            this.traverse(item.tokens, callback)
          }
        })
      }
    })
  }

  /**
   * 查找特定类型的节点
   * @param {Array} ast AST 节点数组
   * @param {string} type 节点类型
   * @returns {Array} 找到的节点数组
   */
  findNodesByType(ast, type) {
    const nodes = []
    
    this.traverse(ast, (node) => {
      if (node.type === type) {
        nodes.push(node)
      }
    })
    
    return nodes
  }

  /**
   * 检查 AST 是否包含特定类型的节点
   * @param {Array} ast AST 节点数组
   * @param {string} type 节点类型
   * @returns {boolean} 是否包含
   */
  hasNodeType(ast, type) {
    let found = false
    
    this.traverse(ast, (node) => {
      if (node.type === type) {
        found = true
      }
    })
    
    return found
  }
}

/**
 * 创建 AST 解析器实例
 * @returns {AstParser} 解析器实例
 */
export function createAstParser() {
  return new AstParser()
}
