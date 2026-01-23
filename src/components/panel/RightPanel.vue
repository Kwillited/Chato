<template>
  <div 
    id="rightPanel" 
    class="h-full flex flex-col bg-white dark:bg-dark-secondary"
  >
    <!-- 内容区 -->
    <div class="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin">
      <!-- 统计卡片 -->
      <section>
        <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">概览</h3>
        <div class="bg-gray-50 dark:bg-dark-tertiary rounded-xl p-4 text-sm space-y-2 border dark:border-dark-700">
          <div class="flex justify-between">
            <span class="text-gray-500">消息数</span>
            <span class="font-mono font-medium">{{ contextCount }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">总 Token (估算)</span>
            <span class="font-mono font-medium text-primary">{{ totalTokens }}</span>
          </div>
          <div class="h-px bg-gray-200 dark:bg-dark-600 my-2"></div>
          <div class="text-xs text-gray-400 text-right">上次更新: {{ lastUpdateTime }}</div>
        </div>
      </section>
      
      <!-- 消息筛选列表 -->
      <section class="flex flex-col h-full min-h-[300px]">
        <div class="flex justify-between items-center mb-3">
          <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider">上下文筛选</h3>
          <div class="flex gap-1">
            <button class="text-xs text-primary hover:underline" @click="selectAllMessages">全选</button>
            <span class="text-gray-300">|</span>
            <button class="text-xs text-gray-500 hover:text-gray-700 hover:underline" @click="clearAllSelections">清空</button>
          </div>
        </div>
        
        <div class="flex-1 bg-gray-50 dark:bg-dark-tertiary rounded-xl border dark:border-dark-700 overflow-hidden flex flex-col">
          <div class="flex-1 overflow-y-auto p-2 scrollbar-thin">
            <template v-if="messages.length > 0">
              <div
                v-for="msg in messages"
                :key="msg.id"
                class="group flex gap-3 p-2 rounded-lg hover:bg-white dark:hover:bg-dark-600 border border-transparent hover:border-gray-200 dark:hover:border-dark-500 transition-all cursor-pointer mb-1"
                :class="{ 'bg-blue-50 dark:bg-blue-900/20 border-blue-200': selectedMessages.has(msg.id) }"
                @click="toggleMessageSelection(msg.id)"
              >
                <div class="pt-1">
                  <input
                    type="checkbox"
                    :checked="selectedMessages.has(msg.id)"
                    class="rounded text-primary focus:ring-primary cursor-pointer"
                  />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex justify-between items-center mb-1">
                    <span 
                      class="text-[10px] font-bold px-1.5 py-0.5 rounded"
                      :class="msg.role === 'user' ? 'bg-gray-200 text-gray-700' : 'bg-primary/10 text-primary'"
                    >
                      {{ msg.role === 'user' ? 'USER' : 'AI' }}
                    </span>
                    <span class="text-[10px] text-gray-400">{{ formatTime(msg.timestamp) }}</span>
                  </div>
                  <p class="text-xs text-gray-600 dark:text-gray-300 line-clamp-2">{{ msg.content }}</p>
                </div>
              </div>
            </template>
            <div v-else class="h-full flex items-center justify-center text-gray-400 text-xs">
              暂无消息
            </div>
          </div>
        </div>
        
        <div class="mt-3 flex justify-end">
             <ActionButton
                icon="fa-check"
                title="应用选择"
                label="应用上下文"
                class="bg-primary text-white hover:bg-primary-hover px-4"
                @click="applyContextChanges"
                :disabled="selectedMessages.size === 0"
              />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import ActionButton from '../common/ActionButton.vue';
import { showNotification } from '../../services/notificationUtils.js';
import { formatTime } from '../../store/utils.js';

const settingsStore = useSettingsStore();
const chatStore = useChatStore();

// 状态
const selectedMessages = ref(new Set());

// 简化 Computed，移除 .value?. 写法，假设 Pinia State 结构规范
const messages = computed(() => chatStore.currentChat?.messages || []);

const contextCount = computed(() => messages.value.length);

// 简易 Token 计算
const estimateTokens = (text = '') => {
  const chinese = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
  const other = text.length - chinese;
  return Math.ceil(chinese * 0.6 + other * 0.25); // 稍微调整了系数
};

const totalTokens = computed(() => {
  return messages.value.reduce((acc, msg) => acc + estimateTokens(msg.content), 0);
});

const lastUpdateTime = computed(() => {
  if (!messages.value.length) return '无';
  const last = messages.value[messages.value.length - 1];
  return formatTime(last.timestamp);
});

// 操作方法
const toggleMessageSelection = (id) => {
  const newSet = new Set(selectedMessages.value);
  if (newSet.has(id)) newSet.delete(id);
  else newSet.add(id);
  selectedMessages.value = newSet;
};

const selectAllMessages = () => {
  selectedMessages.value = new Set(messages.value.map(m => m.id));
};

const clearAllSelections = () => {
  selectedMessages.value = new Set();
};

const applyContextChanges = () => {
  // 实际业务逻辑：通知 LLM 仅使用选中的上下文
  console.log('Selected context IDs:', [...selectedMessages.value]);
  showNotification(`已应用 ${selectedMessages.value.size} 条上下文消息`, 'success');
};

const toggleView = () => {
  chatStore.activeView = chatStore.activeView === 'grid' ? 'list' : 'grid';
};

// 监听会话切换，清空选择
watch(() => chatStore.currentChatId, () => {
  selectedMessages.value.clear();
  // 默认可能需要全选，视业务而定
  // selectAllMessages(); 
});
</script>