<template>
  <!-- 聊天内容区域 -->
  <div id="chatMainContent" class="flex-1 flex flex-col overflow-hidden">
    <!-- 顶部导航 -->
    <div class="panel-header p-3 flex flex-wrap items-center justify-end gap-4 relative transition-all duration-300">
      <!-- 左侧按钮组 -->
        <div class="absolute left-3 flex space-x-2">
          <!-- 隐藏左侧面板按钮 -->
          <ActionButton 
            icon="bars"
            title="隐藏左侧面板"
            @click="handleSideMenuToggle"
          />
          <!-- 新增会话按钮 -->
          <ActionButton 
            id="newChat"
            icon="comment-dots"
            title="新对话"
            @click="handleNewChat"
          />
        </div>
        
        <!-- 标题绝对居中 -->
        <div class="absolute left-1/2 transform -translate-x-1/2 flex items-center">
          <h2 class="text-lg font-bold text-gray-800 dark:text-white">{{ currentTitle }}</h2>
        </div>
        
        <!-- 右侧按钮组 -->
        <div class="flex space-x-2">
          <!-- 历史对话按钮（带下拉菜单） -->
          <div class="relative hover-scale">
            <ActionButton 
              id="historyChat"
              icon="clock-rotate-left"
              title="历史对话"
              @click.stop="toggleHistoryMenu"
            />
            
            <!-- 历史对话下拉菜单 -->
            <div 
              v-if="showHistoryMenu"
              class="absolute top-full mt-2 right-0 w-64 rounded-lg shadow-lg border z-50 dropdown-content flex flex-col py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700 max-h-96 overflow-y-auto"
            >
              <!-- 下拉菜单标题 -->
              <div class="px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-dark-700">
                历史对话
              </div>
              
              <!-- 历史对话列表 -->
              <div v-if="chatStore.chats.length > 0" class="py-2">
                <button 
                  v-for="chat in chatStore.chatHistory" 
                  :key="chat.id"
                  class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-dark-700 text-gray-700 dark:text-gray-300 transition-colors duration-200 flex items-start gap-2"
                  @click="selectChatFromHistory(chat.id)"
                >
                  <i class="fa-solid fa-comments text-xs mt-1 flex-shrink-0 text-gray-400 dark:text-gray-500"></i>
                  <div class="flex-1 min-w-0 flex items-center justify-between">
                    <div class="font-medium truncate">{{ chat.title }}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400 truncate ml-2 whitespace-nowrap">
                      {{ formatDate(chat.updatedAt) }}
                    </div>
                  </div>
                </button>
              </div>
              
              <!-- 空状态 -->
              <div v-else class="px-4 py-4 text-center text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-2">
                <i class="fa-solid fa-inbox text-xl"></i>
                暂无历史对话
              </div>
            </div>
          </div>
        </div>
    </div>

    <!-- 条件渲染聊天消息或知识图谱 -->
    <div class="flex-1 overflow-hidden">
      <!-- 聊天消息容器 -->
      <ChatMessagesContainer 
        v-if="chatStore.activeView === 'grid'"
        ref="chatMessagesContainerRef" 
        @updateScrollVisibility="updateScrollButtonVisibility"
        @scrollToBottom="hideScrollButton"
        class="w-full h-full"
      />
      
      <!-- 上下文可视化容器 -->
      <ContextVisualizationContent 
        v-else
        class="w-full h-full"
      />
    </div>
    
    <!-- 浮动按钮 - 只在聊天视图且有对话消息时显示 -->
      <ScrollToBottomButton 
        :isVisible="chatStore.activeView === 'grid' && isScrollToBottomVisible && chatStore.currentChatMessages.length > 0"
        @scrollToBottom="scrollToBottom"
      />

    <!-- 消息输入区域 - 传递当前视图状态 -->
      <UserInputBox @sendMessage="handleSendMessage" :activeView="chatStore.activeView" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue';
import { useChatStore } from '../store/chatStore.js';
import { useSettingsStore } from '../store/settingsStore.js';
// 导入公共工具函数
import { formatDate } from '../store/utils.js';

