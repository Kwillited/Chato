<template>
  <div id="historyPanel" class="h-full flex flex-col">
    <PanelHeader title="历史会话" :showBackButton="false">
      <template #actions>
        <ActionButton
          id="exportAllBtn"
          icon="fa-download"
          title="导出所有对话"
          @click="handleExportAll"
          class="w-8 h-8 p-1.5 text-neutral hover:text-primary hover:bg-primary/10"
        />
        <ActionButton
          id="deleteAllBtn"
          icon="fa-trash-can"
          title="删除所有对话"
          @click="showDeleteAllModal = true"
          class="w-8 h-8 p-1.5 text-neutral hover:text-red-500 hover:bg-red-50"
        />
      </template>
    </PanelHeader>
    
    <!-- 确认删除所有对话模态框 -->
    <ConfirmationModal
      :visible="showDeleteAllModal"
      title="确认删除"
      message="确定要删除所有对话吗？这将删除所有历史对话，无法恢复！"
      confirmText="确认删除"
      :loading="isDeletingAll"
      loadingText="删除中..."
      @confirm="handleDeleteAllConfirm"
      @close="showDeleteAllModal = false"
    />

    <!-- 搜索框 -->
    <SearchBar v-model="searchQuery" placeholder="搜索对话..." />

    <div ref="scrollContainer" class="overflow-y-auto h-[calc(100%-100px)] scrollbar-thin transition-colors duration-300 ease-in-out" @scroll="handleScroll">
      <div id="chatHistory" class="p-2 space-y-3 transition-all duration-300 ease-in-out">
        <!-- 加载状态：使用骨架屏提升体验 -->
        <div v-if="chatStore.isLoading && chatHistory.length === 0" class="transition-opacity duration-300">
          <div class="animate-pulse">
            <div class="h-6 bg-gray-100 dark:bg-dark-700 rounded-md mx-2 mb-4 transition-colors duration-300"></div>
            <div class="space-y-2">
              <div class="p-2 rounded-lg bg-gray-50 dark:bg-dark-700 transition-colors duration-300">
                <div class="flex items-center w-full">
                  <div class="w-4 h-4 bg-gray-200 dark:bg-dark-600 rounded-full mr-2 transition-colors duration-300"></div>
                  <div class="h-4 bg-gray-200 dark:bg-dark-600 rounded-md flex-1 max-w-[200px] transition-colors duration-300"></div>
                </div>
              </div>
              <div class="p-2 rounded-lg bg-gray-50 dark:bg-dark-700 transition-colors duration-300">
                <div class="flex items-center w-full">
                  <div class="w-4 h-4 bg-gray-200 dark:bg-dark-600 rounded-full mr-2 transition-colors duration-300"></div>
                  <div class="h-4 bg-gray-200 dark:bg-dark-600 rounded-md flex-1 max-w-[150px] transition-colors duration-300"></div>
                </div>
              </div>
              <div class="p-2 rounded-lg bg-gray-50 dark:bg-dark-700 transition-colors duration-300">
                <div class="flex items-center w-full">
                  <div class="w-4 h-4 bg-gray-200 dark:bg-dark-600 rounded-full mr-2 transition-colors duration-300"></div>
                  <div class="h-4 bg-gray-200 dark:bg-dark-600 rounded-md flex-1 max-w-[180px] transition-colors duration-300"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 有对话历史时显示 -->
        <div v-else-if="chatHistory.length > 0" class="transition-opacity duration-300">
          <div v-for="group in groupedChats" :key="group.title" class="mb-4 transition-all duration-300">
            <h3 class="text-xs font-medium text-gray-500 dark:text-white mb-2 px-2 cursor-pointer flex items-center uppercase tracking-wider transition-colors duration-300"
                 @click="toggleGroup(group.title)">
            
              <i
                class="fa-solid fa-chevron-down mr-1.5 text-[8px] transition-transform duration-200 ease-in-out"
                :class="{ 'rotate-[-90deg]': collapsedGroups[group.title] }"
              ></i>
              {{ group.title }} ({{ group.chats.length }})
            </h3>
            <div class="space-y-1" v-if="!collapsedGroups[group.title]">
              <div
                v-for="chat in group.chats"
                :key="chat.id"
                class="p-2 rounded-lg cursor-pointer transition-all duration-300 ease-in-out hover:bg-gray-200 dark:hover:bg-dark-500 hover:shadow-md hover:-translate-y-0.5 min-h-9 flex items-center relative focus-within:outline-2 focus-within:outline-gray-400 dark:focus-within:outline-gray-500 focus-within:outline-offset-2"
                :class="{ 'font-semibold bg-gray-200 dark:bg-dark-500': isActiveChat(chat.id), pinned: chat.pinned }"
                @click="handleChatSelect(chat.id)"
              >
                <div class="flex items-center w-full">
                  <div class="flex items-center space-x-2 flex-1 min-w-0">
                    <div class="relative">
                      <i v-if="chat.pinned" class="fa-solid fa-thumbtack text-sm text-blue-500 flex-shrink-0 transition-colors duration-300"></i>
                      <i v-else class="fa-solid fa-comment text-sm text-gray-400 dark:text-gray-300 flex-shrink-0 transition-colors duration-300"></i>
                      <!-- 未读消息红点提示 -->
                      <span v-if="hasUnreadMessage(chat)" class="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full transition-all duration-300"></span>
                    </div>
                    <div class="font-medium text-sm text-slate-800 dark:text-white truncate transition-colors duration-300">{{ chat.title }}</div>
                  </div>
                  <div class="flex items-center space-x-2 ml-2 flex-shrink-0">
                    <button
                      class="text-[10px] text-neutral-400 opacity-0 hover:text-blue-500 hover:bg-blue-50 p-0.5 rounded transition-all duration-200 ease-in-out"
                      @click.stop="handlePinChat(chat.id)"
                      :title="chat.pinned ? '取消置顶' : '置顶对话'"
                    >
                      <i class="fa-solid fa-thumbtack"></i>
                    </button>
                    <button
                      class="text-[10px] text-neutral-400 opacity-0 hover:text-red-500 hover:bg-red-50 p-0.5 rounded transition-all duration-200 ease-in-out"
                      @click.stop="handleDeleteChat(chat.id)"
                      title="删除对话"
                    >
                      <i class="fa-solid fa-xmark"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 搜索无结果 -->
        <div v-else-if="searchQuery.trim()"
          class="p-6 text-center text-neutral dark:text-gray-300 text-sm transition-colors duration-300">
          没有找到与 "{{ searchQuery }}" 相关的对话
        </div>
        <!-- 错误状态 -->
        <div v-else-if="chatStore.error" id="errorChatState" class="p-6 text-center text-red-500 dark:text-red-400 text-sm transition-colors duration-300">
          <div class="mb-4">{{ chatStore.error }}</div>
          <button 
            @click="handleRetry" 
            class="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors duration-300 flex items-center justify-center mx-auto"
          >
            <i class="fa-solid fa-refresh mr-1.5"></i> 手动重试
          </button>
        </div>
        <!-- 空状态 -->
        <div v-else id="emptyChatState" class="p-10 text-center text-gray-500 dark:text-gray-300 text-sm italic transition-colors duration-300">暂无对话记录</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted, onUnmounted } from 'vue';
