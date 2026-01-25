<template>
  <div class="top-nav">
    <div class="top-nav-content">
      <!-- 左侧按钮组 -->
      <div class="flex space-x-2">
        <!-- 隐藏左侧面板按钮 -->
        <Button 
          icon="bars"
          tooltip="隐藏左侧面板"
          variant="secondary"
          size="md"
          shape="full"
          @click="() => {
            console.log('TopNav handleSideMenuToggle called directly');
            handleSideMenuToggle();
          }"
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
      
      <!-- 标题 -->
      <h1 class="top-nav-title">AI Chat</h1>
      
      <!-- 右侧区域 - 可以添加其他导航元素 -->
      <div class="flex space-x-2">
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
            class="absolute top-full mt-2 right-0 w-64 rounded-lg shadow-lg border z-50 dropdown-content flex flex-col py-2 bg-white dark:bg-dark-800 dark:border-dark-700 max-h-96 overflow-y-auto"
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
                @click="handleSelectHistoryChat(chat.id)"
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
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Button from '../Button.vue';
import { useChatHeader } from '../../../modules/conversation/composables/useChatHeader.js';
import { formatDate } from '../../../shared/utils/date.js';

// 使用聊天头部组合函数
const { 
  handleSideMenuToggle, 
  handleNewChat, 
  handleSelectHistoryChat,
  chatHistory 
} = useChatHeader();

// 简化的下拉菜单状态管理
const showHistoryMenu = ref(false);

const toggleHistoryMenu = () => {
  showHistoryMenu.value = !showHistoryMenu.value;
};
</script>

<style scoped>
.top-nav {
  height: 2.5rem;
  background-color: inherit;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  z-index: 100;
  transition: all 0.3s ease;
}

.dark .top-nav {
  background-color: inherit;
  border-bottom-color: #374151;
}

.top-nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.top-nav-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: #111827;
  transition: color 0.3s ease;
}

.dark .top-nav-title {
  color: #f9fafb;
}

/* 下拉菜单样式 */
.dropdown-content {
  transition: all 0.3s ease;
}

.hover-scale {
  transition: transform 0.2s ease;
}

.hover-scale:hover {
  transform: scale(1.05);
}
</style>