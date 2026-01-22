<template>
  <!-- 聊天内容区域 -->
  <div id="sendMessageContent" class="flex-1 flex flex-col overflow-hidden w-full">
    <!-- 使用公共ChatHeader组件 -->
    <ChatHeader 
      :show-border="false" 
      :chat-history="chatHistory"
      @toggle-side-menu="handleSideMenuToggle"
      @new-chat="handleNewChat"
      @select-history-chat="handleSelectHistoryChat"
    />

    <!-- 消息输入区域 - 使用固定宽度容器包裹 -->
    <div class="w-full max-w-4xl mx-auto px-4 flex-1 flex flex-col justify-center mt-[-40px]">
      <h3 class="text-2xl font-semibold text-dark dark:text-white mb-4 text-center transition-colors duration-300">今天有什么可以帮助你的？</h3>
      <UserInputBox @sendMessage="handleSendMessage" :showShortcutHint="false" />
    </div>
  </div>
</template>

<script setup>
import { useChatHeader } from '../composables/useChatHeader';
import ChatHeader from '../components/common/ChatHeader.vue';
import { UserInputBox } from '../components/library';

// 使用组合式函数
const { 
  chatStore, 
  settingsStore, 
  handleSideMenuToggle, 
  handleNewChat, 
  handleSelectHistoryChat,
  chatHistory 
} = useChatHeader();

// 处理发送消息事件
const handleSendMessage = async (message, model, deepThinking = false, webSearchEnabled = false) => {
  if (message.trim() || chatStore.uploadedFiles.length > 0) {
    // 先确保有当前对话（如果没有则创建）
    if (!chatStore.currentChatId) {
      await chatStore.createNewChat(model);
    }
    
    // 先发送消息，确保isTyping消息立即添加
    chatStore.sendMessage(message, model, deepThinking, webSearchEnabled);
    
    // 然后切换到ChatContent视图（此时isTyping消息已经添加，用户可以看到AI正在输入）
    settingsStore.setActiveContent('chat');
  }
};
</script>

<style scoped>
/* 移除顶部导航的边框和伪元素效果 */
.panel-header {
  border-bottom: none !important;
}

.panel-header::after {
  display: none !important;
  content: none !important;
}
</style>
