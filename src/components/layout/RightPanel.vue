<template>
  <div 
    class="h-full overflow-hidden"
  >
    <!-- 右侧面板内容 -->
    <div class="h-full flex flex-col">
      <!-- 面板切换按钮 -->
      <div class="p-3 pb-0">
        <div class="flex space-x-1 bg-gray-100 dark:bg-dark-700 p-1 rounded-lg">
          <button
            class="flex-1 text-xs py-1 px-2 rounded transition-all duration-300"
            :class="{
              'bg-white dark:bg-dark-600 text-gray-900 dark:text-white shadow-sm': activePanel === 'context',
              'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-dark-600': activePanel !== 'context'
            }"
            @click="activePanel = 'context'"
          >
            上下文管理
          </button>
          <button
            class="flex-1 text-xs py-1 px-2 rounded transition-all duration-300"
            :class="{
              'bg-white dark:bg-dark-600 text-gray-900 dark:text-white shadow-sm': activePanel === 'prompt',
              'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-dark-600': activePanel !== 'prompt'
            }"
            @click="activePanel = 'prompt'"
          >
            提示词工程
          </button>
        </div>
      </div>
      
      <!-- 面板内容区域 -->
      <div class="flex-1 p-3">
        <!-- 上下文管理面板 -->
        <div v-if="activePanel === 'context'" class="flex flex-col">
          <!-- 上下文概述 -->
          <div class="mb-4">
            <h3 class="text-sm font-semibold text-gray-500 mb-2">上下文概述</h3>
            <div class="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700 p-3">
              <div class="space-y-1">
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">当前会话: {{ chatStore.currentChat?.title || '无' }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">上下文数量: {{ getContextCount() }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">输入Token: {{ getInputTokens() }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">输出Token: {{ getOutputTokens() }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">总Token: {{ getTotalTokens() }}</p>
                <p class="text-sm text-gray-600 dark:text-dark-text-secondary">最新更新: {{ getLastUpdateTime() }}</p>
              </div>
            </div>
          </div>
          
          <!-- 上下文筛选 -->
          <div class="flex-1 flex flex-col">
            <div class="flex justify-between items-center mb-2">
              <h3 class="text-sm font-semibold text-gray-500">上下文筛选</h3>
              <div class="flex space-x-2">
                <Button
                  shape="rounded"
                  size="md"
                  variant="secondary"
                  icon="fa-check-square"
                  tooltip="全选"
                  @click="selectAllMessages"
                />
                <Button
                  shape="rounded"
                  size="md"
                  variant="secondary"
                  icon="fa-square"
                  tooltip="取消全选"
                  @click="clearAllSelections"
                />
              </div>
            </div>
            
            <div class="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700 h-[calc(100vh-360px)] overflow-hidden flex flex-col mb-4">
              <div class="flex-1 overflow-y-auto p-2 scrollbar-thin">
                <!-- 消息列表 -->
                <div v-if="chatStore.currentChat && chatStore.currentChat.messages && chatStore.currentChat.messages.length > 0">
                  <div
                    v-for="message in chatStore.currentChat.messages"
                    :key="message.value?.id || message.id"
                    class="message-item mb-3 p-2 rounded border border-gray-200 dark:border-dark-border hover:bg-gray-100 dark:hover:bg-dark-700 transition-colors"
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
          </div>
        </div>
        
        <!-- 提示词工程面板 -->
        <div v-else-if="activePanel === 'prompt'" class="h-full flex flex-col">
          <div class="panel-section flex-1 flex flex-col">
            <!-- 提示词类型选择标签页 -->
            <div class="flex space-x-1 mb-2 bg-gray-100 dark:bg-dark-700 p-1 rounded-lg">
              <button
                v-for="tab in reorderedPromptTabs"
                :key="tab.id"
                class="flex-1 text-xs py-1 px-2 rounded transition-all duration-300"
                :class="{
                  'bg-white dark:bg-dark-600 text-gray-900 dark:text-white shadow-sm': activePromptTab === tab.id,
                  'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-dark-600': activePromptTab !== tab.id
                }"
                @click="activePromptTab = tab.id"
              >
                {{ tab.name }}
              </button>
            </div>
            
            <!-- 提示词编辑区域 -->
            <div class="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700 flex-1 overflow-hidden flex flex-col">
              <!-- 系统提示词 -->
              <div v-if="activePromptTab === 'system'" class="flex-1 flex flex-col space-y-3 pt-2 pb-4">
                <textarea
                  v-model="promptTemplates.system"
                  class="flex-1 w-full text-xs p-3 border border-gray-200 dark:border-dark-border rounded-lg bg-white text-gray-900 dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-200 shadow-sm"
                  placeholder="输入系统提示词模板...\n\n示例:\n你是一个智能助手，负责..."
                ></textarea>
                <div class="flex justify-between items-center pt-1">
                  <span class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                    <i class="fa-solid fa-file-lines text-xs"></i>
                    {{ promptTemplates.system.length }} 字符
                  </span>
                  <Button
                    shape="full"
                    size="sm"
                    icon="fa-save"
                    tooltip="保存系统提示词"
                    @click="savePromptTemplate('system')"
                    class="transition-all duration-200 hover:scale-105"
                    :class="{
                      'bg-primary hover:bg-primary/90 text-white': true
                    }"
                  />
                </div>
              </div>
              
              <!-- RAG提示词 -->
              <div v-else-if="activePromptTab === 'rag'" class="flex-1 flex flex-col space-y-3 pt-2 pb-4">
                <textarea
                  v-model="promptTemplates.rag"
                  class="flex-1 w-full text-xs p-3 border border-gray-200 dark:border-dark-border rounded-lg bg-white text-gray-900 dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-200 shadow-sm"
                  placeholder="输入RAG提示词模板...\n\n示例:\n基于以下上下文信息，回答用户问题..."
                ></textarea>
                <div class="flex justify-between items-center pt-1">
                  <span class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                    <i class="fa-solid fa-file-lines text-xs"></i>
                    {{ promptTemplates.rag.length }} 字符
                  </span>
                  <Button
                    shape="full"
                    size="sm"
                    icon="fa-save"
                    tooltip="保存RAG提示词"
                    @click="savePromptTemplate('rag')"
                    class="transition-all duration-200 hover:scale-105"
                    :class="{
                      'bg-primary hover:bg-primary/90 text-white': true
                    }"
                  />
                </div>
              </div>
              
              <!-- 智能体提示词 -->
              <div v-else-if="activePromptTab === 'agent'" class="flex-1 flex flex-col space-y-3 pt-2 pb-4">
                <textarea
                  v-model="promptTemplates.agent"
                  class="flex-1 w-full text-xs p-3 border border-gray-200 dark:border-dark-border rounded-lg bg-white text-gray-900 dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-200 shadow-sm"
                  placeholder="输入智能体提示词模板...\n\n示例:\n你是一个专业的智能体，需要..."
                ></textarea>
                <div class="flex justify-between items-center pt-1">
                  <span class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                    <i class="fa-solid fa-file-lines text-xs"></i>
                    {{ promptTemplates.agent.length }} 字符
                  </span>
                  <Button
                    shape="full"
                    size="sm"
                    icon="fa-save"
                    tooltip="保存智能体提示词"
                    @click="savePromptTemplate('agent')"
                    class="transition-all duration-200 hover:scale-105"
                    :class="{
                      'bg-primary hover:bg-primary/90 text-white': true
                    }"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { useUiStore } from '../../store/uiStore.js';
