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
        <RightPanel 
          :saved-width="savedRightPanelWidth" 
          :is-initial-loading="isInitialLoading"
          v-if="uiStore.rightPanelVisible"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useUiStore } from '../store/uiStore.js';
import { useChatStore } from '../store/chatStore.js';
import LayoutHeader from '../components/layout/LayoutHeader.vue';
import LeftPanel from '../components/layout/LeftPanel.vue';
import RightPanel from '../components/layout/RightPanel.vue';

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

// 调整状态
const isResizing = ref(false);
let startX = 0;
let startWidth = 0;
let resizeType = '';
let resizeRequestId = null;

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

// 实现面板大小调整功能
const initResize = (e, type) => {
  // 如果面板不可见，不允许调整大小
  if ((type === 'right' && !uiStore.rightPanelVisible) || 
      (type === 'left' && !uiStore.leftNavVisible)) {
    return;
  }
  
  isResizing.value = true;
  resizeType = type;
  startX = e.clientX;
  
  const panelElement = type === 'left' ? document.getElementById('panelContainer') : document.getElementById('rightPanel');
  startWidth = panelElement ? panelElement.offsetWidth : 0;
  
  // 禁用过渡效果以便在拖动时立即响应
  if (panelElement) {
    panelElement.style.transition = 'none';
  }
  
  // 添加调整大小的临时样式
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
  const mainContent = document.getElementById('mainContent');
  if (mainContent) {
    mainContent.style.pointerEvents = 'none';
  }
  
  const resizer = document.getElementById(type === 'left' ? 'LeftResizer' : 'RightResizer');
  if (resizer) {
    resizer.classList.add('resizing');
  }
  
  // 添加事件监听器
  document.addEventListener('mousemove', resizePanel);
  document.addEventListener('mouseup', stopResize);
  document.addEventListener('mouseleave', stopResize);
  
  // 阻止默认行为和事件冒泡
  e.preventDefault();
  e.stopPropagation();
};

const resizePanel = (e) => {
  if (!isResizing.value) return;
  
  // 取消上一个动画帧请求
  if (resizeRequestId) {
    cancelAnimationFrame(resizeRequestId);
  }
  
  // 使用requestAnimationFrame优化动画性能
  resizeRequestId = requestAnimationFrame(() => {
    // 获取元素
    const leftPanel = document.getElementById('panelContainer');
    const rightPanel = document.getElementById('rightPanel');
    const mainLayoutContainer = document.getElementById('mainLayoutContainer');
    
    if (!leftPanel || !rightPanel || !mainLayoutContainer) return;
    
    // 计算宽度变化，右侧面板调整方向相反
    const isRightPanel = resizeType === 'right';
    const widthChange = isRightPanel ? (startX - e.clientX) : (e.clientX - startX);
    let newWidth = startWidth + widthChange;
    
    // 设置最小和最大宽度限制
    const minWidth = 200; // 最小宽度为200px
    const panelMaxWidth = 370; // 所有面板的最大宽度为370px
    const mainContentMinWidth = 300; // 主内容区最小宽度
    
    // 获取当前所有面板的宽度
    const leftPanelWidth = uiStore.leftNavVisible ? leftPanel.offsetWidth : 0;
    const rightPanelWidth = uiStore.rightPanelVisible ? rightPanel.offsetWidth : 0;
    
    // 计算可用总宽度
    const availableWidth = mainLayoutContainer.offsetWidth;
    
    // 计算最大宽度：可用总宽度 - 主内容区最小宽度 - 另一侧面板宽度
    let maxWidth;
    if (!isRightPanel) {
      // 左侧面板最大宽度：取计算值和固定最大值中的较小值
      const calculatedMaxWidth = availableWidth - mainContentMinWidth - rightPanelWidth;
      maxWidth = Math.min(panelMaxWidth, calculatedMaxWidth);
    } else {
      // 右侧面板最大宽度：取计算值和固定最大值中的较小值
      const calculatedMaxWidth = availableWidth - mainContentMinWidth - leftPanelWidth;
      maxWidth = Math.min(panelMaxWidth, calculatedMaxWidth);
    }
    
    // 确保最大宽度不小于最小宽度
    maxWidth = Math.max(minWidth, maxWidth);
    
    // 限制新宽度在合理范围内
    newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
    
    // 更新面板宽度
    const panelElement = isRightPanel ? rightPanel : leftPanel;
    panelElement.style.width = `${newWidth}px`;
    
    // 更新store中的宽度
    if (isRightPanel) {
      uiStore.setRightNavWidth(`${newWidth}px`);
    } else {
      uiStore.setLeftNavWidth(`${newWidth}px`);
    }
  });
};

const stopResize = () => {
  if (!isResizing.value) return;
  
  isResizing.value = false;
  
  // 重新启用过渡效果
  const leftPanel = document.getElementById('panelContainer');
  const rightPanel = document.getElementById('rightPanel');
  if (leftPanel) {
    leftPanel.style.transition = 'width 0.2s ease-out';
  }
  if (rightPanel) {
    rightPanel.style.transition = 'width 0.2s ease-out';
  }
  
  // 移除临时样式
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  const mainContent = document.getElementById('mainContent');
  if (mainContent) {
    mainContent.style.pointerEvents = '';
  }
  
  // 移除resizing类
  const leftResizer = document.getElementById('LeftResizer');
  const rightResizer = document.getElementById('RightResizer');
  if (leftResizer) {
    leftResizer.classList.remove('resizing');
  }
  if (rightResizer) {
    rightResizer.classList.remove('resizing');
  }
  
  // 移除事件监听器
  document.removeEventListener('mousemove', resizePanel);
  document.removeEventListener('mouseup', stopResize);
  document.removeEventListener('mouseleave', stopResize);
  
  // 取消最后一个动画帧请求
  if (resizeRequestId) {
    cancelAnimationFrame(resizeRequestId);
    resizeRequestId = null;
  }
  
  // 更新标题位置
  updateTitlePosition();
};

// 暴露开始调整函数
const startLeftResize = (e) => initResize(e, 'left');
const startRightResize = (e) => initResize(e, 'right');

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