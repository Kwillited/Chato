/**
 * SVG 工具
 * 提供 SVG 处理相关的工具函数
 */

import { parseSvgString as parseSvgStringUtil } from './dom-utils.js'

/**
 * 解析 SVG 字符串为 DOM 元素
 * @param {string} svgString SVG 字符串
 * @returns {Element|null} SVG 元素
 */
export function parseSvgString(svgString) {
  return parseSvgStringUtil(svgString)
}
