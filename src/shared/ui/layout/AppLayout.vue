<template>
  <!-- 统一的应用布局组件 -->
  <div class="app-layout h-screen flex flex-col overflow-hidden">
    <!-- 1. 顶部导航栏：动态加载不同的 header 组件 -->
    <header class="w-full px-4 sm:px-6 h-10 flex items-center justify-between gap-2 sticky top-0 bg-[#F8FAFC] dark:bg-dark-primary backdrop-blur-md z-30 border-b border-gray-100 dark:border-dark-700 transition-all duration-300">
      <!-- 动态渲染不同的头部组件内容 -->
      <component 
        :is="currentHeaderComponent" 
        v-bind="headerConfig.props" 
        v-on="headerConfig.events"
      />
    </header>

    <!-- 2. 主内容区域：左侧导航栏 + 主内容 + 右侧面板 -->
    <main class="flex flex-1 overflow-hidden">
      <!-- 左侧导航栏 -->
      <aside 
        v-if="settingsStore.leftNavVisible" 
        class="left-sidebar" 
        :style="{ width: settingsStore.leftNavWidth }"
      >
        <LeftSidebar />
      </aside>
      
      <!-- 主内容区域 - 使用路由视图 -->
      <section class="main-content flex-1 overflow-hidden w-full h-full flex flex-col">
        <router-view />
      </section>
      
      <!-- 右侧面板 -->
      <aside 
        v-if="settingsStore.rightPanelVisible" 
        class="right-sidebar" 
        :style="{ width: settingsStore.rightPanelWidth }"
      >
        <RightSidebar />
      </aside>
    </main>
  </div>
</template>

<script setup>
import { computed, defineAsyncComponent } from 'vue';
import { useSettingsStore } from '../../../app/store/settingsStore.js';
import { useAppHeader } from '../../../shared/composables/useAppHeader.js';

// 初始化 stores
const settingsStore = useSettingsStore();

// 使用应用头部组合式函数，动态管理不同页面的头部组件
const { headerConfig } = useAppHeader();

// 动态导入头部组件
const ChatHeader = defineAsyncComponent(() => import('../../../modules/conversation/components/headers/ChatHeader.vue'));
const SettingsHeader = defineAsyncComponent(() => import('../../../pages/chat/SettingsHeader.vue'));

// 导入侧边栏组件
const LeftSidebar = defineAsyncComponent(() => import('../../../pages/chat/LeftSidebar.vue'));
const RightSidebar = defineAsyncComponent(() => import('../../../pages/chat/RightSidebar.vue'));

// 统一的组件映射表
const componentMap = {
  // 头部组件映射
  'chat-header': ChatHeader,
  'settings-header': SettingsHeader
};

// 计算当前头部组件
const currentHeaderComponent = computed(() => {
  const headerType = headerConfig.component;
  return componentMap[headerType] || ChatHeader;
});
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