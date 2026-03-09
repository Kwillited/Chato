import katex from 'katex'

export const processMathFormulasInText = (text) => {
  if (!text) return [text];
  
  const parts = text.split(/(\\\[[\s\S]*?\\\]|\$\$[\s\S]*?\$\$|\\\([\s\S]*?\\\)|\$[\s\S]*?\$)/g);
  
  const result = [];
  
  parts.forEach((part, index) => {
    if (!part) return;
    
    if (part.startsWith('\\[') && part.endsWith('\\]')) {
      const latex = part.slice(2, -2).trim();
      try {
        const html = katex.renderToString(latex, {
          throwOnError: false,
          displayMode: true,
          output: 'htmlAndMathml'
        });
        result.push(html);
      } catch (error) {
        console.error('KaTeX 块级公式渲染错误:', error);
        result.push(part);
      }
    } else if (part.startsWith('$$') && part.endsWith('$$')) {
      const latex = part.slice(2, -2).trim();
      try {
        const html = katex.renderToString(latex, {
          throwOnError: false,
          displayMode: true,
          output: 'htmlAndMathml'
        });
        result.push(html);
      } catch (error) {
        console.error('KaTeX 块级公式渲染错误:', error);
        result.push(part);
      }
    } else if (part.startsWith('\\(') && part.endsWith('\\)')) {
      const latex = part.slice(2, -2).trim();
      try {
        const html = katex.renderToString(latex, {
          throwOnError: false,
          displayMode: false,
          output: 'htmlAndMathml'
        });
        result.push(html);
      } catch (error) {
        console.error('KaTeX 行内公式渲染错误:', error);
        result.push(part);
      }
    } else if (part.startsWith('$') && part.endsWith('$')) {
      const latex = part.slice(1, -1).trim();
      try {
        const html = katex.renderToString(latex, {
          throwOnError: false,
          displayMode: false,
          output: 'htmlAndMathml'
        });
        result.push(html);
      } catch (error) {
        console.error('KaTeX 行内公式渲染错误:', error);
        result.push(part);
      }
    } else {
      result.push(part);
    }
  });
  
  return result;
}
