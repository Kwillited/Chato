<template>
  <div id="displayArea" class="flex-1 flex p-0 pl-0 pr-0 pt-0 bg-light dark:bg-dark-primary overflow-hidden" :class="{ 'transition-all duration-300': !isInitialLoading }">
    <!-- 2. 历史对话/设置选项面板 -->
    <div 
      id="panelContainer" 
      class="h-full flex-shrink-0 z-40 overflow-hidden transition-all duration-300" 
      :style="{
        width: settingsStore.leftNavVisible ? settingsStore.leftNavWidth : '0px',
        minWidth: settingsStore.leftNavVisible ? '200px' : '0px',
        maxWidth: settingsStore.leftNavVisible ? '370px' : '0px',
        flexShrink: 0
      }"
    >
      <!-- 面板内容 - 使用复合组件简化逻辑 -->
      <PanelContent :active-panel="settingsStore.activePanel" />
    </div>

    <!-- 面板与主内容区之间的分隔线 -->
    <div 
      id="LeftResizer" 
      class="resizer transition-all duration-300" 
      :class="{
        'resizer-disabled': !settingsStore.leftNavVisible
      }"
      @mousedown="startLeftResize"
    ></div>

    <!-- 3. 主内容区域 -->
    <div id="mainContent" class="flex-1 flex flex-col overflow-hidden bg-[#F8FAFC] dark:bg-dark-primary" :class="{ 'transition-all duration-300': !isInitialLoading }">
      <!-- 根据activeContent动态切换内容组件 -->
      <ChatContent v-if="activeContent === 'chat'" />
      <SettingsContent v-if="activeContent === 'settings'" />
      <RagManagementContent v-if="activeContent === 'ragManagement'" />
      <ContextVisualizationContent v-if="activeContent === 'contextVisualization'" />
      <SendMessageContent v-if="activeContent === 'sendMessage'" />
      <AISettingsContent v-if="activeContent === 'aiSettings'" />

    </div>

    <!-- 新增的分隔div -->
    <div 
      id="RightResizer" 
      class="resizer transition-all duration-300"
      :class="{
        'resizer-disabled': !settingsStore.rightPanelVisible
      }"
      @mousedown="startRightResize"
    ></div>

    <!-- 右侧工具内容区域 -->
    <RightPanel :saved-width="savedRightPanelWidth" :is-initial-loading="isInitialLoading" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import PanelContent from '../panel/PanelContent.vue'; // 使用PanelContent复合组件
import ChatContent from '../../views/ChatContent.vue'; // 移动到views目录
import SettingsContent from '../../views/SettingsContent.vue'; // 移动到views目录
import RagManagementContent from '../../views/RagManagementContent.vue'; // 移动到views目录
import { ContextVisualizationContent } from '../library';
import SendMessageContent from '../../views/SendMessageContent.vue'; // 新增发送消息视图组件
import AISettingsContent from '../../views/AISettingsContent.vue'; // 新增AI配置视图组件

import RightPanel from '../panel/RightPanel.vue';
import { useSettingsStore } from '../../store/settingsStore.js';

// 定义props
const props = defineProps({
  activeContent: {
    type: String,
    default: 'sendMessage' // 默认值改为sendMessage，避免空白chatMainContent
  },
  savedRightPanelWidth: {
    type: String,
    default: '256px'
  },
  isInitialLoading: {
    type: Boolean,
    default: true
  }
});

// 初始化store
const settingsStore = useSettingsStore();

// 调整状态
const isResizing = ref(false);
let startX = 0;
let startWidth = 0;
let resizeType = '';
let resizeRequestId = null;

// 实现面板大小调整功能
const initResize = (e, type) => {
  // 如果面板不可见，不允许调整大小
  if ((type === 'right' && !settingsStore.rightPanelVisible) || 
      (type === 'left' && !settingsStore.leftNavVisible)) {
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
    const displayArea = document.getElementById('displayArea');
    
    if (!leftPanel || !rightPanel || !displayArea) return;
    
    // 计算宽度变化，右侧面板调整方向相反
    const isRightPanel = resizeType === 'right';
    const widthChange = isRightPanel ? (startX - e.clientX) : (e.clientX - startX);
    let newWidth = startWidth + widthChange;
    
    // 设置最小和最大宽度限制
    const minWidth = 200; // 最小宽度为200px
    const panelMaxWidth = 370; // 所有面板的最大宽度为370px
    const mainContentMinWidth = 300; // 主内容区最小宽度
    
    // 获取当前所有面板的宽度
    const leftPanelWidth = settingsStore.leftNavVisible ? leftPanel.offsetWidth : 0;
    const rightPanelWidth = settingsStore.rightPanelVisible ? rightPanel.offsetWidth : 0;
    
    // 计算可用总宽度
    const availableWidth = displayArea.offsetWidth;
    
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
      settingsStore.setRightNavWidth(`${newWidth}px`);
    } else {
      settingsStore.setLeftNavWidth(`${newWidth}px`);
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
};

// 暴露开始调整函数
const startLeftResize = (e) => initResize(e, 'left');
const startRightResize = (e) => initResize(e, 'right');

// 组件挂载时初始化
onMounted(() => {
  // 初始化右侧面板宽度
  const rightPanel = document.getElementById('rightPanel');
  if (rightPanel && settingsStore.rightPanelVisible) {
    rightPanel.style.width = props.savedRightPanelWidth;
  }
});

// 组件卸载时清理
onUnmounted(() => {
  // 确保移除所有事件监听器
  document.removeEventListener('mousemove', resizePanel);
  document.removeEventListener('mouseup', stopResize);
  document.removeEventListener('mouseleave', stopResize);
});
</script>