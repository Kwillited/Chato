<template>
  <div id="mainLayoutContainer" class="flex-1 flex flex-col bg-light dark:bg-dark-primary overflow-hidden" :class="{ 'transition-all duration-300': !isInitialLoading }">
    <!-- 整体导航栏 -->
    <LayoutHeader 
      :active-content="uiStore.activeContent"
      ref="headerRef"
    />
    
    <!-- 三栏内容区域 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 左侧面板 -->
      <LeftPanel ref="leftPanelRef" />
      
      <!-- 左侧分隔线 -->
      <div 
        id="LeftResizer" 
        class="resizer transition-all duration-300" 
        :class="{
          'resizer-disabled': !uiStore.leftNavVisible
        }"
        :style="{
          display: uiStore.leftNavVisible ? 'block' : 'none'
        }"
        @mousedown="startLeftResize"
      ></div>
      
      <!-- 主内容区域 -->
      <div 
        id="mainContent" 
        ref="mainContent"
        class="flex-1 flex flex-col overflow-hidden bg-light dark:bg-dark-primary transition-all duration-300"
      >
        <!-- 路由组件插槽 -->
        <slot></slot>
      </div>
      
      <!-- 右侧分隔线 -->
      <div 
        id="RightResizer" 
        class="resizer transition-all duration-300"
        :class="{
          'resizer-disabled': !uiStore.rightPanelVisible
        }"
        :style="{
          display: uiStore.rightPanelVisible ? 'block' : 'none'
        }"
        @mousedown="startRightResize"
      ></div>
      
      <!-- 右侧面板 -->
      <div 
        id="rightPanel"
        ref="rightPanelRef"
        class="h-full flex-shrink-0 z-40 overflow-hidden mr-0 max-w-[370px]"
        :class="{ 'transition-all duration-300': !isInitialLoading }"
        :style="{
          width: uiStore.rightPanelVisible ? uiStore.rightPanelWidth : 'auto',
          minWidth: uiStore.rightPanelVisible ? '200px' : 'auto',
          maxWidth: uiStore.rightPanelVisible ? '370px' : 'auto',
          flexShrink: 0
        }"
      >
        <!-- 根据当前激活的内容视图显示不同的右侧面板 -->
        <FileRightPanel 
          :saved-width="savedRightPanelWidth" 
          :is-initial-loading="isInitialLoading"
          v-if="uiStore.rightPanelVisible && uiStore.activeContent === 'fileManager'"
        />
        <AgentRightPanel 
          :saved-width="savedRightPanelWidth" 
          :is-initial-loading="isInitialLoading"
          v-else-if="uiStore.rightPanelVisible"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { useUiStore } from '../store/uiStore.js';
import { useChatStore } from '../store/chatStore.js';
import { usePanelResize } from '../composables/usePanelResize.js';
import LayoutHeader from '../components/layout/LayoutHeader.vue';
import LeftPanel from '../components/layout/LeftPanel.vue';
import AgentRightPanel from '../components/layout/AgentRightPanel.vue';
import FileRightPanel from '../components/layout/FileRightPanel.vue';

// Props
const props = defineProps({
  savedRightPanelWidth: {
    type: String,
    default: '256px'
  },
  isInitialLoading: {
    type: Boolean,
    default: true
  }
});

// Stores
const uiStore = useUiStore();
const chatStore = useChatStore();

// Refs
const headerRef = ref(null);
const leftPanelRef = ref(null);
const mainContent = ref(null);
const rightPanelRef = ref(null);

// 计算属性
const leftNavVisible = computed(() => uiStore.leftNavVisible);
const rightPanelVisible = computed(() => uiStore.rightPanelVisible);

// 计算中栏中心位置的函数
const updateTitlePosition = () => {
  if (!headerRef.value?.titleContainer || !mainContent.value) return;
  
  // 使用requestAnimationFrame优化视觉更新
  requestAnimationFrame(() => {
    // 获取左侧面板宽度
    let leftPanelWidth = 0;
    if (uiStore.leftNavVisible && leftPanelRef.value?.leftPanel) {
      leftPanelWidth = leftPanelRef.value.leftPanel.offsetWidth;
    }
    // 获取主内容区宽度
    const mainContentWidth = mainContent.value.offsetWidth;
    // 计算中栏中心位置
    const centerPosition = leftPanelWidth + (mainContentWidth / 2);
    
    // 设置标题容器的位置
    const titleContainer = headerRef.value.titleContainer;
    titleContainer.style.position = 'absolute';
    titleContainer.style.left = `${centerPosition}px`;
    titleContainer.style.transform = 'translateX(-50%)';
    titleContainer.style.flex = 'none';
    titleContainer.style.width = 'auto';
  });
};

// 使用面板调整组合式函数
const { startLeftResize, startRightResize } = usePanelResize(
  leftNavVisible,
  rightPanelVisible,
  uiStore,
  updateTitlePosition
);

// 组件挂载时初始化
onMounted(() => {
  // 初始化右侧面板宽度
  const rightPanelEl = document.getElementById('rightPanel');
  if (rightPanelEl && uiStore.rightPanelVisible) {
    rightPanelEl.style.width = props.savedRightPanelWidth;
  }
  
  // 初始化标题位置
  updateTitlePosition();
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', updateTitlePosition);
});

// 监听右侧面板可见性变化
watch(
  () => uiStore.rightPanelVisible,
  () => {
    // 立即更新标题位置
    updateTitlePosition();
  }
);

// 监听左侧面板可见性变化
watch(
  () => uiStore.leftNavVisible,
  () => {
    // 立即更新标题位置
    updateTitlePosition();
  }
);

// 监听激活内容变化，确保对话切换时标题位置正确
watch(
  () => uiStore.activeContent,
  () => {
    // 立即更新标题位置
    updateTitlePosition();
  }
);

// 监听对话切换，确保标题位置正确
watch(
  () => chatStore.currentChatId,
  () => {
    // 立即更新标题位置
    updateTitlePosition();
  }
);

// 组件卸载时清理
onUnmounted(() => {
  // 确保移除所有事件监听器
  document.removeEventListener('mousemove', resizePanel);
  document.removeEventListener('mouseup', stopResize);
  document.removeEventListener('mouseleave', stopResize);
  window.removeEventListener('resize', updateTitlePosition);
});
</script>

<style scoped>
/* 主布局样式 */
</style>