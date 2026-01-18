<template>
  <!-- 聊天内容区域 -->
  <div id="sendMessageContent" class="flex-1 flex flex-col overflow-hidden w-full">
    <!-- 顶部导航 -->
    <div class="panel-header p-3 flex flex-wrap items-center justify-end gap-4 relative transition-all duration-300 border-b-0">
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
      
  
      <!-- 按钮区域靠右对齐 -->
      <div class="flex items-center space-x-2">
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

    <!-- 消息输入区域 - 使用固定宽度容器包裹 -->
    <div class="w-full max-w-4xl mx-auto px-4 flex-1 flex flex-col justify-center mt-[-40px]">
      <h3 class="text-2xl font-semibold text-dark dark:text-white mb-4 text-center transition-colors duration-300">今天有什么可以帮助你的？</h3>
      <UserInputBox @sendMessage="handleSendMessage" :showShortcutHint="false" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useChatStore } from '../store/chatStore.js';
import { useSettingsStore } from '../store/settingsStore.js';
// 导入公共工具函数
import { formatDate } from '../store/utils.js';

// 使用全局store
const settingsStore = useSettingsStore();

// 导入必要的子组件
import { UserInputBox } from '../components/library';
import ActionButton from '../components/common/ActionButton.vue';

// 处理侧边菜单切换
const handleSideMenuToggle = () => {
  // 使用store方法切换左侧面板可见性
  settingsStore.toggleLeftNav();
};

// 初始化stores
const chatStore = useChatStore();

// 处理新对话点击事件
const handleNewChat = () => {
  // 取消当前会话的激活状态
  chatStore.currentChatId = null;
  
  // 清除所有对话的未读标记
  chatStore.resetUnreadStatus();
  
  // 切换到发送消息视图
  settingsStore.setActiveContent('sendMessage');
};

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
  
  // 切换到聊天视图
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

// 处理发送消息事件
const handleSendMessage = async (message, model, deepThinking = false, webSearchEnabled = false) => {
  if (message.trim() || chatStore.uploadedFiles.length > 0) {
    // 先确保有当前对话（如果没有则创建）
    if (!chatStore.currentChatId) {
      await chatStore.createNewChat(model);
    }
    
    // 先发送消息，确保isTyping消息立即添加
    chatStore.sendMessage(message, model, deepThinking, webSearchEnabled);
    
    // 然后切换到ChatContent视图（此时isTyping消息已经添加，用户可以看到AI正在输入）
    settingsStore.setActiveContent('chat');
  }
};
</script>

<style scoped>
/* 移除顶部导航的边框和伪元素效果 */
.panel-header {
  border-bottom: none !important;
}

.panel-header::after {
  display: none !important;
  content: none !important;
}
</style>
