<template>
  <div ref="scrollContainer" class="flex-1 p-6 overflow-y-auto bg-inherit relative" @scroll="checkScrollPosition">
    <!-- 聊天消息列表容器 - 添加与UserInputBox相同的宽度限制 -->
    <div ref="chatMessagesContainer" class="w-full max-w-4xl mx-auto space-y-6 scrollbar-thin transition-colors duration-300 ease-in-out">
      <ChatMessage v-for="(message, index) in chatMessages" :key="message.timestamp" :message="message" :chatStyleDocument="settingsStore.systemSettings.chatStyleDocument" :id="`message-${index}`" />
    </div>
    
    <!-- 使用组件库中的快捷跳转模块 -->
    <ChatJumpIndicator 
      v-if="userMessages.length > 0"
      ref="jumpIndicatorRef"
      :chatMessages="chatMessages"
      :scrollContainer="scrollContainer"
      @scrollToUserMessage="handleScrollToUserMessage"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import ChatMessage from './ChatMessage.vue';
import { ChatJumpIndicator } from '../library/index.js';
import { useChatStore } from '../../store/chatStore.js';
import { useSettingsStore } from '../../store/settingsStore.js';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();

// 使用ref引用DOM元素
const scrollContainer = ref(null);
const chatMessagesContainer = ref(null);
const jumpIndicatorRef = ref(null);

// 从store计算属性获取数据
const chatMessages = computed(() => chatStore.currentChatMessages);

// 过滤出所有用户消息
const userMessages = computed(() => {
  return chatMessages.value.filter(message => {
    // 处理ref包装的消息对象
    const msgValue = message?.value || message;
    return msgValue.role === 'user';
  });
});

// 处理滚动到指定用户消息
const handleScrollToUserMessage = (userMessage) => {
  // 处理ref包装的用户消息
  const userMsgValue = userMessage?.value || userMessage;
  const messageIndex = chatMessages.value.findIndex(msg => {
    // 处理ref包装的消息列表中的消息
    const msgValue = msg?.value || msg;
    return msgValue.timestamp === userMsgValue.timestamp;
  });
  if (messageIndex !== -1) {
    const messageElement = document.getElementById(`message-${messageIndex}`);
    if (messageElement) {
      messageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
};

// 滚动到底部
const scrollToBottom = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
    
    // 触发事件通知父组件隐藏滚动按钮
    emit('scrollToBottom');
  }
};

// 检测滚动位置
const checkScrollPosition = () => {
  if (scrollContainer.value) {
    const scrollPosition = scrollContainer.value.scrollTop + scrollContainer.value.clientHeight;
    const scrollHeight = scrollContainer.value.scrollHeight;
    
    // 通知父组件是否显示滚动到底部按钮
    // 修改：将阈值从100降低到10，使轻微滚动也能触发状态变化
    emit('updateScrollVisibility', scrollHeight - scrollPosition > 10);
    
    // 通知跳转指示器更新高亮
    if (jumpIndicatorRef.value) {
      jumpIndicatorRef.value.updateCurrentHighlightedMessage();
    }
  }
};

// 暴露方法给父组件
const exposed = {
  scrollToBottom
};

defineExpose(exposed);

// 定义事件
const emit = defineEmits(['updateScrollVisibility', 'scrollToBottom']);

// 组件挂载后初始化
onMounted(() => {
  console.log('ChatMessagesContainer组件已挂载');
});

// 监听消息变化
watch(chatMessages, () => {
  console.log('ChatMessages变化，消息数量:', chatMessages.value.length);
}, { deep: true });
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

/* 响应式设计 */
@media (max-width: 768px) {
  /* 在平板和手机上，调整快捷跳转模块的位置 */
  .fixed.right-10 {
    right: 12px;
  }
}
</style>