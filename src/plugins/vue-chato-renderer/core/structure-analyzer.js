/**
 * 结构分析器
 * 负责分析 Markdown 文本和 AST 的结构，提供统一的结构表示
 */
export class StructureAnalyzer {
  /**
   * 从 Markdown 文本分析结构
   * @param {string} text Markdown 文本
   * @returns {Object} 结构分析结果
   */
  analyzeFromText(text) {
    const blocks = []
    let currentBlock = null
    let blockStart = 0
    
    // 按行分析
    const lines = text.split('\n')
    lines.forEach((line, index) => {
      const lineStart = text.indexOf(line, blockStart)
      const lineEnd = lineStart + line.length
      
      // 检测块类型
      const blockType = this.detectBlockTypeFromText(line)
      
      if (blockType !== currentBlock?.type) {
        if (currentBlock) {
          currentBlock.end = blockStart
          blocks.push(currentBlock)
        }
        
        currentBlock = {
          type: blockType,
          start: lineStart,
          end: lineEnd,
          content: line,
          lines: [line]
        }
      } else {
        currentBlock.end = lineEnd
        currentBlock.content += '\n' + line
        currentBlock.lines.push(line)
      }
      
      blockStart = lineEnd + 1
    })
    
    if (currentBlock) {
      currentBlock.end = text.length
      blocks.push(currentBlock)
    }
    
    return {
      blocks,
      length: text.length
    }
  }
  
  /**
   * 从 AST 分析结构
   * @param {Array} ast AST 结构
   * @returns {Object} 结构分析结果
   */
  analyzeFromAst(ast) {
    const blocks = []
    let position = 0
    
    ast.forEach((node, index) => {
      const block = {
        type: node.type,
        start: position,
        end: position + (node.raw?.length || 0),
        content: node.raw || '',
        node: node
      }
      
      // 处理不同类型的节点
      switch (node.type) {
        case 'heading':
          block.level = node.depth
          break
        case 'code':
          block.language = node.lang
          block.code = node.text
          break
        case 'list':
          block.ordered = node.ordered
          block.items = node.items?.length || 0
          break
        case 'table':
          block.header = node.header
          block.cells = node.cells
          break
      }
      
      blocks.push(block)
      position = block.end
    })
    
    return {
      blocks,
      length: position
    }
  }
  
  /**
   * 从文本检测块类型
   * @param {string} line 行文本
   * @returns {string} 块类型
   */
  detectBlockTypeFromText(line) {
    const trimmedLine = line.trim()
    
    // 检测代码块
    if (trimmedLine.startsWith('```')) {
      return 'code'
    }
    
    // 检测标题
    if (trimmedLine.startsWith('#')) {
      return 'heading'
    }
    
    // 检测引用
    if (trimmedLine.startsWith('>')) {
      return 'blockquote'
    }
    
    // 检测列表
    if (trimmedLine.match(/^\d+\./) || trimmedLine.match(/^[*+-]/)) {
      return 'list'
    }
    
    // 检测表格
    if (trimmedLine.match(/^\|.*\|$/)) {
      return 'table'
    }
    
    // 检测水平线
    if (trimmedLine.match(/^[-*_]{3,}$/)) {
      return 'hr'
    }
    
    // 检测任务列表
    if (trimmedLine.match(/^\s*[-*+]\s*\[([ xX])\]/)) {
      return 'list'
    }
    
    // 默认段落
    return 'paragraph'
  }
  
  /**
   * 检测 AST 节点类型
   * @param {Object} node AST 节点
   * @returns {string} 块类型
   */
  detectBlockTypeFromAst(node) {
    return node.type || 'text'
  }
  
  /**
   * 检查新结构是否是旧结构的扩展
   * @param {Object} oldStructure 旧结构
   * @param {Object} newStructure 新结构
   * @returns {boolean} 是否是扩展
   */
  isStructureExtension(oldStructure, newStructure) {
    if (!oldStructure || !oldStructure.blocks.length) {
      return false
    }
    
    const oldBlocks = oldStructure.blocks
    const newBlocks = newStructure.blocks
    
    // 检查旧结构的所有块是否都在新结构中
    for (let i = 0; i < oldBlocks.length; i++) {
      const oldBlock = oldBlocks[i]
      const newBlock = newBlocks[i]
      
      if (!newBlock || oldBlock.type !== newBlock.type) {
        return false
      }
    }
    
    return true
  }
  
  /**
   * 查找受影响的结构范围
   * @param {Object} oldStructure 旧结构
   * @param {Object} newStructure 新结构
   * @returns {Object} 受影响的范围
   */
  findAffectedRange(oldStructure, newStructure) {
    const oldBlocks = oldStructure.blocks
    const newBlocks = newStructure.blocks
    
    let affectedStart = 0
    let affectedEnd = newStructure.length
    
    // 找到第一个不同的块
    for (let i = 0; i < Math.min(oldBlocks.length, newBlocks.length); i++) {
      if (oldBlocks[i].type !== newBlocks[i].type) {
        affectedStart = oldBlocks[i].start
        break
      }
    }
    
    return {
      start: affectedStart,
      end: affectedEnd
    }
  }
}

/**
 * 创建结构分析器实例
 * @returns {StructureAnalyzer} 结构分析器实例
 */
export function createStructureAnalyzer() {
  return new StructureAnalyzer()
}
