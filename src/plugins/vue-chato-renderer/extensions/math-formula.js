import katex from 'katex'
import 'katex/dist/katex.min.css'

/**
 * 渲染数学公式
 * @param {string} latex LaTeX 公式
 * @param {Object} options 渲染选项
 * @returns {string} 渲染后的 HTML
 */
export function renderMathFormula(latex, options = {}) {
  const defaultOptions = {
    throwOnError: false,
    displayMode: false,
    output: 'htmlAndMathml'
  };
  
  const renderOptions = { ...defaultOptions, ...options };
  
  try {
    return katex.renderToString(latex, renderOptions);
  } catch (error) {
    console.error('KaTeX 公式渲染错误:', error);
    return latex;
  }
}

/**
 * 处理文本中的数学公式
 * @param {string} text 包含数学公式的文本
 * @returns {Array} 处理后的文本片段数组
 */
export function processMathFormulasInText(text) {
  if (!text) return [text];
  
  // 长分隔符优先：块级公式先匹配
  // 使用 [\s\S]*? 来匹配包括换行符在内的所有字符
  const parts = text.split(/(\\\[[\s\S]*?\\\]|\$\$[\s\S]*?\$\$|\\\([\s\S]*?\\\)|\$[\s\S]*?\$)/g);
  
  const result = [];
  
  parts.forEach((part) => {
    if (!part) return; // 跳过空字符串
    
    let latex, displayMode = false;
    
    // 块级公式：\[...\]
    if (part.startsWith('\\[') && part.endsWith('\\]')) {
      latex = part.slice(2, -2).trim();
      displayMode = true;
    }
    // 块级公式：$$...$$
    else if (part.startsWith('$$') && part.endsWith('$$')) {
      latex = part.slice(2, -2).trim();
      displayMode = true;
    }
    // 行内公式：\(...\)
    else if (part.startsWith('\\(') && part.endsWith('\\)')) {
      latex = part.slice(2, -2).trim();
      displayMode = false;
    }
    // 行内公式：$...$
    else if (part.startsWith('$') && part.endsWith('$')) {
      latex = part.slice(1, -1).trim();
      displayMode = false;
    }
    
    if (latex !== undefined) {
      try {
        const html = renderMathFormula(latex, { displayMode });
        result.push(html);
      } catch (error) {
        console.error('KaTeX 公式渲染错误:', error);
        result.push(part); // 降级显示原始文本
      }
    } else {
      // 普通文本直接返回字符串，Vue 会处理成文本节点
      result.push(part);
    }
  });
  
  return result;
}
