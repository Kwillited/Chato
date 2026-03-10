import { h } from 'vue'

/**
 * DOM 工具
 * 提供 DOM 操作相关的工具函数
 */

/**
 * 通用 XML 解析方法
 * @param {string} xmlString XML 字符串
 * @param {string} mimeType MIME 类型
 * @param {string} rootSelector 根元素选择器
 * @returns {Element|null} 解析后的元素
 */
function parseXmlString(xmlString, mimeType, rootSelector) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(xmlString, mimeType)
  // 检查是否解析成功
  const parserError = doc.querySelector('parsererror')
  if (parserError) {
    console.error(`${mimeType} 解析错误:`, parserError.textContent)
    return null
  }
  return doc.querySelector(rootSelector)
}

/**
 * 解析 HTML 字符串为 DOM 元素
 * @param {string} htmlString HTML 字符串
 * @returns {Element|null} DOM 元素
 */
export function parseHtmlString(htmlString) {
  return parseXmlString(htmlString, 'text/html', 'body')
}

/**
 * 递归转换 DOM 元素为 VNode
 * @param {Node} element DOM 元素
 * @param {string} key 节点键
 * @returns {any} VNode 或文本
 */
export function convertElementToVNode(element, key) {
  if (element.nodeType === Node.TEXT_NODE) {
    return element.textContent
  } else if (element.nodeType === Node.ELEMENT_NODE) {
    const props = { key }
    
    // 处理属性
    for (let i = 0; i < element.attributes.length; i++) {
      const attr = element.attributes[i]
      props[attr.name] = attr.value
    }
    
    // 处理样式
    if (element.style) {
      props.style = {}
      for (let i = 0; i < element.style.length; i++) {
        const property = element.style[i]
        props.style[property] = element.style[property]
      }
    }
    
    // 处理子节点
    const children = Array.from(element.childNodes).map((child, index) => 
      convertElementToVNode(child, `${key}-child-${index}`)
    ).filter(child => child !== null && child !== '')
    
    // 创建 VNode
    return h(element.tagName.toLowerCase(), props, children)
  }
  return null
}

/**
 * 解析 SVG 字符串为 DOM 元素
 * @param {string} svgString SVG 字符串
 * @returns {Element|null} SVG 元素
 */
export function parseSvgString(svgString) {
  return parseXmlString(svgString, 'image/svg+xml', 'svg')
}
