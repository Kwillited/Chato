import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { marked } from 'marked'
import { copyToClipboard } from '../utils/browser.js'
import { useNotification } from './useNotification.js'

// 配置 marked 选项
const renderer = new marked.Renderer();

// 自定义代码块渲染
renderer.code = function(code, language) {
  // 处理可能的AST节点
  let actualCode = code;
  let actualLanguage = language;
  
  // 如果code是对象，尝试提取实际的代码内容
  if (typeof code === 'object' && code !== null) {
    // 检查是否是marked的AST节点
    if (code.type === 'code') {
      actualCode = code.text || code.raw || '';
      actualLanguage = code.lang || language;
    } else {
      // 其他对象，转换为JSON字符串
      actualCode = JSON.stringify(code, null, 2);
    }
  } else if (typeof code !== 'string') {
    // 非字符串非对象，转换为字符串
    actualCode = String(code);
  }
  
  // 如果没有语言或语言为'text'，则显示为'plaintext'
  const displayLanguage = actualLanguage && actualLanguage !== 'text' ? actualLanguage : 'plaintext';
  
  // 创建唯一ID用于复制功能
  const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  // 返回带头部的代码块HTML
  return `
    <div class="code-container">
      <div class="code-header">
        <span class="code-language">${displayLanguage}</span>
        <button 
          class="copy-code-btn"
          data-code-block-id="${codeBlockId}"
          title="复制代码"
        >
          <i class="fa-solid fa-copy"></i>
        </button>
      </div>
      <pre><code id="${codeBlockId}">${actualCode}</code></pre>
    </div>
  `;
};

// 设置 marked 配置
marked.setOptions({
  renderer: renderer,
  breaks: true,
  gfm: true
});

/**
 * 聊天气泡组件的公共逻辑
 */
export function useChatBubble(props) {
  // 使用通知组合式函数
  const { showSuccess, showError } = useNotification();

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

  // 格式化消息内容（支持Markdown）
  const formattedContent = computed(() => {
    const content = messageContent.value
    if (!content) return ''

    console.log('原始Markdown内容:', content);

    // 使用集中化配置的marked库转换Markdown为HTML
    let parsedContent = ''
    try {
      console.log('调用marked解析Markdown');
      // 直接使用marked函数解析
      parsedContent = marked(content);
      console.log('Markdown解析结果:', parsedContent);
    } catch (error) {
      console.error('Markdown解析错误:', error);
      parsedContent = content.replace(/\n/g, '<br>');
      console.log('错误处理后的内容:', parsedContent);
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
      // 直接复制内容
      const contentToCopy = messageContent.value;
      await copyToClipboard(contentToCopy)
      // 显示复制成功通知
      showSuccess('消息内容已复制到剪贴板')
    } catch (error) {
      console.error('复制失败:', error)
      // 显示复制失败通知
      showError('复制失败，请重试')
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
        showSuccess('代码已复制到剪贴板')
        
        // 2秒后恢复原状
        setTimeout(() => {
          copyButtonStates.value.delete(codeBlockId)
        }, 2000);
      }
    } catch (error) {
      console.error('复制代码失败:', error);
      // 显示复制失败通知
      showError('复制代码失败，请重试')
    }
  };

  // 格式化思考内容
  const formatThinkingContent = (reasoning_content) => {
    if (!reasoning_content) return ''
    
    // 简单的换行处理
    return reasoning_content.replace(/\n/g, '<br>')
  }

  // 初始化复制按钮事件监听器
  const initCopyButtons = () => {
    // 等待DOM更新完成后添加事件监听器
    setTimeout(() => {
      const copyButtons = document.querySelectorAll('.copy-code-btn');
      copyButtons.forEach(button => {
        // 移除已有的事件监听器，避免重复绑定
        button.removeEventListener('click', handleCopyButtonClick);
        // 添加新的事件监听器
        button.addEventListener('click', handleCopyButtonClick);
      });
    }, 0);
  };

  // 处理复制按钮点击事件
  const handleCopyButtonClick = (event) => {
    const button = event.currentTarget;
    const codeBlockId = button.getAttribute('data-code-block-id');
    if (codeBlockId) {
      copyCodeToClipboard(codeBlockId);
    }
  };

  // 监听消息变化，清理旧的缓存并重新初始化复制按钮
  watch(() => props.message, () => {
    // 由于移除了缓存机制，这里不再需要清理缓存
    // 重新初始化复制按钮事件监听器
    initCopyButtons();
  }, { deep: true })

  // 组件挂载时初始化复制按钮
  onMounted(() => {
    initCopyButtons();
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
    copyCodeToClipboard,
    formatThinkingContent,
    copyButtonStates,
    initCopyButtons,
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