// 导入子组件
import ChatMessagesContainer from '../components/chat/ChatMessagesContainer.vue';
import { ContextVisualizationContent } from '../components/library';
import ScrollToBottomButton from '../components/chat/ScrollToBottomButton.vue';
import { UserInputBox } from '../components/library';
import ActionButton from '../components/common/ActionButton.vue';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();

// 引用子组件
const chatMessagesContainerRef = ref(null);

// 本地UI状态
const isScrollToBottomVisible = ref(false);

  // 处理新对话点击事件
  const handleNewChat = () => {
    // 取消当前会话的激活状态
    chatStore.currentChatId = null;
    
    // 清除所有对话的未读标记
    chatStore.resetUnreadStatus();
    
    // 切换到发送消息视图
    settingsStore.setActiveContent('sendMessage');
  };

// 从store计算属性获取数据
const currentTitle = computed(() => {
  return chatStore.currentChat?.title || '当前无对话';
});

// 历史对话菜单状态
const showHistoryMenu = ref(false);



// 切换历史对话下拉菜单显示状态
const toggleHistoryMenu = () => {
  showHistoryMenu.value = !showHistoryMenu.value;
};

// 从历史对话下拉菜单中选择对话
const selectChatFromHistory = (chatId) => {
  // 关闭下拉菜单
  showHistoryMenu.value = false;
  
  // 选择对话
  chatStore.selectChat(chatId);
  
  // 如果当前内容不是聊天视图，切换到聊天视图
  settingsStore.setActiveContent('chat');
};



// 点击外部区域关闭菜单
const closeMenusOnClickOutside = (event) => {
  const menuButtons = document.querySelectorAll('.relative.hover-scale');
  
  let clickedInsideMenu = false;
  menuButtons.forEach(button => {
    if (button.contains(event.target)) {
      clickedInsideMenu = true;
    }
  });
  
  if (!clickedInsideMenu) {
    showHistoryMenu.value = false;
  }
};

// 添加点击外部事件监听
onMounted(() => {
  document.addEventListener('click', closeMenusOnClickOutside);
});

// 移除事件监听
onUnmounted(() => {
  document.removeEventListener('click', closeMenusOnClickOutside);
});

// 处理隐藏菜单按钮点击事件
const handleSideMenuToggle = () => {
  // 只使用store提供的方法切换左侧导航栏的可见性
  // DOM操作逻辑移至App.vue中统一管理
  settingsStore.toggleLeftNav();
};

// 处理发送消息事件
const handleSendMessage = (message, model, deepThinking, webSearchEnabled) => {
  if (message.trim() || chatStore.uploadedFiles.length > 0) {
    chatStore.sendMessage(message, model, deepThinking, webSearchEnabled);

    // 发送消息后安全滚动到底部
    nextTick(() => {
      safeScrollToBottom();
    });
  }
};

// 滚动到底部
const scrollToBottom = () => {
  if (chatMessagesContainerRef.value) {
    chatMessagesContainerRef.value.scrollToBottom();
  }
};

// 更新滚动按钮可见性
const updateScrollButtonVisibility = (isVisible) => {
  isScrollToBottomVisible.value = isVisible;
};

// 隐藏滚动按钮
const hideScrollButton = () => {
  isScrollToBottomVisible.value = false;
};

// 监听消息变化，自动滚动到底部
watch(
  () => chatStore.currentChatMessages.length,
  (newLength, oldLength) => {
    if (newLength > oldLength && settingsStore.systemSettings.autoScroll) {
      nextTick(() => {
        safeScrollToBottom();
      });
    }
  }
);

