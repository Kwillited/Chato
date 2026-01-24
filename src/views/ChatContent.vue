<template>
  <!-- 聊天内容区域 -->
  <div id="chatMainContent" class="flex-1 flex flex-col overflow-hidden">

    <!-- 条件渲染聊天消息或知识图谱 -->
    <div class="flex-1 overflow-hidden">
      <!-- 聊天消息容器 -->
      <ChatMessagesContainer 
        v-if="chatStore.activeView === 'grid'"
        ref="chatMessagesContainerRef" 
        @updateScrollVisibility="updateScrollButtonVisibility"
        @scrollToBottom="hideScrollButton"
        class="w-full h-full"
      />
      
      <!-- 上下文可视化容器 -->
      <ContextVisualizationContent 
        v-else
        class="w-full h-full"
      />
    </div>
    
    <!-- 浮动按钮 - 只在聊天视图且有对话消息时显示 -->
      <ScrollToBottomButton 
        :isVisible="chatStore.activeView === 'grid' && isScrollToBottomVisible && chatStore.currentChatMessages.length > 0"
        @scrollToBottom="scrollToBottom"
      />

    <!-- 消息输入区域 - 传递当前视图状态 -->
      <UserInputBox @sendMessage="handleSendMessage" :activeView="chatStore.activeView" />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import { useChatHeader } from '../composables/useChatHeader';
import { useChatMessages } from '../composables/useChatMessages';
import ChatMessagesContainer from '../components/chat/ChatMessagesContainer.vue';
import { ContextVisualizationContent } from '../components/library';
import ScrollToBottomButton from '../components/chat/ScrollToBottomButton.vue';
import { UserInputBox } from '../components/library';
import ChatHeader from '../components/common/ChatHeader.vue';
import logger from '../utils/logger.js';

// 使用组合式函数
const { 
  chatStore, 
  settingsStore, 
  handleSideMenuToggle, 
  handleNewChat, 
  handleSelectHistoryChat,
  getCurrentChatTitle,
  chatHistory 
} = useChatHeader();

// 使用聊天消息管理组合函数
const { 
  sendMessage,
  currentChatMessages,
  isLoading: isSendingMessage,
  error: sendMessageError
} = useChatMessages();

// 引用子组件
const chatMessagesContainerRef = ref(null);

// 本地UI状态
const isScrollToBottomVisible = ref(false);

// 从store计算属性获取数据
const currentTitle = computed(() => {
  return getCurrentChatTitle();
});

// 处理发送消息事件
const handleSendMessage = (message, model, deepThinking, webSearchEnabled) => {
  if (message.trim() || chatStore.uploadedFiles.length > 0) {
    // 使用组合函数中的sendMessage方法
    sendMessage(message, model, deepThinking, webSearchEnabled);

    // 发送消息后安全滚动到底部
    nextTick(() => {
      safeScrollToBottom();
    });
  }
};

// 滚动到底部
const scrollToBottom = () => {
  if (chatMessagesContainerRef.value) {
    chatMessagesContainerRef.value.scrollToBottom();
  }
};

// 更新滚动按钮可见性
const updateScrollButtonVisibility = (isVisible) => {
  isScrollToBottomVisible.value = isVisible;
};

// 隐藏滚动按钮
const hideScrollButton = () => {
  isScrollToBottomVisible.value = false;
};

// 监听消息变化，自动滚动到底部
watch(
  () => currentChatMessages.length,
  (newLength, oldLength) => {
    if (newLength > oldLength && settingsStore.systemSettings.autoScroll) {
      nextTick(() => {
        safeScrollToBottom();
      });
    }
  }
);

// 监听最后一条消息内容变化，用于长文本实时渲染时的自动滚动
watch(
  [
    () => {
      const messages = currentChatMessages;
      if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1];
        const messageData = lastMessage?.value || lastMessage;
        return {
          content: messageData.content || '',
          isTyping: messageData.isTyping || false,
          lastUpdate: messageData.lastUpdate || Date.now()
        };
      }
      return { content: '', isTyping: false, lastUpdate: Date.now() };
    }
  ],
  (newValue, oldValue) => {
    // 只有当内容确实发生变化时才滚动
    if (JSON.stringify(newValue) !== JSON.stringify(oldValue) && settingsStore.systemSettings.autoScroll && !isScrollToBottomVisible.value) {
      nextTick(() => {
        safeScrollToBottom();
      });
    }
  },
  {
    deep: true // 深度监听，确保能捕获对象内部属性变化
  }
);

// 监听当前对话变化，安全滚动到底部
watch(
  () => chatStore.currentChatId,
  (newChatId) => {
    // 检查如果消息为空，切换到发送消息视图
    if (newChatId && currentChatMessages.length === 0) {
      settingsStore.setActiveContent('sendMessage');
      return;
    }
    
    nextTick(() => {
      safeScrollToBottom();
    });
  }
);

// 监听当前对话消息列表变化，当消息为空时切换到发送消息视图
watch(
  () => currentChatMessages.length,
  (newLength) => {
    if (newLength === 0 && chatStore.currentChatId) {
      settingsStore.setActiveContent('sendMessage');
    }
  }
);

// 使用requestAnimationFrame确保DOM完全渲染后再滚动
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

// 组件挂载后的操作
  onMounted(() => {
    logger.info('ChatContent组件已挂载，使用Pinia状态管理');

  // 检查如果消息为空，切换到发送消息视图
  if (chatStore.currentChatMessages.length === 0) {
    settingsStore.setActiveContent('sendMessage');
    return;
  }

  // 初始化时安全滚动到底部
  nextTick(() => {
    safeScrollToBottom();
  });

  // 注意：已移除自动保存功能，所有数据操作均通过后端API完成
});
</script>

<style scoped>
/* 主内容区域的样式已经在主CSS中定义，这里可以添加组件特定的样式 */
  
  /* 深色模式下的渐变背景 */
  .dark .bg-gradient-subtle {
    background: linear-gradient(to bottom, #1E293B 0%, #1E293B 100%);
  }
  
  /* 深色模式下的卡片样式 */
  .dark .card {
    border-color: #334155 !important;
    background-color: #334155 !important;
  }
  
  /* 深色模式下的深度效果 */
  .dark .depth-1 {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
  }
  
  .dark .depth-1:hover {
    box-shadow:
      0 4px 6px -1px rgba(0, 0, 0, 0.3),
      0 2px 4px -1px rgba(0, 0, 0, 0.25) !important;
  }
  
  .dark .depth-2 {
    box-shadow:
      0 4px 6px -1px rgba(0, 0, 0, 0.3),
      0 2px 4px -1px rgba(0, 0, 0, 0.25) !important;
  }
  
  /* 深色模式下的滚动条 */
  .dark .scrollbar-thin::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
  }
  
  .dark .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
  }

/* 滚动条样式 */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 渐变背景 */
.bg-gradient-subtle {
  background: linear-gradient(to bottom, #f9fafb 0%, #ffffff 100%);
}

/* 卡片阴影效果 - 增加特异性确保样式应用 */
.card {
  border-radius: 20px !important;
  border: 1px solid #e5e7eb !important;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

/* 深度效果 - 增加特异性确保样式应用 */
.depth-1 {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}

.depth-1:hover {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
}

.depth-2 {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
}

/* 按钮悬停效果 */
.hover-scale:hover {
  transform: scale(1.05);
}

/* 焦点环效果 */
.focus-ring:focus {
  outline: 2px solid rgba(66, 153, 225, 0.5);
  outline-offset: 2px;
}
</style>