import PanelHeader from '../common/PanelHeader.vue';
import { useChatStore } from '../../store/chatStore.js';
import { useSettingsStore } from '../../store/settingsStore.js';
import { showNotification } from '../../services/notificationUtils.js';
import { SearchBar, ActionButton, ConfirmationModal } from '../library/index.js';

// 滚动容器引用
const scrollContainer = ref(null);

// 滚动计时器
let scrollTimer = null;

// 处理滚动开始
const handleScrollStart = () => {
  if (scrollContainer.value) {
    scrollContainer.value.classList.add('scrolling');
    
    // 清除之前的计时器
    if (scrollTimer) {
      clearTimeout(scrollTimer);
    }
  }
};

// 处理滚动结束
const handleScrollEnd = () => {
  if (scrollContainer.value) {
    scrollTimer = setTimeout(() => {
      scrollContainer.value.classList.remove('scrolling');
    }, 150);
  }
};

// 组件挂载时添加事件监听
onMounted(() => {
  if (scrollContainer.value) {
    const container = scrollContainer.value;
    
    // 防抖滚动处理函数
    const handleScroll = () => {
      handleScrollStart();
      
      // 清除之前的计时器
      if (scrollTimer) {
        clearTimeout(scrollTimer);
      }
      
      // 设置新的计时器来检测滚动结束
      scrollTimer = setTimeout(handleScrollEnd, 150);
    };
    
    // 添加滚动事件监听
    container.addEventListener('scroll', handleScroll);
    
    // 对于支持scrollend事件的浏览器，添加额外的滚动结束监听
    if ('scrollend' in window) {
      container.addEventListener('scrollend', handleScrollEnd);
    }
    
    // 保存处理函数引用以便卸载时移除
    container._scrollHandler = handleScroll;
  }
});

