<template>
  <div 
    ref="scrollContainer" 
    class="flex-1 p-4 md:p-6 overflow-y-auto bg-inherit relative scrollbar-thin scroll-smooth" 
    @scroll="checkScrollPosition"
  >
    <!-- 聊天消息列表容器 -->
    <div 
      ref="chatMessagesContainer" 
      class="w-full max-w-4xl mx-auto space-y-6 pb-10"
    >
      <ChatMessage 
        v-for="(message, index) in chatMessages" 
        :key="message.id || index" 
        :message="message" 
        :chatStyleDocument="settingsStore.systemSettings.chatStyleDocument" 
        :id="`message-${message.timestamp}`" 
      />
    </div>
    
    <!-- 快捷跳转模块 -->
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import ChatJumpIndicator from './ChatJumpIndicator/ChatJumpIndicator.vue';
import { useChatStore } from '../../../app/store/chatStore.js';
import { useSettingsStore } from '../../../app/store/settingsStore.js';

const emit = defineEmits(['updateScrollVisibility', 'scrollToBottom']);

const chatStore = useChatStore();
const settingsStore = useSettingsStore();

const scrollContainer = ref(null);
const jumpIndicatorRef = ref(null);

// 核心数据：直接获取纯对象数组
const chatMessages = computed(() => chatStore.currentChatMessages || []);

// 过滤用户消息 (用于跳转导航)
const userMessages = computed(() => {
  return chatMessages.value.filter(msg => msg.role === 'user');
});

// 跳转到指定消息
const handleScrollToUserMessage = (userMessage) => {
  const targetId = `message-${userMessage.timestamp}`;
  const el = document.getElementById(targetId);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

// 滚动到底部
const scrollToBottom = async (smooth = true) => {
  await nextTick(); // 等待 DOM 更新
  if (scrollContainer.value) {
    scrollContainer.value.scrollTo({
      top: scrollContainer.value.scrollHeight,
      behavior: smooth ? 'smooth' : 'auto'
    });
    emit('scrollToBottom');
  }
};

// 检测滚动位置 (用于控制"回到底部"按钮的显示)
const checkScrollPosition = () => {
  if (!scrollContainer.value) return;
  
  const { scrollTop, clientHeight, scrollHeight } = scrollContainer.value;
  // 距离底部超过 100px 显示按钮
  const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
  
  emit('updateScrollVisibility', !isNearBottom);
  
  // 更新跳转指示器高亮
  jumpIndicatorRef.value?.updateCurrentHighlightedMessage();
};

// 监听新消息，自动滚动
watch(() => chatMessages.value.length, async (newLen, oldLen) => {
  if (newLen > oldLen) {
    // 只有在用户已经在底部，或者这是新对话的第一条消息时才自动滚动
    // 这里简单处理：总是尝试滚动，或者由父组件控制
    // await scrollToBottom(); 
  }
});

defineExpose({
  scrollToBottom
});
</script>