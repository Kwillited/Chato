import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { marked } from '../../../plugins/markdown.js'
import { copyToClipboard } from '../../../shared/utils/helpers.js'
import { useNotifications } from './useNotifications.js'
import logger from '../../../shared/utils/logger.js'

/**
 * 聊天气泡组件的公共逻辑
 */
export function useChatBubble(props) {
  // 使用通知管理组合函数（在函数内部调用，避免模块加载时调用）
  const { showSystemNotification } = useNotifications();
  // 访问ref包装的消息对象
  const messageValue = computed(() => {
    // 更严格的类型检查，确保返回有效的消息对象
    const message = props.message?.value || props.message || {}
    return {
      id: message.id || '',
      role: message.role || 'ai',
      content: message.content || message.text || '',
      timestamp: message.timestamp || Date.now(),
      error: message.error || '',
      isTyping: message.isTyping || false,
      lastUpdate: message.lastUpdate || Date.now(),
      ...message
    }
  })

  // 获取消息内容
  const messageContent = computed(() => {
    return messageValue.value.content || messageValue.value.text || ''
  })

  // 正则表达式常量，避免重复创建
  const THINKING_TAG_REGEX = /^\s*<think>[\s\S]*?<\/think>\s*/;

  // 缓存计算结果，避免重复解析相同内容
  const formattedContentCache = ref(new Map())

  // 格式化消息内容（支持Markdown）
  const formattedContent = computed(() => {
    const content = messageContent.value
    if (!content) return ''

    // 生成缓存key
    const cacheKey = `${content}-${messageValue.value.lastUpdate}`
    
    // 如果缓存中存在，直接返回
    if (formattedContentCache.value.has(cacheKey)) {
      return formattedContentCache.value.get(cacheKey)
    }

    // 处理AI回复中的思考标签
    let contentToParse = content.replace(THINKING_TAG_REGEX, '');
    
    // 使用集中化配置的marked库转换Markdown为HTML
    let parsedContent = ''
    try {
      parsedContent = marked.parse(contentToParse);
    } catch (error) {
      logger.error('Markdown解析错误:', error);
      parsedContent = contentToParse.replace(/\n/g, '<br>');
    }
    
    // 缓存结果
    formattedContentCache.value.set(cacheKey, parsedContent)
    
    // 限制缓存大小，防止内存泄漏
    if (formattedContentCache.value.size > 50) {
      // 删除最早的缓存项
      const firstKey = formattedContentCache.value.keys().next().value
      formattedContentCache.value.delete(firstKey)
    }
    
    return parsedContent
  })

  // 用于触发更新的key值
  const updateKey = computed(() => {
    return `${messageContent.value.length}-${messageValue.value.lastUpdate || Date.now()}`
  })

  // 复制消息内容到剪贴板
  const copyMessageContent = async () => {
    try {
      // 移除思考标签后再复制
      const contentToCopy = messageContent.value.replace(THINKING_TAG_REGEX, '');
      await copyToClipboard(contentToCopy)
      // 显示复制成功通知
      showSystemNotification('消息内容已复制到剪贴板', 'success')
    } catch (error) {
      logger.error('复制失败:', error)
      // 显示复制失败通知
      showSystemNotification('复制失败，请重试', 'error')
    }
  }

  // 复制代码到剪贴板的状态管理
  const copyButtonStates = ref(new Map())

  // 复制代码到剪贴板，支持两种模式：1. 提供codeText 2. 自动查找code元素
  const copyCodeToClipboard = async (codeBlockId, codeText = null) => {
    try {
      let textToCopy = codeText;
      
      // 如果没有提供codeText，尝试查找DOM元素获取
      if (!textToCopy) {
        const codeElement = document.getElementById(codeBlockId);
        if (codeElement) {
          textToCopy = codeElement.textContent;
        }
      }
      
      if (textToCopy) {
        await copyToClipboard(textToCopy);
        
        // 更新复制按钮状态
        copyButtonStates.value.set(codeBlockId, true)
        
        // 显示复制成功通知
        showSystemNotification('代码已复制到剪贴板', 'success')
        
        // 2秒后恢复原状
        setTimeout(() => {
          copyButtonStates.value.delete(codeBlockId)
        }, 2000);
      }
    } catch (error) {
      logger.error('复制代码失败:', error);
      // 显示复制失败通知
      showSystemNotification('复制代码失败，请重试', 'error')
    }
  };

  // 格式化思考内容
  const formatThinkingContent = (thinking) => {
    if (!thinking) return ''
    
    // 简单的换行处理
    return thinking.replace(/\n/g, '<br>')
  }

  // 监听消息变化，清理旧的缓存
  watch(() => props.message, () => {
    // 清理超过100项的缓存，防止内存泄漏
    if (formattedContentCache.value.size > 100) {
      formattedContentCache.value.clear()
    }
  }, { deep: true })

  return {
    messageValue,
    messageContent,
    formattedContent,
    updateKey,
    copyMessageContent,
    copyCodeToClipboard,
    formatThinkingContent,
    copyButtonStates
  }
}