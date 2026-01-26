<template>
  <!-- 消息列表侧边栏组件 -->
  <Sidebar type="left" class="message-list-sidebar">
    <template #content>
      <div class="message-panel">
        <!-- 搜索栏 -->
        <div class="p-4 border-b border-gray-100 dark:border-dark-700">
          <div class="relative">
            <input 
              type="text" 
              placeholder="搜索消息..." 
              class="w-full pl-9 pr-4 py-2 rounded-lg bg-gray-50 dark:bg-dark-800 border border-gray-200 dark:border-dark-700 text-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              v-model="searchQuery"
            >
            <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">🔍</span>
          </div>
        </div>
        
        <!-- 消息列表 -->
        <div class="message-list overflow-y-auto">
          <div 
            v-for="message in filteredMessages" 
            :key="message.id"
            class="message-item p-3 border-b border-gray-100 dark:border-dark-700 cursor-pointer transition-colors"
            :class="{ 'bg-blue-50 dark:bg-dark-600': selectedMessageId === message.id, 'hover:bg-gray-50 dark:hover:bg-dark-800': selectedMessageId !== message.id }"
            @click="selectMessage(message.id)"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-gray-200 dark:bg-dark-700 flex items-center justify-center text-sm font-medium text-gray-700 dark:text-white">
                  {{ message.sender.charAt(0) }}
                </div>
                <div class="flex flex-col min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-gray-800 dark:text-white truncate">{{ message.sender }}</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">{{ message.time }}</span>
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 truncate mt-0.5">
                    {{ message.contentPreview }}
                  </div>
                </div>
              </div>
              <div v-if="message.unread" class="w-2 h-2 rounded-full bg-blue-500 mt-2"></div>
            </div>
          </div>
          
          <div v-if="filteredMessages.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-8">
            没有找到消息
          </div>
        </div>
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import { ref, computed } from 'vue';
import Sidebar from '../../shared/ui/layout/Sidebar.vue';

// 搜索查询
const searchQuery = ref('');
// 选中的消息ID
const selectedMessageId = ref(null);

// 消息数据
const messages = ref([
  {
    id: 1,
    sender: '张三',
    contentPreview: '你好，关于项目的最新进展...',
    time: '今天 14:30',
    unread: true
  },
  {
    id: 2,
    sender: '李四',
    contentPreview: '我已经完成了设计稿，需要你审核一下...',
    time: '今天 10:15',
    unread: false
  },
  {
    id: 3,
    sender: '王五',
    contentPreview: '会议时间改到明天下午3点了，请准时参加...',
    time: '昨天 16:45',
    unread: true
  },
  {
    id: 4,
    sender: '赵六',
    contentPreview: '这个问题我已经修复了，你可以测试一下...',
    time: '昨天 09:20',
    unread: false
  },
  {
    id: 5,
    sender: '张三',
    contentPreview: '关于数据库的优化方案，我有一些想法...',
    time: '前天 15:10',
    unread: false
  },
  {
    id: 6,
    sender: '技术团队',
    contentPreview: '系统将于今晚进行维护升级...',
    time: '2024-01-24',
    unread: true
  },
  {
    id: 7,
    sender: '产品经理',
    contentPreview: '新版本的需求文档已经更新...',
    time: '2024-01-23',
    unread: false
  },
  {
    id: 8,
    sender: '李四',
    contentPreview: '这个功能需要再调整一下...',
    time: '2024-01-22',
    unread: false
  }
]);

// 过滤消息
const filteredMessages = computed(() => {
  if (!searchQuery.value) return messages.value;
  
  const query = searchQuery.value.toLowerCase();
  return messages.value.filter(message => 
    message.sender.toLowerCase().includes(query) || 
    message.contentPreview.toLowerCase().includes(query)
  );
});

// 选择消息
const selectMessage = (messageId) => {
  selectedMessageId.value = messageId;
  // 可以触发消息详情的显示或其他逻辑
};
</script>

<style scoped>
.message-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.message-list {
  flex: 1;
  overflow-y: auto;
}

.message-item {
  /* 消息项基础样式 */
}

.message-list::-webkit-scrollbar {
  width: 4px;
}
</style>