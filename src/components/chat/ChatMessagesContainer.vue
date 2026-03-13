<template>
  <div ref="scrollContainer" class="flex-1 p-6 overflow-y-auto bg-inherit relative scrollbar-thin">
    <!-- 聊天消息列表容器 - 添加与UserInputBox相同的宽度限制 -->
    <div ref="chatMessagesContainer" class="w-full max-w-4xl mx-auto space-y-6 transition-colors duration-300 ease-in-out">
      <!-- 渲染分组后的消息 -->
      <template v-for="(group, groupIndex) in groupedMessages" :key="group.id">
        <!-- 所有消息都单独渲染 -->
        <ChatMessage 
          v-for="(message, msgIndex) in group.messages" 
          :key="message.timestamp" 
          :message="message" 
          :chatStyle="settingsStore.systemSettings.chatStyle" 
          :id="`message-${groupIndex}-${msgIndex}`"
          :class="{ 'last-message': isLastMessage(groupIndex, msgIndex) }"
        />
      </template>
      <!-- 用于检测底部的哨兵元素 -->
      <div ref="sentinel" class="h-1 w-full"></div>
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
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import { AIChatBubble, ChatJumpIndicator } from '../library/index.js';
import { useChatStore } from '../../store/chatStore.js';
import { useSettingsStore } from '../../store/settingsStore.js';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();

// 使用ref引用DOM元素
const scrollContainer = ref(null);
const chatMessagesContainer = ref(null);
const jumpIndicatorRef = ref(null);
const sentinel = ref(null);
const observer = ref(null);

// 从store计算属性获取数据
const chatMessages = computed(() => {
  const messages = chatStore.currentChatMessages;
  console.log('ChatMessages计算属性:', messages.length, '条消息');
  return messages;
});

// 过滤出所有用户消息
const userMessages = computed(() => {
  return chatMessages.value.filter(message => {
    // 处理ref包装的消息对象
    const msgValue = message?.value || message;
    return msgValue.role === 'user';
  });
});

// 直接使用消息列表，不需要分组
const groupedMessages = computed(() => {
  const messages = chatMessages.value;
  if (!messages || messages.length === 0) return [];
  
  console.log('消息列表:', messages);
  
  // 将每条消息包装为独立分组，保持与原有结构兼容
  return messages.map((message, index) => {
    const msgValue = message?.value || message;
    const timestamp = msgValue.timestamp || Date.now();
    
    return {
      id: `message-group-${timestamp}-${index}`,
      isAgentGroup: false,
      messages: [message],
      role: msgValue.role,
      model: msgValue.model,
      timestamp: timestamp
    };
  });
});

// 检查是否是最后一条消息
const isLastMessage = (groupIndex, msgIndex) => {
  const groups = groupedMessages.value;
  if (groups.length === 0) return false;
  
  const lastGroup = groups[groups.length - 1];
  const lastGroupIndex = groups.length - 1;
  const lastMessageIndex = lastGroup.messages.length - 1;
  
  return groupIndex === lastGroupIndex && msgIndex === lastMessageIndex;
};

// 处理滚动到指定用户消息
const handleScrollToUserMessage = (userMessage) => {
  // 处理ref包装的用户消息
  const userMsgValue = userMessage?.value || userMessage;
  
  // 查找消息在分组中的位置
  let found = false;
  groupedMessages.value.forEach((group, groupIndex) => {
    if (found) return;
    
    // 检查分组中的消息
    group.messages.forEach((msg, msgIndex) => {
      if (found) return;
      const msgValue = msg?.value || msg;
      if (msgValue.timestamp === userMsgValue.timestamp) {
        // 找到消息，滚动到对应的消息
        const messageElement = document.getElementById(`message-${groupIndex}-${msgIndex}`);
        if (messageElement && scrollContainer.value) {
          const containerRect = scrollContainer.value.getBoundingClientRect();
          const messageRect = messageElement.getBoundingClientRect();
          const scrollPosition = messageRect.top - containerRect.top + scrollContainer.value.scrollTop;
          scrollContainer.value.scrollTo({ 
            top: scrollPosition - 20, // 减去20px的偏移，使消息显示在容器顶部下方一点
            behavior: 'smooth' 
          });
          found = true;
        }
      }
    });
  });
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
      
      // 触发事件通知父组件隐藏滚动按钮
      emit('scrollToBottom');
    }
  });
};

// 初始化IntersectionObserver
const initObserver = () => {
  if (!scrollContainer.value || !sentinel.value) return;
  
  // 清理之前的观察器
  if (observer.value) {
    observer.value.disconnect();
  }
  
  // 创建新的观察器
  observer.value = new IntersectionObserver((entries) => {
    const entry = entries[0];
    // 当哨兵元素可见时，隐藏滚动按钮
    if (entry.isIntersecting) {
      emit('updateScrollVisibility', false);
    } else {
      // 当哨兵元素不可见时，显示滚动按钮
      emit('updateScrollVisibility', true);
    }
    
    // 通知跳转指示器更新高亮
    if (jumpIndicatorRef.value) {
      jumpIndicatorRef.value.updateCurrentHighlightedMessage();
    }
  }, {
    root: scrollContainer.value,
    threshold: 0.1 // 当哨兵元素10%可见时触发
  });
  
  // 观察哨兵元素
  observer.value.observe(sentinel.value);
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
  nextTick(() => {
    initObserver();
  });
});

// 组件卸载时清理
onUnmounted(() => {
  if (observer.value) {
    observer.value.disconnect();
  }
});

// 监听消息变化
watch(chatMessages, () => {
  console.log('ChatMessages变化，消息数量:', chatMessages.value.length);
  
  // 检查最后一条消息是否正在输入
  const lastMessage = chatMessages.value[chatMessages.value.length - 1];
  const lastMessageValue = lastMessage?.value || lastMessage;
  
  // 只有当消息不在输入状态且用户当前在底部时才滚动到底部
  if (lastMessageValue && !lastMessageValue.isTyping && scrollContainer.value) {
    // 使用IntersectionObserver后，我们可以直接检查哨兵元素的可见性
    // 但为了保持原有逻辑，我们仍然使用滚动位置检查
    const scrollPosition = scrollContainer.value.scrollTop + scrollContainer.value.clientHeight;
    const scrollHeight = scrollContainer.value.scrollHeight;
    
    // 只有当用户接近底部时才滚动（阈值20px）
    if (scrollHeight - scrollPosition <= 20) {
      scrollToBottom();
    }
  }
  
  // 消息变化后重新初始化观察器
  nextTick(() => {
    initObserver();
  });
}, { deep: true });
</script>

<style scoped>
/* 响应式设计 */
@media (max-width: 768px) {
  /* 在平板和手机上，调整快捷跳转模块的位置 */
  .fixed.right-10 {
    right: 12px;
  }
}
</style>