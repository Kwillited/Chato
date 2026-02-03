<template>
  <!-- 聊天快捷跳转模块 -->
  <div class="fixed flex flex-col items-center z-10" :style="indicatorPosition">
    <div class="flex flex-col items-center">
      <!-- 遍历所有用户消息 -->
      <div 
        v-for="(userMessage, index) in userMessages" 
        :key="userMessage.timestamp"
        class="flex flex-col items-center"
      >
        <!-- 连接线 - 除了第一个指示器外，其他指示器前都显示 -->
        <div 
          v-if="index > 0"
          class="w-px h-6 bg-gray-300 dark:bg-gray-600 transition-colors duration-300 mt-1 mb-1"
        ></div>
        
        <!-- 指示器 -->
        <div 
          class="cursor-pointer transition-all duration-300 relative group z-10"
          :title="`跳转到第 ${index + 1} 次提问`"
          @click="scrollToUserMessage(userMessage)"
        >
          <!-- 主指示器 -->
          <div 
            class="transition-all duration-300 ease-in-out relative"
            :class="{
              'w-4 h-4 bg-primary rounded-full shadow-lg transform scale-110': index === currentHighlightedMessage,
              'w-3 h-3 bg-gray-300 dark:bg-gray-600 rounded-full hover:w-4 hover:h-4 hover:bg-primary/70': index !== currentHighlightedMessage
            }"
          >
            <!-- 高亮状态的脉冲效果 -->
            <div 
              v-if="index === currentHighlightedMessage"
              class="absolute inset-0 bg-primary opacity-30 rounded-full animate-ping"
            ></div>
            
            <!-- 中心亮点 -->
            <div 
              class="absolute inset-0 flex items-center justify-center"
              :class="{
                'opacity-100': index === currentHighlightedMessage,
                'opacity-0': index !== currentHighlightedMessage
              }"
            >
              <div class="w-1.5 h-1.5 bg-white rounded-full"></div>
            </div>
          </div>
          
          <!-- 悬停时显示的序号 -->
          <div 
            class="absolute right-6 top-1/2 transform -translate-y-1/2 bg-primary text-white text-xs font-medium py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap"
          >
            {{ index + 1 }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useSettingsStore } from '../../../store/settingsStore.js';
import { useUiStore } from '../../../store/uiStore.js';

const props = defineProps({
  chatMessages: {
    type: Array,
    required: true
  },
  scrollContainer: {
    type: Object,
    required: true
  }
});

// 初始化settingsStore
const settingsStore = useSettingsStore();
const uiStore = useUiStore();

const emit = defineEmits(['scrollToUserMessage']);

// 过滤出所有用户消息
const userMessages = computed(() => {
  return props.chatMessages.filter(message => {
    // 处理ref包装的消息对象
    const msgValue = message?.value || message;
    return msgValue.role === 'user';
  });
});

// 当前高亮的消息索引
const currentHighlightedMessage = ref(0);

// 滚动到指定用户消息
const scrollToUserMessage = (userMessage) => {
  emit('scrollToUserMessage', userMessage);
};

