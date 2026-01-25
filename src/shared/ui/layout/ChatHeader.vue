<template>
  <!-- 聊天顶部导航栏 -->
  <div class="w-full flex items-center justify-between gap-2">
    <!-- 左侧按钮组 -->
    <div class="flex items-center gap-2">
      <!-- 隐藏左侧面板按钮 -->
      <Button 
        icon="bars"
        tooltip="隐藏左侧面板"
        variant="secondary"
        size="md"
        shape="full"
        @click="handleSideMenuToggle"
      />
      <!-- 新增会话按钮 -->
      <Button 
        id="newChat"
        icon="comment-dots"
        tooltip="新对话"
        variant="secondary"
        size="md"
        shape="full"
        @click="handleNewChat"
      />
    </div>
    
    <!-- 标题区域 -->
    <h1 v-if="title" class="font-bold text-sm sm:text-base tracking-tight text-gray-900 dark:text-white">{{ title }}</h1>
    
    <!-- 右侧按钮区域 -->
    <div class="flex items-center gap-2">
      <!-- 历史对话按钮（带下拉菜单） -->
      <div class="relative hover-scale">
        <Button 
          id="historyChat"
          icon="clock-rotate-left"
          tooltip="历史对话"
          variant="secondary"
          size="md"
          shape="full"
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
          <div v-if="chatHistory.length > 0" class="py-2">
            <button 
              v-for="chat in chatHistory" 
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
</template>

<script setup>
import { ref } from 'vue';
import Button from '../Button.vue';
import { formatDate } from '../../../shared/utils/date.js';

// 定义组件属性
defineProps({
  // 可选的标题文本
  title: {
    type: String,
    default: ''
  },
  // 是否显示底部边框
  showBorder: {
    type: Boolean,
    default: true
  },
  // 历史对话列表
  chatHistory: {
    type: Array,
    default: () => []
  }
});

// 定义事件
const emit = defineEmits([
  // 切换侧边菜单
  'toggleSideMenu',
  // 新对话
  'newChat',
  // 选择历史对话
  'selectHistoryChat'
]);

// 简化的下拉菜单状态管理
const showHistoryMenu = ref(false);

const toggleHistoryMenu = () => {
  showHistoryMenu.value = !showHistoryMenu.value;
};

// 处理侧边菜单切换
const handleSideMenuToggle = () => {
  emit('toggleSideMenu');
};

// 处理新对话点击事件
const handleNewChat = () => {
  emit('newChat');
};

// 从历史对话下拉菜单中选择对话
const selectChatFromHistory = (chatId) => {
  emit('selectHistoryChat', chatId);
  showHistoryMenu.value = false; // 选择后关闭菜单
};
</script>

<style scoped>
/* 组件特定样式可以在这里添加 */
</style>