import { computed, ref, watch, onMounted, onUnmounted, nextTick, inject } from 'vue'
import { useNotification } from './useNotification.js'

/**
 * 聊天气泡组件的公共逻辑
 */
export function useChatBubble(props) {
  // 使用通知组合式函数
  const { showSuccess, showError } = useNotification();

  // 注入复制功能
  const copyUtils = inject('copyUtils', null);

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

  // 格式化消息内容（现在由 MarkdownRender 组件处理）
  const formattedContent = computed(() => {
    return messageContent.value
  })

  // 用于触发更新的key值
  const updateKey = computed(() => {
    return `${messageContent.value.length}-${messageValue.value.lastUpdate || Date.now()}`
  })

  // 复制消息内容到剪贴板
  const copyMessageContent = async () => {
    try {
      // 直接复制内容
      const contentToCopy = messageContent.value;
      
      // 使用注入的复制功能或降级到本地实现
      if (copyUtils && copyUtils.copyMarkdown) {
        await copyUtils.copyMarkdown(contentToCopy)
      } else {
        // 降级方案：直接使用 navigator.clipboard
        await navigator.clipboard.writeText(contentToCopy)
      }
      
      // 显示复制成功通知
      showSuccess('消息内容已复制到剪贴板')
    } catch (error) {
      console.error('复制失败:', error)
      // 显示复制失败通知
      showError('复制失败，请重试')
    }
  }

  // 格式化思考内容
  const formatThinkingContent = (reasoning_content) => {
    if (!reasoning_content) return ''
    
    // 简单的换行处理
    return reasoning_content.replace(/\n/g, '<br>')
  }

  // 监听消息变化
  watch(() => props.message, () => {
    // 检查新消息中的思考内容完成标志
    const message = props.message?.value || props.message || {}
    if (message.thinkingCompleted === true) {
      isReasoningExpanded.value = false
    }
    // 检查新消息状态和思考内容
    if (message.reasoning_content) {
      // 只有流式渲染的消息才展开
      if (message.status === 'streaming') {
        isReasoningExpanded.value = true
      } else {
        isReasoningExpanded.value = false
      }
    }
  }, { deep: true })

  // 组件挂载时初始化
  onMounted(() => {
    // 初始化思考内容展开状态
    initReasoningExpanded();
  });

  // 思考内容展开状态 - 流式渲染时默认展开，历史消息默认折叠
  const isReasoningExpanded = ref(false)

  // 初始化时检查思考内容
  const initReasoningExpanded = () => {
    // 检查消息中的思考内容和状态
    const message = props.message?.value || props.message || {}
    // 历史消息默认折叠，流式渲染默认展开
    if (message.reasoning_content) {
      // 只有当消息状态是 "streaming" 时才默认展开
      // 其他所有情况（包括历史消息）都默认折叠
      if (message.status === 'streaming') {
        isReasoningExpanded.value = true
      } else {
        isReasoningExpanded.value = false
      }
    }
  }

  // 监听消息变化，检查思考内容完成标志
  watch(() => props.message, (newMessage) => {
    // 检查新消息中的思考内容完成标志
    const message = newMessage?.value || newMessage || {}
    if (message.thinkingCompleted === true) {
      isReasoningExpanded.value = false
    }
    // 检查新消息状态和思考内容
    if (message.reasoning_content) {
      // 只有流式渲染的消息才展开
      if (message.status === 'streaming') {
        isReasoningExpanded.value = true
      } else {
        isReasoningExpanded.value = false
      }
    }
  }, { deep: true })

  // 切换思考内容展开/折叠状态
  const toggleReasoningExpanded = () => {
    isReasoningExpanded.value = !isReasoningExpanded.value
  }

  // 计算思考内容的高度类名
  const reasoningContentHeightClass = computed(() => {
    return isReasoningExpanded.value ? '' : 'max-h-10'
  })

  // 解析内容中的工具执行信息
  const parseToolExecutions = (content) => {
    if (!content) return []
    
    const toolExecutions = []
    // 支持两种格式的工具执行信息
    const toolStartRegex1 = /\[工具执行开始\] 工具: ([^,]+), 输入: ([^\n]+)/g
    const toolEndRegex1 = /\[工具执行完成\] 工具: ([^,]+), 输出: ([^\n]+)/g
    const toolStartRegex2 = /\[工具 \d+ 开始\] 工具: ([^,]+), 输入: ([^\n]+)/g
    const toolEndRegex2 = /\[工具 \d+ 完成\] 工具: ([^,]+), 输出: ([^\n]+)/g
    
    let match
    // 处理第一种格式
    while ((match = toolStartRegex1.exec(content)) !== null) {
      const [, toolName, inputStr] = match
      try {
        // 尝试解析输入参数
        const input = JSON.parse(inputStr.replace(/'/g, '"'))
        toolExecutions.push({
          name: toolName.trim(),
          status: 'executing',
          input
        })
      } catch (e) {
        console.error('解析工具输入参数失败:', e)
      }
    }
    
    while ((match = toolEndRegex1.exec(content)) !== null) {
      const [, toolName, outputStr] = match
      try {
        // 尝试解析输出结果
        const output = JSON.parse(outputStr.replace(/'/g, '"'))
        // 查找对应的执行中工具，更新其状态
        const existingTool = toolExecutions.find(t => t.name === toolName.trim() && t.status === 'executing')
        if (existingTool) {
          existingTool.status = 'executed'
          existingTool.output = output
        } else {
          // 如果没有找到对应的执行中工具，创建一个新的
          toolExecutions.push({
            name: toolName.trim(),
            status: 'executed',
            output
          })
        }
      } catch (e) {
        console.error('解析工具输出结果失败:', e)
      }
    }
    
    // 处理第二种格式（历史消息格式）
    while ((match = toolStartRegex2.exec(content)) !== null) {
      const [, toolName, inputStr] = match
      try {
        // 尝试解析输入参数
        const input = JSON.parse(inputStr.replace(/'/g, '"'))
        toolExecutions.push({
          name: toolName.trim(),
          status: 'executing',
          input
        })
      } catch (e) {
        console.error('解析工具输入参数失败:', e)
        // 即使解析失败，也要添加工具执行状态，只是没有输入参数
        toolExecutions.push({
          name: toolName.trim(),
          status: 'executing'
        })
      }
    }
    
    while ((match = toolEndRegex2.exec(content)) !== null) {
      const [, toolName, outputStr] = match
      try {
        // 尝试解析输出结果
        const output = JSON.parse(outputStr.replace(/'/g, '"'))
        // 查找对应的执行中工具，更新其状态
        const existingTool = toolExecutions.find(t => t.name === toolName.trim() && t.status === 'executing')
        if (existingTool) {
          existingTool.status = 'executed'
          existingTool.output = output
        } else {
          // 如果没有找到对应的执行中工具，创建一个新的
          toolExecutions.push({
            name: toolName.trim(),
            status: 'executed',
            output
          })
        }
      } catch (e) {
        console.error('解析工具输出结果失败:', e)
        // 即使解析失败，也要更新工具执行状态，只是没有输出参数
        const existingTool = toolExecutions.find(t => t.name === toolName.trim() && t.status === 'executing')
        if (existingTool) {
          existingTool.status = 'executed'
        } else {
          // 如果没有找到对应的执行中工具，创建一个新的
          toolExecutions.push({
            name: toolName.trim(),
            status: 'executed'
          })
        }
      }
    }
    
    return toolExecutions
  }

  // 提取非工具执行信息的内容
  const extractNonToolContent = (content) => {
    if (!content) return content
    
    // 移除工具执行信息
    return content
      .replace(/\[工具执行开始\] 工具: [^,]+, 输入: [^\n]+/g, '')
      .replace(/\[工具执行完成\] 工具: [^,]+, 输出: [^\n]+/g, '')
      .replace(/\[工具 \d+ 开始\] 工具: [^,]+, 输入: [^<]+/g, '')
      .replace(/\[工具 \d+ 完成\] 工具: [^,]+, 输出: [^<]+/g, '')
      .replace(/\[工具调用计划\] 工具: [^,]+, 参数: [^\n]+/g, '')
      .trim()
  }

  // 获取事件类型标签
  const getEventLabel = (event) => {
    const eventLabels = {
      'on_chat_model_stream': 'AI 模型流',
      'on_chat_model_end': 'AI 模型结束',
      'text': '文本消息',
      'tool_call': '工具调用',
      'tool_response': '工具响应'
    }
    return eventLabels[event] || event
  }

  // 获取节点类型标签
  const getNodeLabel = (node) => {
    const nodeLabels = {
      'reasoning': '推理',
      'execute': '执行',
      'reflect': '反思',
      'default': '默认'
    }
    return nodeLabels[node] || node
  }

  return {
    messageValue,
    messageContent,
    formattedContent,
    updateKey,
    copyMessageContent,
    formatThinkingContent,
    // 添加从 useChatBubbleUtils 合并的功能
    isReasoningExpanded,
    initReasoningExpanded,
    toggleReasoningExpanded,
    reasoningContentHeightClass,
    parseToolExecutions,
    extractNonToolContent,
    getEventLabel,
    getNodeLabel
  }
}