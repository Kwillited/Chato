/**
 * 复制功能
 * 负责处理代码复制功能
 */

// 跟踪事件监听器是否已添加
let copyHandlerAdded = false

/**
 * 复制文本到剪贴板
 * @param {string} text 要复制的文本
 * @returns {Promise<void>}
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (error) {
    console.error('复制失败:', error)
    return false
  }
}

/**
 * 设置复制功能处理
 */
export function setupCopyHandler() {
  // 避免重复添加事件监听器
  if (!copyHandlerAdded) {
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
    
    copyHandlerAdded = true
    console.log('CopyFeature 已设置')
  }
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
      const success = await copyToClipboard(codeText)
      
      if (success) {
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
    }
  } catch (error) {
    console.error('复制失败:', error)
  }
}
