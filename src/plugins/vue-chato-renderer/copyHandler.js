import { copyToClipboard } from '../../utils/browser.js'

/**
 * 设置复制功能处理
 */
export function setupCopyHandler() {
  // 全局事件监听器
  document.addEventListener('click', (event) => {
    const copyButton = event.target.closest('.copy-code-btn')
    if (copyButton) {
      const codeBlockId = copyButton.getAttribute('data-code-block-id')
      if (codeBlockId) {
        handleCopyCode(codeBlockId, copyButton)
      }
    }
  })
  
  console.log('Chato Renderer 复制功能已设置')
}

/**
 * 处理代码复制
 * @param {string} codeBlockId 代码块ID
 * @param {HTMLElement} button 复制按钮元素
 */
async function handleCopyCode(codeBlockId, button) {
  try {
    const codeElement = document.getElementById(codeBlockId)
    if (codeElement) {
      const codeText = codeElement.textContent
      await copyToClipboard(codeText)
      
      // 显示复制成功状态
      button.classList.add('text-green-400')
      const originalIcon = button.innerHTML
      button.innerHTML = '<i class="fa-solid fa-check"></i>'
      
      // 2秒后恢复原状
      setTimeout(() => {
        button.classList.remove('text-green-400')
        button.innerHTML = originalIcon
      }, 2000)
    }
  } catch (error) {
    console.error('复制失败:', error)
  }
}
