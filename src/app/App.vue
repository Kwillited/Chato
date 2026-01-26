<template>
  <!-- 根组件：只渲染路由视图 -->
  <router-view />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useChatStore } from './store/chatStore.js';
import { useSettingsStore } from './store/settingsStore.js';
import { apiService } from '../shared/api/apiService.js';
import logger from '../shared/utils/logger.js';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();

// 初始加载状态
const isInitialLoading = ref(true);

// 初始化应用
onMounted(async () => {
  // 执行健康检查，使用优化后的重试机制
  const isBackendHealthy = await checkBackendHealth();
  
  // 根据后端健康状态加载数据
  await initializeAppData(isBackendHealthy);

  logger.info('AIClient应用已初始化，使用Vue Router路由管理');
  
  // 初始化完成
  isInitialLoading.value = false;
});

// 检查后端健康状态 - 封装为独立函数
async function checkBackendHealth() {
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
    return true;
  } catch {
    logger.error('后端服务健康检查失败，已达到最大重试次数');
    return false;
  }
}

// 初始化应用数据 - 封装为独立函数
async function initializeAppData(isBackendHealthy) {
  if (isBackendHealthy) {
    logger.info('后端服务健康，开始加载应用数据...');
    
    // 并行加载非依赖数据，提高初始化速度
    await Promise.all([
      settingsStore.loadSettings(),
      settingsStore.loadModels().catch(error => {
        logger.error('初始化加载模型数据失败:', error);
      })
    ]);

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
}
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
