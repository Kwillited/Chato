import { ref, nextTick } from 'vue';

/**
 * 聊天滚动管理组合函数，统一处理聊天滚动相关逻辑
 * @param {Object} options - 配置选项
 * @param {Object} options.chatMessagesContainerRef - 聊天消息容器引用
 * @param {Function} options.scrollToBottomImpl - 滚动到底部的实现函数
 * @returns {Object} 包含聊天滚动管理功能的对象
 */
export function useChatScroll(options = {}) {
  // 本地UI状态
  const isScrollToBottomVisible = ref(false);

  /**
   * 滚动到底部
   */
  const scrollToBottom = () => {
    if (options.chatMessagesContainerRef?.value) {
      options.chatMessagesContainerRef.value.scrollToBottom();
    } else if (options.scrollToBottomImpl) {
      options.scrollToBottomImpl();
    }
  };

  /**
   * 更新滚动按钮可见性
   * @param {boolean} isVisible - 是否可见
   */
  const updateScrollButtonVisibility = (isVisible) => {
    isScrollToBottomVisible.value = isVisible;
  };

  /**
   * 隐藏滚动按钮
   */
  const hideScrollButton = () => {
    isScrollToBottomVisible.value = false;
  };

  /**
   * 使用requestAnimationFrame确保DOM完全渲染后再滚动
   */
  const safeScrollToBottom = () => {
    // 使用requestAnimationFrame确保在浏览器下一次重绘之前执行
    requestAnimationFrame(() => {
      scrollToBottom();
      
      // 对于复杂内容，可能需要第二次确认
      requestAnimationFrame(() => {
        scrollToBottom();
      });
    });
  };

  /**
   * 安全滚动到底部，确保DOM已更新
   */
  const safeScrollToBottomWithNextTick = () => {
    nextTick(() => {
      safeScrollToBottom();
    });
  };

  return {
    // 响应式状态
    isScrollToBottomVisible,
    
    // 方法
    scrollToBottom,
    updateScrollButtonVisibility,
    hideScrollButton,
    safeScrollToBottom,
    safeScrollToBottomWithNextTick
  };
}