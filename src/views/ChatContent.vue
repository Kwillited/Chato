<template>
  <!-- 聊天内容区域 -->
  <div id="chatMainContent" class="flex-1 flex flex-col overflow-hidden">

    <!-- 条件渲染聊天消息或知识图谱 -->
    <div class="flex-1 overflow-hidden">
      <!-- 聊天消息容器 -->
      <ChatMessagesContainer 
        v-if="uiStore.activeView === 'chat'"
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
        :isVisible="uiStore.activeView === 'chat' && isScrollToBottomVisible && chatStore.currentChatMessages.length > 0"
        @scrollToBottom="scrollToBottom"
      />

    <!-- 消息输入区域 - 传递当前视图状态 -->
      <UserInputBox @messageSubmitted="handleSendMessage" :activeView="uiStore.activeView" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useChatStore } from '../store/chatStore.js';
import { useSettingsStore } from '../store/settingsStore.js';
import { useUiStore } from '../store/uiStore.js';

// 导入子组件
import ChatMessagesContainer from '../components/chat/ChatMessagesContainer.vue';
import { ContextVisualizationContent } from '../components/library';
import ScrollToBottomButton from '../components/chat/ScrollToBottomButton.vue';
import { UserInputBox } from '../components/library';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();
const uiStore = useUiStore();

// 初始化路由
const router = useRouter();

// 引用子组件
const chatMessagesContainerRef = ref(null);

// 本地UI状态
const isScrollToBottomVisible = ref(false);

// 统一检查和跳转逻辑
const checkAndRedirectToHome = () => {
  // 检查当前路由是否为聊天路由
  const currentRoute = router.currentRoute.value;
  if (currentRoute.name === 'Chat') {
    // 如果是聊天路由，即使没有当前对话ID，也不跳转到首页
    // 因为handleRouteChange正在处理加载对话的逻辑
    return false;
  }
  
  // 只有当不在加载状态且没有当前对话时才跳转到首页
  // 避免在加载对话历史时误跳转
  // 同时，当有当前对话ID但消息为空时，不跳转到首页，因为可能正在从后端加载消息
  if (!uiStore.isLoading && !chatStore.currentChatId) {
    console.log('没有当前对话，跳转到首页');
    router.push('/');
    return true;
  }
  return false;
};

// 处理发送消息事件
const handleSendMessage = (message, model, deepThinking, webSearchEnabled, agent = false) => {
  if (message.trim() || chatStore.uploadedFiles.length > 0) {
    chatStore.sendMessage(message, model, deepThinking, webSearchEnabled, agent);

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
  () => chatStore.currentChatMessages.length,
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
      const messages = chatStore.currentChatMessages;
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
    // 只有当内容确实发生变化且用户当前在底部时才滚动
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

// 合并监听：当前对话ID和消息长度变化
watch(
  [() => chatStore.currentChatId, () => chatStore.currentChatMessages.length],
  async ([newChatId, newLength]) => {
    console.log('对话状态变化 - ID:', newChatId, '消息数:', newLength);
    
    // 检查是否需要跳转
    if (checkAndRedirectToHome()) {
      return;
    }
    
    // 如果有对话ID，等待微任务确保状态更新
    if (newChatId) {
      await nextTick();
      console.log('当前对话:', chatStore.currentChat);
      console.log('当前对话消息:', chatStore.currentChatMessages.length, '条');
    }
    
    nextTick(() => {
      safeScrollToBottom();
    });
  },
  { immediate: true } // 立即执行一次检查
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
  console.log('ChatContent组件已挂载，使用Pinia状态管理');

  // 检查是否需要跳转
  if (checkAndRedirectToHome()) {
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
/* 滚动条样式 - 使用全局scrollbar-thin样式，与文件面板保持一致 */

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
