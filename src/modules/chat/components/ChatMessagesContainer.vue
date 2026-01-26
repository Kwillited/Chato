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
const chatMessagesContainer = ref(null);
const jumpIndicatorRef = ref(null);

// 滚动状态管理
const isScrollToBottomVisible = ref(false);

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
    hideScrollButton();
  }
};

// 安全滚动到底部 - 只有在用户接近底部时才自动滚动
const safeScrollToBottom = async () => {
  await nextTick();
  if (!scrollContainer.value) return;
  
  const { scrollTop, clientHeight, scrollHeight } = scrollContainer.value;
  const isNearBottom = scrollHeight - scrollTop - clientHeight < 200;
  
  if (isNearBottom) {
    await scrollToBottom(true);
  }
};

// 检测滚动位置 (用于控制"回到底部"按钮的显示)
const checkScrollPosition = () => {
  if (!scrollContainer.value) return;
  
  const { scrollTop, clientHeight, scrollHeight } = scrollContainer.value;
  // 距离底部超过 100px 显示按钮
  const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
  const shouldShowButton = !isNearBottom;
  
  if (isScrollToBottomVisible.value !== shouldShowButton) {
    isScrollToBottomVisible.value = shouldShowButton;
    emit('updateScrollVisibility', shouldShowButton);
  }
  
  // 更新跳转指示器高亮
  jumpIndicatorRef.value?.updateCurrentHighlightedMessage();
};

// 隐藏滚动按钮
const hideScrollButton = () => {
  if (isScrollToBottomVisible.value) {
    isScrollToBottomVisible.value = false;
    emit('updateScrollVisibility', false);
  }
};

// 监听新消息，自动滚动
watch(() => chatMessages.value.length, async (newLen, oldLen) => {
  if (newLen > oldLen && settingsStore.systemSettings.autoScroll) {
    await safeScrollToBottom();
  }
});

// 监听自动滚动设置变化
watch(() => settingsStore.systemSettings.autoScroll, async (newValue) => {
  if (newValue && chatMessages.value.length > 0) {
    await safeScrollToBottom();
  }
});

defineExpose({
  scrollToBottom,
  safeScrollToBottom,
  hideScrollButton
});
</script>