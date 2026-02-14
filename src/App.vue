<template>
  <div 
    class="app-container h-screen flex flex-col overflow-hidden bg-light text-dark dark:bg-dark-primary dark:text-light"
    :class="{ 'transition-all duration-300': !isInitialLoading }"
  >
    <!-- 路由视图：渲染当前路由对应的组件 -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <MainLayout 
          :saved-right-panel-width="uiStore.rightPanelWidth" 
          :is-initial-loading="isInitialLoading"
        >
          <component :is="Component" :key="$route.path" />
        </MainLayout>
      </transition>
    </router-view>

    <!-- 模型版本表单（支持添加和编辑） -->
    <ModelVersionForm />

    <!-- 模型配置抽屉 -->
    <ModelSettingsDrawer />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useNavigation } from './composables/useNavigation.js';
import ModelVersionForm from './components/models/ModelVersionForm.vue';
import ModelSettingsDrawer from './components/models/ModelSettingsDrawer.vue';
import MainLayout from './layout/MainLayout.vue';
import { useChatStore } from './store/chatStore.js';
import { useSettingsStore } from './store/settingsStore.js';
import { useUiStore } from './store/uiStore.js';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();
const uiStore = useUiStore();

// 路由
const route = useRoute();
const router = useRouter();

// 导航管理
const { handleRouteChange, handleStateDrivenRouting } = useNavigation();

// 初始加载状态，用于控制首次加载时的动画
const isInitialLoading = ref(true);

// 监听路由变化，更新应用状态
watch(
  () => route,
  async (newRoute) => {
    await handleRouteChange(newRoute, router);
  },
  {
    immediate: true,
    deep: true
  }
);

// 监听currentChatId变化，实现状态驱动路由
watch(
  () => chatStore.currentChatId,
  (newChatId) => {
    handleStateDrivenRouting(newChatId, route.path, router);
  }
);

import { apiService } from './services/apiService.js';

// 初始化应用
onMounted(async () => {
  let isBackendHealthy = false;
  
  // 执行健康检查，使用优化后的重试机制
  try {
    await apiService.requestWithRetry(
      { method: 'GET', url: '/health' },
      { 
        maxRetries: 8,       // 健康检查需要更多重试次数
        initialDelay: 500,   // 初始延迟500ms
        backoffFactor: 1.5,  // 指数退避
        maxDelay: 8000,      // 最大延迟8秒
        retryableStatusCodes: [404, 500, 502, 503, 504], // 包含404以便使用fallback
        jitter: 0.1          // 随机抖动
      }
    );
    console.log('后端服务健康检查通过！');
    isBackendHealthy = true;
  } catch {
    console.error('后端服务健康检查失败，已达到最大重试次数');
    isBackendHealthy = false;
  }
  
  // 只有在后端服务健康时，才加载设置、模型和聊天历史
  if (isBackendHealthy) {
    console.log('后端服务健康，开始加载应用数据...');
    
    // 加载用户设置和数据
    await settingsStore.loadSettings();
    
    // 加载模型数据
    try {
      await settingsStore.loadModels();
    } catch (error) {
      console.error('初始化加载模型数据失败:', error);
    }

    // 异步加载对话历史（非阻塞方式）
    chatStore.loadChatHistory().catch(error => {
      console.error('初始化加载对话历史失败，但应用继续运行:', error);
    });
  } else {
    console.error('后端服务不可用，应用将以有限功能运行');
    // 仅从本地存储加载设置，不请求API
    await settingsStore.loadSettingsFromStorageOnly();
    // 可以在这里添加用户友好的提示，比如显示一个通知
    // showNotification('后端服务连接失败，请检查服务状态', 'error');
  }

  // 初始化默认面板
  if (!uiStore.activePanel) {
    uiStore.setActivePanel('history');
  }

  console.log('AIClient应用已初始化，使用Pinia状态管理');
  
  // 初始化完成，启用动画
  isInitialLoading.value = false;
});
</script>

<style>
.resizer.resizing {
  background-color: #94a3b8;
}

/* 添加面板过渡动画 */
#panelContainer {
  transition: width 0.3s ease;
  min-width: 0;
}

/* 隐藏状态样式 */
.hidden {
  display: none !important;
}

/* 不可用状态的调整器样式 */
.resizer-disabled {
  cursor: not-allowed !important;
  opacity: 0.5;
  pointer-events: none;
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
