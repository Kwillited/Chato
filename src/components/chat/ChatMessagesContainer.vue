<template>
  <div class="flex-1 p-6 overflow-y-auto bg-inherit">
    <!-- 聊天消息列表容器 - 添加与UserInputBox相同的宽度限制 -->
    <div ref="chatMessagesContainer" class="w-full max-w-4xl mx-auto space-y-6 scrollbar-thin transition-colors duration-300 ease-in-out" @scroll="checkScrollPosition">
      <ChatMessage v-for="message in chatMessages" :key="message.timestamp" :message="message" :chatStyleDocument="settingsStore.systemSettings.chatStyleDocument" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import ChatMessage from './ChatMessage.vue';
import { useChatStore } from '../../store/chatStore.js';
import { useSettingsStore } from '../../store/settingsStore.js';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();

// 使用ref引用DOM元素
const chatMessagesContainer = ref(null);

// 从store计算属性获取数据
const chatMessages = computed(() => chatStore.currentChatMessages);

// 滚动到底部
const scrollToBottom = () => {
  if (chatMessagesContainer.value) {
    chatMessagesContainer.value.scrollTop = chatMessagesContainer.value.scrollHeight;
    
    // 触发事件通知父组件隐藏滚动按钮
    emit('scrollToBottom');
  }
};

// 检测是否需要显示滚动到底部按钮
const checkScrollPosition = () => {
  if (chatMessagesContainer.value) {
    const scrollPosition = chatMessagesContainer.value.scrollTop + chatMessagesContainer.value.clientHeight;
    const scrollHeight = chatMessagesContainer.value.scrollHeight;
    
    // 通知父组件是否显示滚动到底部按钮
    // 修改：将阈值从100降低到10，使轻微滚动也能触发状态变化
    emit('updateScrollVisibility', scrollHeight - scrollPosition > 10);
  }
};

// 暴露方法给父组件
const exposed = {
  scrollToBottom
};

defineExpose(exposed);

// 定义事件
const emit = defineEmits(['updateScrollVisibility', 'scrollToBottom']);
</script>

<style scoped>
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

/* 深色模式滚动条样式 */
.dark .scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  transition: background-color 0.3s ease-in-out;
}

.dark .scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>