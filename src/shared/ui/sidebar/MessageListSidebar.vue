<template>
  <!-- 消息列表侧边栏组件 -->
  <Sidebar class="message-list-sidebar left">
    <template #content>
      <!-- 搜索框 -->
      <SearchBar
        v-model="searchQuery"
        placeholder="搜索消息..."
        class="border-b border-gray-100 dark:border-dark-700"
      />

      <!-- 滚动容器 -->
      <div class="flex-1 overflow-y-auto p-2 space-y-3 scrollbar-thin transition-colors duration-300 ease-in-out">
        <!-- 有消息时显示 -->
        <div v-if="groupedMessages.length > 0" class="transition-opacity duration-300">
          <div v-for="group in groupedMessages" :key="group.title" class="mb-4 transition-all duration-300">
            <h3 class="text-xs font-medium text-gray-500 dark:text-white mb-2 px-2 cursor-pointer flex items-center uppercase tracking-wider transition-colors duration-300"
                 @click="toggleGroup(group.title)">
            
              <i
                class="fa-solid fa-chevron-down mr-1.5 text-[8px] transition-transform duration-200 ease-in-out"
                :class="{ 'rotate-[-90deg]': collapsedGroups[group.title] }"
              ></i>
              {{ group.title }} ({{ group.messages.length }})
            </h3>
            <div class="space-y-1" v-if="!collapsedGroups[group.title]">
              <div
                v-for="chat in group.messages"
                :key="chat.id"
                class="p-2 rounded-lg cursor-pointer transition-all duration-300 ease-in-out hover:bg-gray-200 dark:hover:bg-dark-500 hover:shadow-md hover:-translate-y-0.5 min-h-9 flex items-center relative focus-within:outline-2 focus-within:outline-gray-400 dark:focus-within:outline-gray-500 focus-within:outline-offset-2"
                :class="{ 'font-semibold bg-gray-200 dark:bg-dark-500': isActiveChat(chat.id), pinned: chat.pinned }"
                @click="selectMessage(chat.id)"
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
                      @click.stop="chatStore.togglePinChat(chat.id)"
                      :title="chat.pinned ? '取消置顶' : '置顶对话'"
                    >
                      <i class="fa-solid fa-thumbtack"></i>
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
          没有找到与 "{{ searchQuery }}" 相关的消息
        </div>
        <!-- 空状态 -->
        <div v-else class="p-10 text-center text-gray-500 dark:text-gray-300 text-sm italic transition-colors duration-300">暂无消息记录</div>
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';
import { useChatStore } from '../../../app/store/chatStore.js';
import Sidebar from '../layout/Sidebar.vue';
import SearchBar from '../SearchBar.vue';

// 初始化store
const chatStore = useChatStore();

// 搜索查询 - 使用 chatStore 中的状态
const searchQuery = computed({
  get: () => chatStore.searchQuery,
  set: (value) => chatStore.setSearchQuery(value)
});

// 用于管理分组的展开/折叠状态
const collapsedGroups = reactive({});

// 切换分组的展开/折叠状态
function toggleGroup(groupTitle) {
  collapsedGroups[groupTitle] = !collapsedGroups[groupTitle];
}

// 按时间分组对话并应用搜索过滤
const groupedMessages = computed(() => {
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

  // 使用 chatStore 的对话历史数据
  chatStore.chatHistory.forEach((chat) => {
    // 应用搜索过滤
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase().trim();
      const titleMatches = chat.title.toLowerCase().includes(query);

      // 检查消息内容是否匹配（如果有消息）
      let contentMatches = false;
      if (chat.messages && chat.messages.length > 0) {
        contentMatches = chat.messages.some((msg) => msg.value.content.toLowerCase().includes(query));
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
  if (pinnedChats.length > 0) groups.push({ title: '置顶', messages: pinnedChats });
  if (today.length > 0) groups.push({ title: '今天', messages: today });
  if (yesterday.length > 0) groups.push({ title: '昨天', messages: yesterday });
  if (dayBeforeYesterday.length > 0) groups.push({ title: '前天', messages: dayBeforeYesterday });
  if (withinWeek.length > 0) groups.push({ title: '一星期内', messages: withinWeek });
  if (withinMonth.length > 0) groups.push({ title: '一个月内', messages: withinMonth });
  if (withinYear.length > 0) groups.push({ title: '一年内', messages: withinYear });
  if (older.length > 0) groups.push({ title: '更早', messages: older });

  // 搜索结果为空时显示提示
  if (searchQuery.value.trim() && groups.length === 0) {
    return [{ title: '搜索结果', messages: [] }];
  }

  return groups;
});

// 判断对话是否为当前活跃对话
const isActiveChat = (chatId) => {
  return chatStore.currentChatId === chatId;
};

// 处理选择对话
const selectMessage = (chatId) => {
  chatStore.selectChat(chatId);
};

// 判断对话是否有未读消息
const hasUnreadMessage = (chat) => {
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
</script>

<style scoped>
/* 添加悬停时显示按钮的效果 */
.hover\:shadow-md:hover .opacity-0 {
  opacity: 1;
}
</style>