import { Button } from '../library/index.js';
import { showNotification } from '../../utils/notificationUtils.js';
import { ref, watch } from 'vue';
// 导入公共工具函数
import { formatTime } from '../../utils/time.js';

// 定义props
const _props = defineProps({
  isInitialLoading: {
    type: Boolean,
    default: true
  }
});

// 初始化stores
const settingsStore = useSettingsStore();
const _modelStore = useSettingsStore();
const chatStore = useChatStore();
const uiStore = useUiStore();

// 上下文调整状态
const selectedMessages = ref(new Set());

// 面板切换状态
const activePanel = ref('context');

// 提示词工程状态
const promptTabs = [
  { id: 'rag', name: 'RAG提示词' },
  { id: 'system', name: '系统提示词' },
  { id: 'agent', name: '智能体提示词' }
];
// 交换RAG提示词和系统提示词的位置
const reorderedPromptTabs = [
  { id: 'system', name: '系统' },
  { id: 'rag', name: 'RAG' },
  { id: 'agent', name: '智能体' }
];
const activePromptTab = ref('rag');
const promptTemplates = ref({
  rag: '',
  system: '',
  agent: ''
});

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





// 保存提示词模板
const savePromptTemplate = (type) => {
  // 这里可以添加保存提示词模板的逻辑
  // 例如：更新到设置存储、发送到后端等
  showNotification(`${promptTabs.find(tab => tab.id === type)?.name}已保存`, 'success');
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

/* 滚动条样式 - 使用全局scrollbar-thin样式，与文件面板保持一致 */
</style>