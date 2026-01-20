import { computed } from 'vue'
import { marked } from '../plugins/markdown.js'
import { copyToClipboard } from '../store/utils.js'

/**
 * 聊天气泡组件的公共逻辑
 */
export function useChatBubble(props) {
  // 访问ref包装的消息对象
  const messageValue = computed(() => {
    return props.message?.value || props.message || {}
  })

  // 获取消息内容
  const messageContent = computed(() => {
    return messageValue.value.content || messageValue.value.text || ''
  })

  // 格式化消息内容（支持Markdown）
  const formattedContent = computed(() => {
    if (!messageContent.value) return ''

    // 处理AI回复中的思考标签（</think>）
    let contentToParse = messageContent.value;
    const thinkingTagRegex = /^\s*<think>[\s\S]*?<\/think>\s*/;
    contentToParse = contentToParse.replace(thinkingTagRegex, '');
    
    // 使用集中化配置的marked库转换Markdown为HTML
    try {
      return marked.parse(contentToParse);
    } catch (error) {
      console.error('Markdown解析错误:', error);
      return contentToParse.replace(/\n/g, '<br>');
    }
  })

  // 用于触发更新的key值
  const updateKey = computed(() => {
    return `${messageContent.value.length}-${messageValue.value.lastUpdate || Date.now()}`
  })

  // 复制消息内容到剪贴板
  const copyMessageContent = async () => {
    try {
      // 移除思考标签（</think>和</think>）后再复制
      let contentToCopy = messageContent.value;
      const thinkingTagRegex = /^\s*<think>[\s\S]*?<\/think>\s*/;
      contentToCopy = contentToCopy.replace(thinkingTagRegex, '');
      await copyToClipboard(contentToCopy)
    } catch (error) {
      console.error('复制失败:', error)
    }
  }

  // 复制代码到剪贴板
  const copyCodeToClipboard = async (codeBlockId) => {
    try {
      const codeElement = document.getElementById(codeBlockId);
      if (codeElement) {
        const codeText = codeElement.textContent;
        await copyToClipboard(codeText);
        
        // 更改复制按钮图标为成功状态
        const button = document.querySelector(`button[data-code-block-id="${codeBlockId}"]`);
        if (button) {
          const originalIcon = button.innerHTML;
          button.innerHTML = '<i class="fa-solid fa-check"></i>';
          button.classList.add('text-green-400');
          
          // 2秒后恢复原状
          setTimeout(() => {
            button.innerHTML = originalIcon;
            button.classList.remove('text-green-400');
          }, 2000);
        }
      }
    } catch (error) {
      console.error('复制代码失败:', error);
    }
  };

  // 格式化思考内容
  const formatThinkingContent = (thinking) => {
    if (!thinking) return ''
    
    // 简单的换行处理
    return thinking.replace(/\n/g, '<br>')
  }

  return {
    messageValue,
    messageContent,
    formattedContent,
    updateKey,
    copyMessageContent,
    copyCodeToClipboard,
    formatThinkingContent
  }
}