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
import { useAppUI } from '../../shared/composables/useAppUI.js';
import { useNavigation } from '../../shared/composables/useNavigation.js';

// 使用应用UI组合函数
const { setActiveContent } = useAppUI();

// 使用导航组合函数
const { navigateToChat } = useNavigation();

// 使用聊天头部组合函数
const {
  chatStore
} = useChatHeader();

// 使用聊天消息管理组合函数
const {
  sendMessage
} = useChatMessages();

// 处理发送消息事件
const handleSendMessage = async (message, model, deepThinking = false, webSearchEnabled = false, files = []) => {
  if (message.trim() || files.length > 0) {
    // 1. 先跳转路由到chat页面
    await navigateToChat();
    
    // 2. 确保有当前对话（如果没有则创建）
    if (!chatStore.currentChatId) {
      await chatStore.createNewChat(model);
    }
    
    // 3. 切换到聊天视图
    setActiveContent('chat');
    
    // 4. 发送消息，传递文件列表
    await sendMessage(message, model, deepThinking, webSearchEnabled, files);
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
