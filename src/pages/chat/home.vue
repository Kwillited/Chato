<template>
  <!-- 发送消息内容区域 - 基于BaseContent -->
  <BaseContent>
    <div id="sendMessageContent" class="flex-1 flex flex-col overflow-hidden w-full">
      <!-- 消息输入区域 - 使用固定宽度容器包裹 -->
      <div class="w-full max-w-4xl mx-auto px-4 flex-1 flex flex-col justify-center">
        <h3 class="text-2xl font-semibold text-dark dark:text-white mb-4 text-center transition-colors duration-300">今天有什么可以帮助你的？</h3>
        <UserInputBox @sendMessage="handleSendMessage" :showShortcutHint="false" />
      </div>
    </div>
  </BaseContent>
</template>

<script setup>
import BaseContent from './BaseContent.vue';
import UserInputBox from '../../modules/conversation/components/UserInputBox/UserInputBox.vue';

// 从BaseContent继承的属性和方法会自动可用
// 不需要重复定义useChatHeader和useChatMessages
// handleSendMessage方法已在BaseContent中定义，会自动可用
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
