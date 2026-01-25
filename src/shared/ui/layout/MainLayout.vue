<template>
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
    
    <!-- 主内容区域 -->
    <section class="main-content flex-1 overflow-hidden">
      <DisplayArea 
        :active-content="settingsStore.activeContent" 
        :saved-right-panel-width="settingsStore.rightPanelWidth" 
        :is-initial-loading="isInitialLoading"
      />
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
</template>

<script setup>
import { useSettingsStore } from '../../../app/store/settingsStore.js';
import LeftSidebar from './LeftSidebar.vue';
import RightSidebar from './RightSidebar.vue';
import DisplayArea from '../../../pages/chat/DisplayArea.vue';

// 定义组件属性
const props = defineProps({
  // 初始加载状态，用于控制首次加载时的动画
  isInitialLoading: {
    type: Boolean,
    default: false
  }
});

// 初始化stores
const settingsStore = useSettingsStore();
</script>

<style scoped>
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
</style>