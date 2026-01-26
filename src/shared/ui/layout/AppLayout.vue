<template>
  <!-- 统一的应用布局组件 -->
  <div class="app-layout h-screen flex flex-col overflow-hidden">
    <!-- 1. 顶部导航栏：提供基础header结构，根据路由动态切换header组件 -->
    <header class="w-full px-4 sm:px-6 h-10 flex items-center justify-between gap-2 sticky top-0 bg-[#F8FAFC] dark:bg-dark-primary backdrop-blur-md z-30 border-b border-gray-100 dark:border-dark-700 transition-all duration-300">
      <!-- 头部内容插槽，允许子组件定制header -->
      <slot name="header">
        <!-- 根据当前路由动态渲染合适的header组件 -->
        <template v-if="currentRoute === '/settings'">
          <SettingsHeader 
            title="ChaTo Setting & Configuration"
            :active-tab="activeTab"
            @back="handleBackToHome"
            @tab-change="handleTabChange"
          />
        </template>
        <template v-else>
          <!-- 默认的ChatHeader，用于聊天页面 -->
          <ChatHeader 
            :title="defaultHeaderTitle" 
            :chat-history="chatHistory" 
            @toggle-side-menu="handleSideMenuToggle"
            @new-chat="handleNewChat"
            @select-history-chat="handleSelectHistoryChat"
          />
        </template>
      </slot>
    </header>

    <!-- 2. 主内容区域：左侧导航栏 + 主内容 + 右侧面板 -->
    <main class="flex flex-1 overflow-hidden">
      <!-- 左侧导航栏 -->
      <aside 
        v-if="leftNavVisible" 
        class="left-sidebar" 
        :style="{ width: leftNavWidth }"
      >
        <!-- 根据activeSidebar动态渲染不同的侧边栏组件 -->
        <MessageListSidebar v-if="activeSidebar === 'message'" />
        <FolderListSidebar v-else-if="activeSidebar === 'folder'" />
        <MCPToolListSidebar v-else-if="activeSidebar === 'mcp'" />
        <LeftSidebar v-else />
      </aside>
      
      <!-- 主内容区域 - 使用路由视图 -->
      <section class="main-content flex-1 overflow-hidden w-full h-full flex flex-col">
        <router-view />
      </section>
      
      <!-- 右侧面板 -->
      <aside 
        v-if="rightPanelVisible" 
        class="right-sidebar" 
        :style="{ width: rightPanelWidth }"
      >
        <RightSidebar />
      </aside>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useSettingsStore } from '../../../app/store/settingsStore.js';
import { useChatHeader } from '../../../modules/conversation';
import { useAppUI } from '../../../shared/composables/useAppUI.js';
import ChatHeader from '../../../modules/conversation/components/headers/ChatHeader.vue';
import SettingsHeader from '../../../pages/chat/SettingsHeader.vue';
import { defineAsyncComponent } from 'vue';
import { useRouter } from 'vue-router';

// 初始化 stores
const settingsStore = useSettingsStore();
const router = useRouter();

// 使用应用UI状态组合式函数
const {
  leftNavVisible,
  leftNavWidth,
  rightPanelVisible,
  rightPanelWidth,
  activeTab,
  activeSidebar,
  toggleLeftNav,
  setActiveTab,
  setActiveSidebar
} = useAppUI();

// 使用聊天头部组合式函数获取默认header所需的数据
const {
  handleNewChat,
  handleSelectHistoryChat,
  getCurrentChatTitle,
  chatHistory
} = useChatHeader();

// 监听路由变化，更新当前路由
const currentRoute = ref(router.currentRoute.value.path);

// 监听路由变化
watch(() => router.currentRoute.value, (newRoute) => {
  currentRoute.value = newRoute.path;
}, { immediate: true });

// 默认header标题
const defaultHeaderTitle = computed(() => {
  return getCurrentChatTitle();
});

// 返回首页
const handleBackToHome = () => {
  router.push('/');
};

// 处理标签切换
const handleTabChange = (tabValue) => {
  setActiveTab(tabValue);
};

// 切换侧边菜单可见性
const handleSideMenuToggle = () => {
  toggleLeftNav();
};

// 导入侧边栏组件
const LeftSidebar = defineAsyncComponent(() => import('../../../pages/chat/LeftSidebar.vue'));
const FolderListSidebar = defineAsyncComponent(() => import('../../../pages/chat/FolderListSidebar.vue'));
const MessageListSidebar = defineAsyncComponent(() => import('../../../pages/chat/MessageListSidebar.vue'));
const MCPToolListSidebar = defineAsyncComponent(() => import('../../../pages/chat/MCPToolListSidebar.vue'));
const RightSidebar = defineAsyncComponent(() => import('../../../pages/chat/RightSidebar.vue'));
</script>

<style scoped>
/* 应用布局容器样式 */
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background-color: #f8fafc;
  color: #1e293b;
  transition: all 0.3s ease;
}

/* 主内容区域样式 */
.main-content {
  background-color: inherit;
  transition: all 0.3s ease;
  overflow: hidden;
}

/* 侧边栏容器样式 */
.left-sidebar,
.right-sidebar {
  background-color: inherit;
  height: 100%;
  transition: all 0.3s ease;
  overflow: hidden;
}

/* 确保按钮和内容的交互效果一致 */
button {
  transition: all 0.2s ease;
}

button:active {
  transform: scale(0.98);
}

/* 深色模式适配 */
.dark {
  background-color: #0f172a;
  color: #f1f5f9;
}

/* 高度100% */
.height-full {
  height: 100%;
}

/* 背景继承 */
.bg-inherit {
  background-color: inherit;
}
</style>