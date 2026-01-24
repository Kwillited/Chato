<template>
  <div 
    class="w-full max-w-2xl bg-transparent dark:bg-transparent rounded-xl p-4 overflow-hidden"
    role="article"
    aria-label="AI聊天消息"
    aria-live="polite"
  >
    <!-- 使用v-memo优化渲染性能，只有当updateKey变化时才重新渲染 -->
    <div 
      class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed"
      v-memo="[updateKey, formattedContent]"
      v-html="formattedContent"
      @click="handleCopyCodeClick"
      role="region"
      aria-label="消息内容"
      tabindex="0"
      @keydown.enter="handleCopyCodeClick"
      @keydown.space="handleCopyCodeClick"
    ></div>
    
    <!-- 错误状态显示 -->
    <div 
      v-if="messageValue.error" 
      class="chat-error mt-2"
      v-memo="[messageValue.error]"
      role="alert"
      aria-live="assertive"
      aria-label="错误信息"
    >
      <i class="fa-solid fa-circle-exclamation text-red-500 mr-1" aria-hidden="true"></i>
      <span>{{ messageValue.error }}</span>
    </div>
    
    <!-- 旋转动画 -->
    <Loading 
      v-if="messageValue.isTyping" 
      type="spin" 
      size="small" 
      color="var(--text-color-secondary, #9ca3af)" 
      containerClass="mt-2"
      v-memo="[messageValue.isTyping]"
      aria-label="正在输入"
      role="status"
    />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import Loading from '../../common/Loading.vue'
// 导入聊天气泡公共逻辑
import { useChatBubble } from '../../../composables/useChatBubble.js'
import logger from '../../../utils/logger.js';

const props = defineProps({
  message: {
    type: [Object, Function], // 支持普通对象和ref包装的对象
    required: true,
    default: () => ({})
  }
})

// 使用公共聊天气泡逻辑
const { 
  messageValue, 
  formattedContent,
  updateKey,
  copyButtonStates,
  copyCodeToClipboard
} = useChatBubble(props)

// 复制按钮状态管理组合式函数
const useCopyButtonManager = () => {
  // 存储当前复制按钮状态，避免频繁DOM操作
  const currentCopiedButtons = ref(new Map())

  // 监听复制按钮状态变化，更新本地状态
  watch(copyButtonStates, (newStates) => {
    // 同步本地状态
    currentCopiedButtons.value.clear()
    newStates.forEach((isCopied, codeBlockId) => {
      currentCopiedButtons.value.set(codeBlockId, isCopied)
    })
  }, { deep: true })

  // 更新复制按钮状态
  const updateCopyButtonState = (button, isCopied) => {
    if (!button) return
    
    try {
      if (isCopied) {
        button.innerHTML = '<i class="fa-solid fa-check"></i>'
        button.classList.add('text-green-400')
      } else {
        button.innerHTML = '<i class="fa-solid fa-copy"></i>'
        button.classList.remove('text-green-400')
      }
    } catch (error) {
      logger.warn('更新复制按钮状态失败:', error)
    }
  }

  // 处理复制代码点击事件
  const handleCopyCodeClick = (event) => {
    const button = event.target.closest('button[data-code-block-id]')
    if (button) {
      const codeBlockId = button.dataset.codeBlockId
      // 查找对应的代码元素
      const codeElement = document.getElementById(codeBlockId)
      if (codeElement) {
        const codeText = codeElement.textContent
        copyCodeToClipboard(codeBlockId, codeText)
        
        // 更新按钮状态
        updateCopyButtonState(button, true)
        
        // 2秒后恢复原状
        setTimeout(() => {
          updateCopyButtonState(button, false)
        }, 2000)
      }
    }
  }

  return {
    currentCopiedButtons,
    handleCopyCodeClick,
    updateCopyButtonState
  }
}

// 使用复制按钮管理
const { handleCopyCodeClick } = useCopyButtonManager()
</script>

<style scoped>
/* 使用CSS变量统一管理样式 */
:deep(.markdown-content) {
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 错误提示样式 */
.chat-error {
  color: var(--error-color, #ef4444);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}

/* 代码容器样式优化 */
:deep(.code-container) {
  margin: 1rem 0;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

/* 代码块头部样式 */
:deep(.code-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: var(--code-header-bg, #f3f4f6);
  border-bottom: 1px solid var(--code-header-border, #e5e7eb);
  font-size: 0.75rem;
  font-weight: 500;
}

/* 代码语言标签样式 */
:deep(.code-language) {
  color: var(--code-language-color, #4b5563);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* 复制代码按钮样式 */
:deep(.copy-code-btn) {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--copy-btn-color, #6b7280);
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  /* 添加可访问性支持 - aria-label应在HTML中设置，此处移除 */
}

/* 复制代码按钮焦点样式 */
:deep(.copy-code-btn:focus) {
  outline: none;
  box-shadow: 0 0 0 2px blue-500;
}

/* 复制按钮悬停效果 */
:deep(.copy-code-btn:hover) {
  background-color: var(--copy-btn-hover-bg, #e5e7eb);
  color: var(--copy-btn-hover-color, #374151);
}

/* 复制成功状态 */
:deep(.copy-code-btn.text-green-400) {
  color: var(--copy-success-color, #10b981);
}

/* 代码块样式 */
:deep(.code-container pre) {
  margin: 0;
  background-color: var(--code-bg, #1f2937);
  overflow-x: auto;
  padding: 1rem;
}

/* 代码样式 */
:deep(.code-container code) {
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--code-text-color, #e5e7eb);
}

/* 响应式设计 */
@media (max-width: 768px) {
  /* 在平板和手机上调整样式 */
  :host {
    max-width: 100%;
    padding: 0 1rem;
  }
  
  .max-w-2xl {
    max-width: 100%;
  }
  
  .p-4 {
    padding: 1rem;
  }
  
  /* 调整代码块样式 */
  :deep(.code-container) {
    margin: 0.5rem 0;
  }
  
  :deep(.code-container pre) {
    padding: 0.75rem;
  }
  
  :deep(.code-container code) {
    font-size: 0.8125rem; /* 13px */
  }
}

@media (max-width: 480px) {
  /* 在手机上进一步调整样式 */
  .p-4 {
    padding: 0.75rem;
  }
  
  /* 调整代码块头部样式 */
  :deep(.code-header) {
    padding: 0.375rem 0.75rem;
    font-size: 0.6875rem; /* 11px */
  }
  
  /* 调整代码样式 */
  :deep(.code-container code) {
    font-size: 0.75rem; /* 12px */
    line-height: 1.4;
  }
}

/* 深色模式适配 - 使用CSS变量自动适配 */
@media (prefers-color-scheme: dark) {
  :deep(.code-header) {
    background-color: var(--code-header-dark-bg, #374151);
    border-bottom-color: var(--code-header-dark-border, #4b5563);
  }

  :deep(.code-language) {
    color: var(--code-language-dark-color, #d1d5db);
  }

  :deep(.copy-code-btn) {
    color: var(--copy-btn-dark-color, #9ca3af);
  }

  :deep(.copy-code-btn:hover) {
    background-color: var(--copy-btn-dark-hover-bg, #4b5563);
    color: var(--copy-btn-dark-hover-color, #d1d5db);
  }
}
</style>