<template>
  <div 
    class="app-container h-screen flex flex-col overflow-hidden bg-light text-dark dark:bg-dark-primary dark:text-light"
    :class="{ 'transition-all duration-300': !isInitialLoading }"
  >
    <!-- 整合后的顶部导航和面板容器 -->
    <div class="flex flex-col flex-1 overflow-hidden">
      <!-- 1. 顶部导航栏 -->
      <TopNav data-tauri-drag-region/>

      <!-- 主内容区域：包含左右面板和显示区域 -->
      <div class="flex flex-1 overflow-hidden">
        <!-- 左侧面板 -->
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

        <!-- 左侧面板与主内容区之间的分隔线 -->
        <div 
          id="LeftResizer" 
          class="resizer transition-all duration-300" 
          :class="{
            'resizer-disabled': !settingsStore.leftNavVisible
          }"
          @mousedown="startLeftResize"
        ></div>

        <!-- 3. 显示区域容器 -->
        <DisplayArea 
          :active-content="settingsStore.activeContent" 
          :saved-right-panel-width="settingsStore.rightPanelWidth" 
          :is-initial-loading="isInitialLoading"
        />

        <!-- 右侧面板与主内容区之间的分隔线 -->
        <div 
          id="RightResizer" 
          class="resizer transition-all duration-300"
          :class="{
            'resizer-disabled': !settingsStore.rightPanelVisible
          }"
          @mousedown="startRightResize"
        ></div>

        <!-- 右侧面板 -->
        <RightPanel :saved-width="settingsStore.rightPanelWidth" :is-initial-loading="isInitialLoading" />
      </div>
    </div>

    <!-- 模型版本表单（支持添加和编辑） -->
    <ModelVersionForm />

    <!-- 模型配置抽屉 -->
    <ModelSettingsDrawer />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import TopNav from './components/layout/TopNav.vue';
import ModelVersionForm from './components/models/ModelVersionForm.vue';
import ModelSettingsDrawer from './components/models/ModelSettingsDrawer.vue';
import DisplayArea from './components/layout/DisplayArea.vue';
import PanelContent from './components/panel/PanelContent.vue';
import RightPanel from './components/panel/RightPanel.vue';
import { useChatStore } from './store/chatStore.js';
import { useSettingsStore } from './store/settingsStore.js';
import { useModelSettingStore } from './store/modelSettingStore.js';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();
const modelSettingStore = useModelSettingStore();

// 初始加载状态，用于控制首次加载时的动画
const isInitialLoading = ref(true);

// 调整状态
const isResizing = ref(false);
let startX = 0;
let startWidth = 0;
let resizeType = '';
let resizeRequestId = null;

// 监听activePanel变化，同步更新activeContent
watch(
  () => settingsStore.activePanel,
  (newPanel) => {
    // 当切换到任何面板时，自动展开左侧面板
    settingsStore.leftNavVisible = true;
    
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

import { apiService } from './services/apiService.js';

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
      await modelSettingStore.loadModels();
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
  if (!settingsStore.activePanel) {
    settingsStore.setActivePanel('history');
  }

  console.log('AIClient应用已初始化，使用Pinia状态管理');
  
  // 初始化完成，启用动画
  isInitialLoading.value = false;
});

// 组件卸载时清理
onUnmounted(() => {
  // 确保移除所有事件监听器
  document.removeEventListener('mousemove', resizePanel);
  document.removeEventListener('mouseup', stopResize);
  document.removeEventListener('mouseleave', stopResize);
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
</style>
