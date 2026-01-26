<template>
  <div class="base-content">
    <!-- 预留插槽，用于子组件自定义内容 -->
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useChatHeader, useChatMessages } from '../../modules/conversation';
import logger from '../../shared/utils/logger.js';

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

// 从store计算属性获取数据
const currentTitle = computed(() => {
  return getCurrentChatTitle();
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
      
      // 切换到home视图
      // settingsStore.setActiveContent('home'); // 已改为路由管理
    }
  };

// 暴露公共属性和方法
defineExpose({
  chatStore,
  settingsStore,
  handleSideMenuToggle,
  handleNewChat,
  handleSelectHistoryChat,
  currentChatMessages,
  isSendingMessage,
  sendMessageError,
  currentTitle,
  chatHistory,
  handleSendMessage
});
</script>

<style scoped>
.base-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>