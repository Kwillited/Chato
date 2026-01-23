<template>
  <div 
    id="displayArea" 
    class="flex-1 flex overflow-hidden mt-[72px] h-[calc(100vh-72px)] bg-light dark:bg-dark-primary relative"
    :class="{ 'opacity-0': isInitialLoading, 'opacity-100': !isInitialLoading }"
  >
    <!-- 全局遮罩：仅在拖拽时显示，防止鼠标事件被 iframe 或子组件捕获 -->
    <div 
      v-if="isResizing" 
      class="absolute inset-0 z-[9999] cursor-col-resize"
    ></div>

    <!-- 1. 左侧面板容器 -->
    <aside
      v-show="settingsStore.leftNavVisible"
      class="h-full flex-shrink-0 z-40 overflow-hidden border-r dark:border-dark-700 relative"
      :class="{ 'transition-width duration-300 ease-in-out': !isResizing }"
      :style="{ width: settingsStore.leftNavWidth }"
    >
      <PanelContent :active-panel="settingsStore.activePanel" />
    </aside>

    <!-- 左侧调整手柄 -->
    <div 
      v-show="settingsStore.leftNavVisible"
      class="w-1 hover:w-1.5 -mr-1 z-50 cursor-col-resize hover:bg-blue-500 active:bg-blue-600 transition-all flex-shrink-0 opacity-0 hover:opacity-100 active:opacity-100"
      :class="{ '!opacity-100 !bg-blue-600': isResizing && resizeTarget === 'left' }"
      @mousedown.prevent="startResize($event, 'left')"
    ></div>

    <!-- 2. 主内容区域 -->
    <main 
      id="mainContent" 
      class="flex-1 flex flex-col overflow-hidden relative min-w-[300px]"
    >
      <component :is="currentContentComponent" />
    </main>

    <!-- 右侧调整手柄 -->
    <div 
      v-show="settingsStore.rightPanelVisible"
      class="w-1 hover:w-1.5 -ml-1 z-50 cursor-col-resize hover:bg-blue-500 active:bg-blue-600 transition-all flex-shrink-0 opacity-0 hover:opacity-100 active:opacity-100"
      :class="{ '!opacity-100 !bg-blue-600': isResizing && resizeTarget === 'right' }"
      @mousedown.prevent="startResize($event, 'right')"
    ></div>

    <!-- 3. 右侧面板容器 (修复：使用 div 包裹组件来控制宽度) -->
    <aside
      v-show="settingsStore.rightPanelVisible"
      class="h-full flex-shrink-0 z-40 overflow-hidden border-l dark:border-dark-700 relative"
      :class="{ 'transition-width duration-300 ease-in-out': !isResizing }"
      :style="{ width: settingsStore.rightPanelWidth }"
    >
      <RightPanel 
        class="w-full h-full"
        :is-initial-loading="isInitialLoading" 
      />
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, inject } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';

// 组件导入
import PanelContent from '../panel/PanelContent.vue';
import RightPanel from '../panel/RightPanel.vue';
import ChatContent from '../../views/ChatContent.vue';
import RagManagementContent from '../../views/RagManagementContent.vue';
import SendMessageContent from '../../views/SendMessageContent.vue';
import AISettingsContent from '../../views/AISettingsContent.vue';
import { ContextVisualizationContent } from '../library';

// Props
const props = defineProps({
  activeContent: { type: String, default: 'sendMessage' },
  isInitialLoading: { type: Boolean, default: true }
});

// Stores & Utils
const settingsStore = useSettingsStore();
// 假设你通过 provide/inject 注入了 mitt 实例，或者直接 import emitter from '@/utils/emitter'
const emitter = inject('emitter'); 

// 动态组件映射
const componentMap = {
  chat: ChatContent,
  settings: AISettingsContent,
  aiSettings: AISettingsContent,
  ragManagement: RagManagementContent,
  contextVisualization: ContextVisualizationContent,
  sendMessage: SendMessageContent
};

const currentContentComponent = computed(() => componentMap[props.activeContent] || SendMessageContent);

// --- 拖拽调整大小逻辑 ---

const isResizing = ref(false);
const resizeTarget = ref(''); // 'left' | 'right'
let startX = 0;
let startWidth = 0;
let animationFrameId = null;

/**
 * 开始调整大小
 * @param {MouseEvent} e 
 * @param {'left'|'right'} target 
 */
const startResize = (e, target) => {
  isResizing.value = true;
  resizeTarget.value = target;
  startX = e.clientX;
  
  // 从 Store 获取当前宽度数值 (去除 px)
  const currentWidthStr = target === 'left' 
    ? settingsStore.leftNavWidth 
    : settingsStore.rightPanelWidth;
  startWidth = parseInt(currentWidthStr, 10) || 260; // 默认值防守

  // 绑定全局事件
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', stopResize);
  
  // 设置全局光标
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
};

/**
 * 处理鼠标移动 (使用 requestAnimationFrame 节流)
 */
const handleMouseMove = (e) => {
  if (!isResizing.value) return;

  if (animationFrameId) cancelAnimationFrame(animationFrameId);

  animationFrameId = requestAnimationFrame(() => {
    const isLeft = resizeTarget.value === 'left';
    // 左侧：向右拖动增加宽度；右侧：向左拖动增加宽度
    const offset = e.clientX - startX;
    const newWidth = isLeft ? (startWidth + offset) : (startWidth - offset);

    // 边界限制 (min: 200, max: 500 或 屏幕宽度的 40%)
    const minWidth = 200;
    const maxWidth = Math.min(500, window.innerWidth * 0.4);
    
    const clampedWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
    const widthPx = `${clampedWidth}px`;

    // 更新 Store
    if (isLeft) {
      settingsStore.setLeftNavWidth(widthPx);
    } else {
      settingsStore.setRightNavWidth(widthPx);
    }
  });
};

/**
 * 停止拖拽
 */
const stopResize = () => {
  isResizing.value = false;
  resizeTarget.value = '';
  
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', stopResize);
  
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = null;
  }

  // Mitt: 通知其他组件布局已改变 (例如 ECharts 需要 resize)
  if (emitter) {
    emitter.emit('layout:resize');
  }
};

// 清理事件防止内存泄漏
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', stopResize);
});
</script>

<style scoped>
/* 定义一个工具类来控制 width 的过渡 */
.transition-width {
  transition-property: width, min-width, max-width;
}
</style>