// 监听最后一条消息内容变化，用于长文本实时渲染时的自动滚动
watch(
  [
    () => {
      const messages = chatStore.currentChatMessages;
      if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1];
        const messageData = lastMessage?.value || lastMessage;
        return {
          content: messageData.content || '',
          isTyping: messageData.isTyping || false,
          lastUpdate: messageData.lastUpdate || Date.now()
        };
      }
      return { content: '', isTyping: false, lastUpdate: Date.now() };
    }
  ],
  (newValue, oldValue) => {
    // 只有当内容确实发生变化时才滚动
    if (JSON.stringify(newValue) !== JSON.stringify(oldValue) && settingsStore.systemSettings.autoScroll && !isScrollToBottomVisible.value) {
      nextTick(() => {
        safeScrollToBottom();
      });
    }
  },
  {
    deep: true // 深度监听，确保能捕获对象内部属性变化
  }
);

// 监听当前对话变化，安全滚动到底部
watch(
  () => chatStore.currentChatId,
  (newChatId) => {
    // 检查如果消息为空，切换到发送消息视图
    if (newChatId && chatStore.currentChatMessages.length === 0) {
      settingsStore.setActiveContent('sendMessage');
      return;
    }
    
    nextTick(() => {
      safeScrollToBottom();
    });
  }
);

// 监听当前对话消息列表变化，当消息为空时切换到发送消息视图
watch(
  () => chatStore.currentChatMessages.length,
  (newLength) => {
    if (newLength === 0 && chatStore.currentChatId) {
      settingsStore.setActiveContent('sendMessage');
    }
  }
);

// 使用requestAnimationFrame确保DOM完全渲染后再滚动
const safeScrollToBottom = () => {
  // 使用requestAnimationFrame确保在浏览器下一次重绘之前执行
  requestAnimationFrame(() => {
    scrollToBottom();
    
    // 对于复杂内容，可能需要第二次确认
    requestAnimationFrame(() => {
      scrollToBottom();
    });
  });
};

// 组件挂载后的操作
onMounted(() => {
  console.log('ChatContent组件已挂载，使用Pinia状态管理');

  // 检查如果消息为空，切换到发送消息视图
  if (chatStore.currentChatMessages.length === 0) {
    settingsStore.setActiveContent('sendMessage');
    return;
  }

  // 初始化时安全滚动到底部
  nextTick(() => {
    safeScrollToBottom();
  });

  // 注意：已移除自动保存功能，所有数据操作均通过后端API完成
});
</script>

<style scoped>
/* 主内容区域的样式已经在主CSS中定义，这里可以添加组件特定的样式 */
  
  /* 深色模式下的渐变背景 */
  .dark .bg-gradient-subtle {
    background: linear-gradient(to bottom, #1E293B 0%, #1E293B 100%);
  }
  
  /* 深色模式下的卡片样式 */
  .dark .card {
    border-color: #334155 !important;
    background-color: #334155 !important;
  }
  
  /* 深色模式下的深度效果 */
  .dark .depth-1 {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
  }
  
  .dark .depth-1:hover {
    box-shadow:
      0 4px 6px -1px rgba(0, 0, 0, 0.3),
      0 2px 4px -1px rgba(0, 0, 0, 0.25) !important;
  }
  
  .dark .depth-2 {
    box-shadow:
      0 4px 6px -1px rgba(0, 0, 0, 0.3),
      0 2px 4px -1px rgba(0, 0, 0, 0.25) !important;
  }
  
  /* 深色模式下的滚动条 */
  .dark .scrollbar-thin::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
  }
  
  .dark .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
  }

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

/* 渐变背景 */
.bg-gradient-subtle {
  background: linear-gradient(to bottom, #f9fafb 0%, #ffffff 100%);
}

/* 卡片阴影效果 - 增加特异性确保样式应用 */
.card {
  border-radius: 20px !important;
  border: 1px solid #e5e7eb !important;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

/* 深度效果 - 增加特异性确保样式应用 */
.depth-1 {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}

.depth-1:hover {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
}

.depth-2 {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
}

/* 按钮悬停效果 */
.hover-scale:hover {
  transform: scale(1.05);
}

/* 焦点环效果 */
.focus-ring:focus {
  outline: 2px solid rgba(66, 153, 225, 0.5);
  outline-offset: 2px;
}
</style>
