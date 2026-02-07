<template>
  <div ref="scrollContainer" class="flex-1 p-6 overflow-y-auto bg-inherit relative scrollbar-thin" @scroll="checkScrollPosition">
    <!-- 聊天消息列表容器 - 添加与UserInputBox相同的宽度限制 -->
    <div ref="chatMessagesContainer" class="w-full max-w-4xl mx-auto space-y-6 transition-colors duration-300 ease-in-out">
      <!-- 渲染分组后的消息 -->
      <template v-for="(group, groupIndex) in groupedMessages" :key="group.id">
        <!-- 所有消息都单独渲染 -->
        <ChatMessage 
          v-for="(message, msgIndex) in group.messages" 
          :key="message.timestamp" 
          :message="message" 
          :chatStyleDocument="settingsStore.systemSettings.chatStyleDocument" 
          :id="`message-${groupIndex}-${msgIndex}`" 
        />
      </template>
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

// 计算分组后的消息
const groupedMessages = computed(() => {
  const messages = chatMessages.value;
  if (!messages || messages.length === 0) return [];
  
  console.log('原始消息列表:', messages);
  
  const groups = [];
  
  messages.forEach(message => {
    const msgValue = message?.value || message;
    console.log('处理消息:', msgValue);
    
    // 检查是否是智能体消息（使用agent字段或agent_step字段）
    if (msgValue.agent || msgValue.agent_step !== undefined) {
      console.log('发现智能体消息，step:', msgValue.agent_step);
      
      // 为每个智能体消息创建独立的分组
      const agentGroup = {
        id: `agent-message-${msgValue.timestamp}-${msgValue.agent_step}`,
        isAgentGroup: false, // 改为普通分组，每个智能体消息独立显示
        messages: [message],
        role: msgValue.role,
        model: msgValue.model,
        timestamp: msgValue.timestamp,
        agent_step: msgValue.agent_step,
        agent_node: msgValue.agent_node
      };
      
      groups.push(agentGroup);
      console.log('创建智能体消息分组:', agentGroup.id);
    } else {
      console.log('发现普通消息:', msgValue.role);
      
      // 添加普通消息分组
      groups.push({
        id: `normal-group-${msgValue.timestamp}`,
        isAgentGroup: false,
        messages: [message]
      });
    }
  });
  
  console.log('最终分组结果:', groups);
  return groups;
});

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
/* 响应式设计 */
@media (max-width: 768px) {
  /* 在平板和手机上，调整快捷跳转模块的位置 */
  .fixed.right-10 {
    right: 12px;
  }
}
</style>