<template>
  <div 
    class="app-container h-screen flex flex-col overflow-hidden bg-light text-dark dark:bg-dark-primary dark:text-light"
    :class="{ 'transition-all duration-300': !isInitialLoading }"
  >
    <!-- 1. 顶部导航栏 -->
    <TopNav/>

    <!-- 主内容区域：显示区域 -->
    <div class="flex flex-1 overflow-hidden">
      <!-- 3. 显示区域容器 -->
      <DisplayArea 
        :active-content="settingsStore.activeContent" 
        :saved-right-panel-width="settingsStore.rightPanelWidth" 
        :is-initial-loading="isInitialLoading"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import TopNav from '../shared/ui/TopNav.vue';
import DisplayArea from '../pages/chat/DisplayArea.vue';
import { useChatStore } from './store/chatStore.js';
import { useSettingsStore } from './store/settingsStore.js';
import { apiService } from '../shared/api/apiService.js';
import logger from '../shared/utils/logger.js'; // 引入日志工具

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();

// 初始加载状态，用于控制首次加载时的动画
const isInitialLoading = ref(true);

// 监听activePanel变化，同步更新activeContent
watch(
  () => settingsStore.activePanel,
  (newPanel) => {
    // 只有当前视图不是sendMessage时，才根据activePanel更新视图
    if (settingsStore.activeContent !== 'sendMessage') {
      if (newPanel === 'settings') {
        settingsStore.setActiveContent('settings');
      } else {
        // 当面板不是settings时，切换回chat内容
        settingsStore.setActiveContent('chat');
      }
    }
  }
);

// 初始化应用
onMounted(async () => {
  let isBackendHealthy = false;
  
  // 执行健康检查，使用优化后的重试机制
  try {
    await apiService.requestWithRetry(
      { method: 'GET', url: '/api/health' },
      { 
        maxRetries: 8,       // 健康检查需要更多重试次数
        initialDelay: 500,   // 初始延迟500ms
        backoffFactor: 1.5,  // 指数退避
        maxDelay: 8000,      // 最大延迟8秒
        retryableStatusCodes: [404, 500, 502, 503, 504], // 包含404以便使用fallback
        jitter: 0.1          // 随机抖动
      }
    );
    logger.info('后端服务健康检查通过！');
    isBackendHealthy = true;
  } catch {
    logger.error('后端服务健康检查失败，已达到最大重试次数');
    isBackendHealthy = false;
  }
  
  // 只有在后端服务健康时，才加载设置、模型和聊天历史
  if (isBackendHealthy) {
    logger.info('后端服务健康，开始加载应用数据...');
    
    // 加载用户设置和数据
    await settingsStore.loadSettings();
    
    // 加载模型数据
    try {
      await settingsStore.loadModels();
    } catch (error) {
      logger.error('初始化加载模型数据失败:', error);
    }

    // 异步加载对话历史（非阻塞方式）
    chatStore.loadChatHistory().catch(error => {
      logger.error('初始化加载对话历史失败，但应用继续运行:', error);
    });
  } else {
    logger.error('后端服务不可用，应用将以有限功能运行');
    // 仅从本地存储加载设置，不请求API
    await settingsStore.loadSettingsFromStorageOnly();
    // 可以在这里添加用户友好的提示，比如显示一个通知
    // showNotification('后端服务连接失败，请检查服务状态', 'error');
  }

  // 初始化默认面板
  if (!settingsStore.activePanel) {
    settingsStore.setActivePanel('history');
  }

  logger.info('AIClient应用已初始化，使用Pinia状态管理');
  
  // 初始化完成，启用动画
  isInitialLoading.value = false;
});
</script>

<style scoped>
/* App 组件特定样式 */
</style>
