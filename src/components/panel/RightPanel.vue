<template>
  <div 
    id="rightPanel" 
    class="h-full flex-shrink-0 z-40 overflow-hidden mr-0 max-w-[370px]"
    :class="{ 'transition-all duration-300': !isInitialLoading }"
    :style="{ width: settingsStore.rightPanelVisible ? settingsStore.rightPanelWidth : '0px', display: settingsStore.rightPanelVisible ? 'block' : 'none', flexShrink: 0 }"
  >
    <!-- 右侧面板标题 -->
    <div class="panel-header p-3 flex items-center justify-between gap-2">
      <h2 class="text-lg font-bold text-dark dark:text-white flex-1">上下文工程</h2>
      <ActionButton
        :icon="chatStore.activeView === 'grid' ? 'fa-sitemap' : 'fa-comments'"
        :title="`切换到${chatStore.activeView === 'grid' ? '上下文工程可视化' : '对话'}视图`"
        @click="toggleView"
      />
      <ActionButton
        icon="fa-times"
        title="关闭面板"
        @click="settingsStore.toggleRightPanel()"
      />
    </div>
    
    <!-- 右侧面板内容 -->
    <div class="p-3 space-y-4">
      <!-- 上下文概述 -->
      <div class="panel-section">
        <h3 class="text-sm font-semibold text-gray-500 mb-2">上下文概述</h3>
        <div class="bg-gray-50 dark:bg-dark-bg-tertiary p-3 rounded-lg">
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary mb-1">当前会话: {{ chatStore.currentChat?.title || '无' }}</p>
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary mb-1">上下文数量: {{ getContextCount() }}</p>
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary mb-1">输入Token: {{ getInputTokens() }}</p>
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary mb-1">输出Token: {{ getOutputTokens() }}</p>
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary">总Token: {{ getTotalTokens() }}</p>
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary mt-1">最新更新: {{ getLastUpdateTime() }}</p>
        </div>
      </div>
      
      <!-- 上下文筛选 -->
      <div class="panel-section">
        <div class="flex justify-between items-center mb-2">
          <h3 class="text-sm font-semibold text-gray-500">上下文筛选</h3>
          <div class="flex space-x-2">
            <ActionButton
              icon="fa-check-square"
              title="全选"
              size="sm"
              @click="selectAllMessages"
            />
            <ActionButton
              icon="fa-square"
              title="取消全选"
              size="sm"
              @click="clearAllSelections"
            />
          </div>
        </div>
        
        <div class="bg-gray-50 dark:bg-dark-bg-tertiary rounded-lg max-h-[200px] overflow-y-auto">
          <div class="p-2">
            <!-- 消息列表 -->
            <div v-if="chatStore.currentChat && chatStore.currentChat.messages && chatStore.currentChat.messages.length > 0">
              <div
                v-for="message in chatStore.currentChat.messages"
                :key="message.value?.id || message.id"
                class="message-item mb-3 p-2 rounded border border-gray-200 dark:border-dark-border hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary transition-colors"
                :class="{ 'selected': selectedMessages.has(message.value?.id || message.id) }"
              >
                <div class="flex items-start space-x-2">
                  <!-- 选择复选框 -->
                  <input
                    type="checkbox"
                    :id="`msg-${message.value?.id || message.id}`"
                    :checked="selectedMessages.has(message.value?.id || message.id)"
                    @change="toggleMessageSelection(message.value?.id || message.id)"
                    class="mt-1"
                  />
                  
                  <!-- 消息内容 -->
                  <div class="flex-1">
                    <div class="flex justify-between items-center mb-1">
                      <span class="text-xs font-semibold text-gray-500 dark:text-gray-400">
                        {{ (message.value?.role || message.role) === 'user' ? '用户' : 'AI' }}
                      </span>
                      <span class="text-xs text-gray-400 dark:text-gray-500">
                        {{ formatTime(message.value?.timestamp || message.timestamp) }}
                      </span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-dark-text-secondary whitespace-pre-wrap">
                      {{ message.value?.content || message.content }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 无消息提示 -->
            <div v-else class="text-center py-4 text-xs text-gray-500 dark:text-gray-400">
              暂无上下文信息
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="flex justify-end mt-2 space-x-2">
          <ActionButton
            icon="fa-check"
            title="应用调整"
            @click="applyContextChanges"
            :disabled="selectedMessages.size === 0"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import ActionButton from '../common/ActionButton.vue';
import { showNotification } from '../../services/notificationUtils.js';
import { ref, watch } from 'vue';
// 导入公共工具函数
import { formatTime } from '../../store/utils.js';

// 定义props
const _props = defineProps({
  isInitialLoading: {
    type: Boolean,
    default: true
  }
});

// 初始化stores
const settingsStore = useSettingsStore();
const chatStore = useChatStore();

// 上下文调整状态
const selectedMessages = ref(new Set());

// 计算上下文数量
const getContextCount = () => {
  if (!chatStore.currentChat || !chatStore.currentChat.messages) return 0;
  return chatStore.currentChat.messages.length;
};

// 估算token数量（简化实现）
const estimateTokens = (text) => {
  if (!text) return 0;
  // 简单估算：英文按1 token/4字符，中文按1 token/2字符
  const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
  const otherChars = text.length - chineseChars;
  return Math.ceil(chineseChars / 2 + otherChars / 4);
};

// 计算输入token数量
const getInputTokens = () => {
  if (!chatStore.currentChat || !chatStore.currentChat.messages) return 0;
  let totalTokens = 0;
  chatStore.currentChat.messages.forEach(message => {
    const msgData = message.value || message;
    if (msgData.role === 'user') {
      totalTokens += estimateTokens(msgData.content);
    }
  });
  return totalTokens;
};

// 计算输出token数量
const getOutputTokens = () => {
  if (!chatStore.currentChat || !chatStore.currentChat.messages) return 0;
  let totalTokens = 0;
  chatStore.currentChat.messages.forEach(message => {
    const msgData = message.value || message;
    if (msgData.role === 'ai') {
      totalTokens += estimateTokens(msgData.content);
    }
  });
  return totalTokens;
};

// 计算总token数量
const getTotalTokens = () => {
  return getInputTokens() + getOutputTokens();
};



// 获取最新更新时间
const getLastUpdateTime = () => {
  if (!chatStore.currentChat || !chatStore.currentChat.messages || chatStore.currentChat.messages.length === 0) {
    return '无';
  }
  
  const messages = chatStore.currentChat.messages;
  let lastUpdate = 0;
  
  messages.forEach(message => {
    const msgData = message.value || message;
    if (msgData.timestamp > lastUpdate) {
      lastUpdate = msgData.timestamp;
    }
  });
  
  return formatTime(lastUpdate);
};

// 切换消息选择状态
const toggleMessageSelection = (messageId) => {
  if (selectedMessages.value.has(messageId)) {
    selectedMessages.value.delete(messageId);
  } else {
    selectedMessages.value.add(messageId);
  }
};

// 选择所有消息
const selectAllMessages = () => {
  if (!chatStore.currentChat || !chatStore.currentChat.messages) return;
  
  const messages = chatStore.currentChat.messages;
  messages.forEach(message => {
    const msgData = message.value || message;
    selectedMessages.value.add(msgData.id);
  });
};

// 取消选择所有消息
const clearAllSelections = () => {
  selectedMessages.value.clear();
};

// 应用上下文调整
const applyContextChanges = () => {
  // 这里可以添加应用上下文调整的逻辑
  // 例如：更新上下文配置、发送到后端等
  showNotification('上下文调整已应用', 'success');
};

// 切换视图模式
const toggleView = () => {
  chatStore.activeView = chatStore.activeView === 'grid' ? 'list' : 'grid';
};

// 监听当前聊天变化，重置选择状态
watch(() => chatStore.currentChatId, () => {
  selectedMessages.value.clear();
});
</script>

<style scoped>
.panel-section {
  margin-bottom: 1rem;
}

.message-item {
  position: relative;
}

.message-item.selected {
  background-color: #e3f2fd !important;
  border-color: #90caf9 !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-item.dark:selected {
  background-color: #1a237e !important;
  border-color: #3949ab !important;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 深色模式滚动条 */
.dark ::-webkit-scrollbar-track {
  background: #333;
}

.dark ::-webkit-scrollbar-thumb {
  background: #666;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #888;
}
</style>