// 组件卸载时移除事件监听
onUnmounted(() => {
  if (scrollContainer.value) {
    const container = scrollContainer.value;
    
    // 移除滚动事件监听
    if (container._scrollHandler) {
      container.removeEventListener('scroll', container._scrollHandler);
    }
    
    // 移除scrollend事件监听
    container.removeEventListener('scrollend', handleScrollEnd);
  }
  
  // 清除计时器
  if (scrollTimer) {
    clearTimeout(scrollTimer);
  }
});

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();

// 从store获取对话历史
const chatHistory = computed(() => chatStore.chatHistory);

// 搜索查询
const searchQuery = ref('');

// 用于管理分组的展开/折叠状态
const collapsedGroups = reactive({});

// 显示删除所有对话模态框
const showDeleteAllModal = ref(false);

// 删除所有对话的加载状态
const isDeletingAll = ref(false);

// 切换分组的展开/折叠状态
function toggleGroup(groupTitle) {
  collapsedGroups[groupTitle] = !collapsedGroups[groupTitle];
}

// 处理置顶对话
const handlePinChat = (chatId) => {
  console.log('切换对话置顶状态:', chatId);
  chatStore.togglePinChat(chatId);
};

// 按时间分组对话并应用搜索过滤
const groupedChats = computed(() => {
  const now = new Date();
  const nowOnly = new Date(now);
  nowOnly.setHours(0, 0, 0, 0);

  const pinnedChats = [];
  const today = [];
  const yesterday = [];
  const dayBeforeYesterday = [];
  const withinWeek = [];
  const withinMonth = [];
  const withinYear = [];
  const older = [];

  chatHistory.value.forEach((chat) => {
    // 应用搜索过滤
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase().trim();
      const titleMatches = chat.title.toLowerCase().includes(query);

      // 检查消息内容是否匹配（如果有消息）
      let contentMatches = false;
      if (chat.messages && chat.messages.length > 0) {
        contentMatches = chat.messages.some((msg) => msg.content.toLowerCase().includes(query));
      }

      // 如果标题和内容都不匹配，则跳过此对话
      if (!titleMatches && !contentMatches) {
        return;
      }
    }

    // 置顶对话单独分组
    if (chat.pinned) {
      pinnedChats.push(chat);
      return;
    }

    // 按时间分组
    const chatDate = new Date(chat.updatedAt);
    const chatDateOnly = new Date(chatDate);
    chatDateOnly.setHours(0, 0, 0, 0);

    const diffInTime = nowOnly - chatDateOnly;
    const diffInDays = Math.floor(diffInTime / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) {
      today.push(chat);
    } else if (diffInDays === 1) {
      yesterday.push(chat);
    } else if (diffInDays === 2) {
      dayBeforeYesterday.push(chat);
    } else if (diffInDays < 7) {
      withinWeek.push(chat);
    } else if (diffInDays < 30) {
      withinMonth.push(chat);
    } else if (diffInDays < 365) {
      withinYear.push(chat);
    } else {
      older.push(chat);
    }
  });

  const groups = [];
  if (pinnedChats.length > 0) groups.push({ title: '置顶', chats: pinnedChats });
  if (today.length > 0) groups.push({ title: '今天', chats: today });
  if (yesterday.length > 0) groups.push({ title: '昨天', chats: yesterday });
  if (dayBeforeYesterday.length > 0) groups.push({ title: '前天', chats: dayBeforeYesterday });
  if (withinWeek.length > 0) groups.push({ title: '一星期内', chats: withinWeek });
  if (withinMonth.length > 0) groups.push({ title: '一个月内', chats: withinMonth });
  if (withinYear.length > 0) groups.push({ title: '一年内', chats: withinYear });
  if (older.length > 0) groups.push({ title: '更早', chats: older });

  // 搜索结果为空时显示提示
  if (searchQuery.value.trim() && groups.length === 0) {
    return [{ title: '搜索结果', chats: [] }];
  }

  return groups;
});

