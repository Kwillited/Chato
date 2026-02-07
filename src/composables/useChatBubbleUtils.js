import { ref, computed, watch, onMounted, nextTick } from 'vue'

/**
 * 聊天气泡工具函数组合式API
 * 管理思考内容展开/折叠、工具执行状态等逻辑
 */
export function useChatBubbleUtils(props) {
  // 思考内容展开状态 - 流式渲染时默认展开，历史消息默认折叠
  const isThinkingExpanded = ref(false)

  // 初始化时检查思考内容
  const initThinkingExpanded = () => {
    // 检查消息中的思考内容和状态
    const message = props.message?.value || props.message || {}
    // 历史消息默认折叠，流式渲染默认展开
    if (message.thinking) {
      // 只有当消息状态是 "streaming" 时才默认展开
      // 其他所有情况（包括历史消息）都默认折叠
      if (message.status === 'streaming') {
        isThinkingExpanded.value = true
      } else {
        isThinkingExpanded.value = false
      }
    }
  }

  // 组件挂载时初始化
  onMounted(() => {
    // 使用 nextTick 确保消息数据已经完全加载
    nextTick(() => {
      initThinkingExpanded()
    })
  })

  // 监听消息变化，检查思考内容完成标志
  watch(() => props.message, (newMessage) => {
    // 检查新消息中的思考内容完成标志
    const message = newMessage?.value || newMessage || {}
    if (message.thinkingCompleted === true) {
      isThinkingExpanded.value = false
    }
    // 检查新消息状态和思考内容
    if (message.thinking) {
      // 只有流式渲染的消息才展开
      if (message.status === 'streaming') {
        isThinkingExpanded.value = true
      } else {
        isThinkingExpanded.value = false
      }
    }
  }, { deep: true })

  // 切换思考内容展开/折叠状态
  const toggleThinkingExpanded = () => {
    isThinkingExpanded.value = !isThinkingExpanded.value
  }

  // 计算思考内容的高度类名
  const thinkingContentHeightClass = computed(() => {
    return isThinkingExpanded.value ? '' : 'max-h-10'
  })

  // 解析内容中的工具执行信息
  const parseToolExecutions = (content) => {
    if (!content) return []
    
    const toolExecutions = []
    const toolStartRegex = /\[工具执行开始\] 工具: ([^,]+), 输入: ([^\n]+)/g
    const toolEndRegex = /\[工具执行完成\] 工具: ([^,]+), 输出: ([^\n]+)/g
    
    let match
    while ((match = toolStartRegex.exec(content)) !== null) {
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
    
    while ((match = toolEndRegex.exec(content)) !== null) {
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
    
    return toolExecutions
  }

  // 提取非工具执行信息的内容
  const extractNonToolContent = (content) => {
    if (!content) return content
    
    // 移除工具执行信息
    return content
      .replace(/\[工具执行开始\] 工具: [^,]+, 输入: [^\n]+/g, '')
      .replace(/\[工具执行完成\] 工具: [^,]+, 输出: [^\n]+/g, '')
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
      'think': '思考',
      'analyze': '分析',
      'execute_tools': '执行工具',
      'default': '默认'
    }
    return nodeLabels[node] || node
  }

  return {
    isThinkingExpanded,
    initThinkingExpanded,
    toggleThinkingExpanded,
    thinkingContentHeightClass,
    parseToolExecutions,
    extractNonToolContent,
    getEventLabel,
    getNodeLabel
  }
}
