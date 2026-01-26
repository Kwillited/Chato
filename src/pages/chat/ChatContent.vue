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
import { ref, onMounted, nextTick, watch } from 'vue';
import ChatMessagesContainer from '../../modules/conversation/components/ChatMessagesContainer.vue';
import ScrollToBottomButton from '../../modules/conversation/components/ScrollToBottomButton.vue';
import UserInputBox from '../../modules/conversation/components/UserInputBox/UserInputBox.vue';
import { KnowledgeGraphCanvas as ContextVisualizationContent } from '../../modules/knowledge-graph';
import { useChatScroll } from '../../modules/conversation/composables/useChatScroll.js';
import logger from '../../shared/utils/logger.js';
import { useChatHeader, useChatMessages } from '../../modules/conversation';
import { useSettingsStore } from '../../app/store/settingsStore.js';

// 初始化 stores
const settingsStore = useSettingsStore();

// 引用子组件
const chatMessagesContainerRef = ref(null);

// 使用聊天头部组合函数
const {
  chatStore
} = useChatHeader();

// 使用聊天消息管理组合函数
const {
  sendMessage,
  currentChatMessages
} = useChatMessages();

// 使用聊天滚动管理组合函数
const { 
  isScrollToBottomVisible,
  scrollToBottom,
  updateScrollButtonVisibility,
  hideScrollButton,
  safeScrollToBottom
} = useChatScroll({
  chatMessagesContainerRef
});

// 处理发送消息事件
const handleSendMessage = async (message, model, deepThinking = false, webSearchEnabled = false) => {
  if (message.trim() || chatStore.uploadedFiles.length > 0) {
    // 先确保有当前对话（如果没有则创建）
    if (!chatStore.currentChatId) {
      await chatStore.createNewChat(model);
    }
    
    // 发送消息
    await sendMessage(message, model, deepThinking, webSearchEnabled);
  }
};

// 组件挂载后的操作
onMounted(() => {
  logger.info('ChatContent组件已挂载');

  // 初始化时安全滚动到底部
  nextTick(() => {
    scrollToBottom();
  });
});

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