// 处理选择对话
const handleChatSelect = (chatId) => {
  console.log('选择对话:', chatId);
  chatStore.selectChat(chatId);
  
  // 确保activeContent是'chat'，以便正确显示ChatContent组件
  settingsStore.setActiveContent('chat');
};

// 处理导出所有对话
const handleExportAll = () => {
  console.log('导出所有对话');
  try {
    // 将对话历史转换为JSON字符串
    const chatData = JSON.stringify(chatStore.chats, null, 2);

    // 创建Blob对象和下载链接
    const blob = new Blob([chatData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_history_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('对话历史导出成功');
  } catch (error) {
    console.error('导出对话历史失败:', error);
    showNotification('导出失败，请重试。', 'error');
  }
};

// 处理删除所有对话确认
const handleDeleteAllConfirm = async () => {
  console.log('确认删除所有对话');
  isDeletingAll.value = true;
  
  try {
    await chatStore.clearAllChats();
    showNotification('所有对话已删除', 'success');
    showDeleteAllModal.value = false;
    
    // 删除所有对话后切换到sendMessage内容
    settingsStore.setActiveContent('sendMessage');
  } catch (error) {
    showNotification('删除失败: ' + error.message, 'error');
  } finally {
    isDeletingAll.value = false;
  }
};

// 处理删除单个对话
const handleDeleteChat = async (chatId) => {
  console.log('删除对话:', chatId);
  try {
    const wasCurrentChat = chatStore.currentChatId === chatId;
    await chatStore.deleteChat(chatId);
    showNotification('对话已删除', 'success');
    
    // 检查是否删除了最后一个对话
    if (chatStore.chats.length === 0 || (wasCurrentChat && chatStore.chats.length === 0)) {
      // 切换回sendMessageContent视图
      settingsStore.setActiveContent('sendMessage');
    }
  } catch (error) {
    showNotification('删除失败: ' + error.message, 'error');
  }
};

// 判断对话是否为当前活跃对话
const isActiveChat = (chatId) => {
  return chatStore.currentChatId === chatId;
};

// 判断对话是否有未读消息
const hasUnreadMessage = (chat) => {
  // 优先使用对话对象上的显式未读标记
  if (chat.hasUnreadMessage === false) {
    return false;
  }
  if (chat.hasUnreadMessage === true) {
    return true;
  }
  
  // 如果是当前活跃对话，则没有未读消息
  if (isActiveChat(chat.id)) {
    return false;
  }
  
  // 检查对话中是否有AI消息，并且是最近接收到的
  if (chat.messages && Array.isArray(chat.messages) && chat.messages.length > 0) {
    // 获取最后一条消息
    const lastMessage = chat.messages[chat.messages.length - 1];
    
    // 检查最后一条消息是否为AI消息，并且状态为已接收（流式渲染结束）
    if (lastMessage && lastMessage.value) {
      return lastMessage.value.role === 'ai' && 
             lastMessage.value.status === 'received' &&
             lastMessage.value.isTyping === false;
    }
  }
  
  return false;
};

// 处理手动重试
const handleRetry = () => {
  console.log('手动触发重试获取对话历史');
  chatStore.loadChatHistory(true);
};
</script>

<style scoped>
/* 添加悬停时显示按钮的效果 */
.hover\:shadow-md:hover .opacity-0 {
  opacity: 1;
}

/* 滚动条样式 - 与ChatMessagesContainer.vue保持一致 */
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
