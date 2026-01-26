<template>
  <!-- 发送消息内容区域 -->
  <div id="sendMessageContent" class="flex-1 flex flex-col overflow-hidden w-full">
    <!-- 消息输入区域 - 使用固定宽度容器包裹 -->
    <div class="w-full max-w-4xl mx-auto px-4 flex-1 flex flex-col justify-center">
      <h3 class="text-2xl font-semibold text-dark dark:text-white mb-4 text-center transition-colors duration-300">今天有什么可以帮助你的？</h3>
      <UserInputBox @sendMessage="handleSendMessage" :showShortcutHint="false" />
    </div>
  </div>
</template>

<script setup>
import UserInputBox from '../../modules/conversation/components/UserInputBox/UserInputBox.vue';
import { useChatHeader, useChatMessages } from '../../modules/conversation';

// 使用聊天头部组合函数
const {
  chatStore
} = useChatHeader();

// 使用聊天消息管理组合函数
const {
  sendMessage
} = useChatMessages();

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