// 更新当前高亮的消息
const updateCurrentHighlightedMessage = () => {
  if (!props.scrollContainer || userMessages.value.length === 0) return;
  
  const scrollTop = props.scrollContainer.scrollTop;
  const scrollBottom = scrollTop + props.scrollContainer.clientHeight;
  
  // 找到视口内最上方的用户消息
  const messages = props.chatMessages;
  let currentUserMessage = null;
  
  // 从前往后遍历，找到第一个完全或部分在视口内的用户消息
  for (let i = 0; i < messages.length; i++) {
    const message = messages[i];
    const messageElement = document.getElementById(`message-${i}`);
    
    // 处理ref包装的消息对象
    const msgValue = message?.value || message;
    if (messageElement && msgValue.role === 'user') {
      const rect = messageElement.getBoundingClientRect();
      const containerRect = props.scrollContainer.getBoundingClientRect();
      const messageTop = rect.top - containerRect.top + props.scrollContainer.scrollTop;
      const messageBottom = messageTop + rect.height;
      
      // 检查消息是否在视口内
      if (messageTop < scrollBottom && messageBottom > scrollTop) {
        currentUserMessage = message;
        break;
      }
    }
  }
  
  // 如果没有找到在视口内的用户消息，就使用最后一个用户消息
  if (!currentUserMessage) {
    currentUserMessage = userMessages.value[userMessages.value.length - 1];
  }
  
  // 找到对应的用户消息索引
  if (currentUserMessage) {
    // 处理ref包装的当前用户消息
    const currentUserMsgValue = currentUserMessage?.value || currentUserMessage;
    const userMessageIndex = userMessages.value.findIndex(um => {
      // 处理ref包装的用户消息列表中的消息
      const umValue = um?.value || um;
      return umValue.timestamp === currentUserMsgValue.timestamp;
    });
    if (userMessageIndex !== -1) {
      currentHighlightedMessage.value = userMessageIndex;
    }
  }
};

// 组件挂载后初始化
onMounted(() => {
  // 初始更新高亮消息
  updateCurrentHighlightedMessage();
});

// 监听消息变化，更新高亮消息
watch(() => props.chatMessages, () => {
  // 消息变化后，延迟更新高亮，确保DOM已更新
  setTimeout(() => {
    updateCurrentHighlightedMessage();
  }, 100);
}, { deep: true });

// 位置状态
const indicatorStyle = ref({});

// 计算滚动容器的垂直中心点并更新位置
const updateIndicatorPosition = () => {
  if (!props.scrollContainer) return;
  
  const baseRight = 20; // 基础right值
  let rightPanelWidth = 0;
  
  // 如果右侧面板可见，计算其宽度
  if (uiStore.rightPanelVisible) {
    // 从settingsStore获取右侧面板宽度，默认256px
    const widthStr = uiStore.rightPanelWidth || '256px';
    rightPanelWidth = parseInt(widthStr, 10) || 0;
  }
  
  // 计算滚动容器的垂直中心点
  const rect = props.scrollContainer.getBoundingClientRect();
  const centerY = rect.top + rect.height / 2;
  
  // 更新位置样式
  indicatorStyle.value = {
    right: `${baseRight + rightPanelWidth}px`,
    top: `${centerY}px`,
    transform: 'translateY(-50%)'
  };
};

// 监听滚动容器大小变化
let resizeTimeout = null;
let resizeObserver = null;

const handleResize = () => {
  // 立即更新位置（无延迟），确保响应迅速
  updateIndicatorPosition();
  
  // 但对高亮消息更新添加防抖，避免频繁计算
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
  resizeTimeout = setTimeout(() => {
    updateCurrentHighlightedMessage();
  }, 50); // 减少防抖延迟到50ms
};

// 组件挂载后初始化
onMounted(() => {
  // 初始更新位置和高亮消息
  updateIndicatorPosition();
  updateCurrentHighlightedMessage();
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize);
  
  // 添加滚动容器大小变化监听
  if (props.scrollContainer) {
    resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(props.scrollContainer);
  }
});

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
});

// 计算指示器位置：根据右侧面板的宽度和可见性动态调整
const indicatorPosition = computed(() => {
  // 确保位置始终是最新的
  updateIndicatorPosition();
  return indicatorStyle.value;
});

// 暴露方法给父组件
const exposed = {
  updateCurrentHighlightedMessage
};

defineExpose(exposed);
</script>

<style scoped>
/* 脉冲动画定义 */
@keyframes ping {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.5;
  }
}

.animate-ping {
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

/* 响应式设计 */
@media (max-width: 768px) {
  /* 在平板和手机上，调整快捷跳转模块的位置 */
  .fixed.right-10 {
    right: 12px;
  }
}
</style>