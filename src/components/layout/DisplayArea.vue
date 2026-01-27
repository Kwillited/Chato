<template>
  <div id="displayArea" class="flex-1 flex p-0 pl-0 pr-0 pt-0 mt-8 bg-light dark:bg-dark-primary h-[calc(100vh-2rem)] overflow-hidden" :class="{ 'transition-all duration-300': !isInitialLoading }">
    <!-- 2. 历史对话/设置选项面板 -->
    <div 
      id="panelContainer" 
      class="h-full flex-shrink-0 z-40 overflow-hidden transition-all duration-300" 
      :style="{
        width: uiStore.leftNavVisible ? uiStore.leftNavWidth : 'auto',
        minWidth: uiStore.leftNavVisible ? '200px' : 'auto',
        maxWidth: uiStore.leftNavVisible ? '370px' : 'auto',
        flexShrink: 0
      }"
    >
      <!-- 左侧面板header -->
      <div class="panel-header p-3 flex justify-between items-center transition-all duration-300">
        <!-- 历史面板：显示隐藏按钮和新增会话按钮 -->
        <div v-if="uiStore.activePanel !== 'settings'" class="flex space-x-2">
          <!-- 隐藏左侧面板按钮 -->
          <Button 
            shape="full"
            size="md"
            icon="fa-bars"
            tooltip="隐藏左侧面板"
            @click="handleSideMenuToggle"
          />
          <!-- 新增会话按钮 -->
          <Button 
            id="newChat"
            shape="full"
            size="md"
            icon="fa-comment-dots"
            tooltip="新对话"
            @click="handleNewChat"
          />
        </div>
        <!-- 设置面板：显示返回按钮和系统设置标题 -->
        <div v-else class="flex items-center space-x-1">
          <!-- 返回按钮 -->
          <Button 
            shape="full"
            size="md"
            icon="fa-chevron-left"
            tooltip="返回聊天"
            @click="handleBackToChat"
            class="pr-0"
          />
          <!-- 系统设置标题 -->
          <h2 class="text-lg font-bold text-dark dark:text-white">系统设置</h2>
        </div>
      </div>
      <!-- 面板内容 - 使用复合组件简化逻辑 -->
      <div v-if="uiStore.leftNavVisible" class="transition-all duration-300">
        <PanelContent :active-panel="uiStore.activePanel" />
      </div>
    </div>

    <!-- 面板与主内容区之间的分隔线 -->
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

    <!-- 3. 主内容区域 -->
    <div id="mainContent" class="flex-1 flex flex-col overflow-hidden bg-[#F8FAFC] dark:bg-dark-primary" :class="{ 'transition-all duration-300': !isInitialLoading }">
      <!-- 主内容区header -->
      <div class="panel-header p-3 flex flex-wrap items-center justify-end gap-4 relative transition-all duration-300 border-b-0">

        <!-- 标题绝对居中 - 只在chat内容时显示 -->
        <div v-if="props.activeContent === 'chat'" class="absolute left-1/2 transform -translate-x-1/2 flex items-center">
          <h2 class="text-lg font-bold text-gray-800 dark:text-white">{{ getChatTitle() }}</h2>
        </div>

      </div>
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
        'resizer-disabled': !uiStore.rightPanelVisible
      }"
      @mousedown="startRightResize"
    ></div>

    <!-- 右侧工具内容区域 -->
    <div 
      class="h-full flex-shrink-0 z-40 overflow-hidden mr-0 max-w-[370px]"
      :class="{ 'transition-all duration-300': !isInitialLoading }"
      :style="{
        width: uiStore.rightPanelVisible ? uiStore.rightPanelWidth : 'auto',
        minWidth: uiStore.rightPanelVisible ? '200px' : 'auto',
        maxWidth: uiStore.rightPanelVisible ? '370px' : 'auto',
        flexShrink: 0
      }"
    >
      <!-- 右侧面板header -->
      <div class="panel-header p-3 flex justify-end items-center">
        <!-- 历史对话按钮（带下拉菜单） - 只在非设置页面显示 -->
        <div v-if="props.activeContent !== 'settings'" class="relative hover-scale">
          <Button 
            id="historyChat"
            shape="full"
            size="md"
            icon="fa-clock-rotate-left"
            tooltip="历史对话"
            @click.stop="toggleHistoryMenu"
          />
          
          <!-- 历史对话下拉菜单 -->
          <div 
            v-if="showHistoryMenu"
            class="absolute top-full mt-2 right-0 w-64 rounded-lg shadow-lg border z-50 dropdown-content flex flex-col py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700 max-h-96 overflow-y-auto"
          >
            <!-- 下拉菜单标题 -->
            <div class="px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-dark-700">
              历史对话
            </div>
            
            <!-- 历史对话列表 -->
            <div v-if="chatStore.chats.length > 0" class="py-2">
              <button 
                v-for="chat in chatStore.chatHistory" 
                :key="chat.id"
                class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-dark-700 text-gray-700 dark:text-gray-300 transition-colors duration-200 flex items-start gap-2"
                @click="selectChatFromHistory(chat.id)"
              >
                <i class="fa-solid fa-comments text-xs mt-1 flex-shrink-0 text-gray-400 dark:text-gray-500"></i>
                <div class="flex-1 min-w-0 flex items-center justify-between">
                    <div class="font-medium truncate">{{ chat.title }}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400 truncate ml-2 whitespace-nowrap">
                      {{ formatDate(chat.updatedAt) }}
                    </div>
                  </div>
              </button>
            </div>
            
            <!-- 空状态 -->
            <div v-else class="px-4 py-4 text-center text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-2">
              <i class="fa-solid fa-inbox text-xl"></i>
              暂无历史对话
            </div>
          </div>
        </div>
      </div>
      <!-- 右侧面板内容 -->
      <RightPanel 
        :saved-width="savedRightPanelWidth" 
        :is-initial-loading="isInitialLoading"
        v-if="uiStore.rightPanelVisible"
      />
    </div>
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
import { useUiStore } from '../../store/uiStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { Button } from '../library/index.js';
import { showNotification } from '../../utils/notificationUtils.js';
import { formatDate } from '../../utils/time.js';

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

// 初始化stores
const settingsStore = useSettingsStore();
const uiStore = useUiStore();
const chatStore = useChatStore();

// 历史对话菜单状态
const showHistoryMenu = ref(false);

// 处理侧边菜单切换
const handleSideMenuToggle = () => {
  // 使用store方法切换左侧面板可见性
  uiStore.toggleLeftNav();
};

// 处理新对话点击事件
const handleNewChat = () => {
  // 取消当前会话的激活状态
  chatStore.currentChatId = null;
  
  // 清除所有对话的未读标记
  chatStore.resetUnreadStatus();
  
  // 切换到发送消息视图
  uiStore.setActiveContent('sendMessage');
};

// 切换历史对话下拉菜单显示状态
const toggleHistoryMenu = () => {
  showHistoryMenu.value = !showHistoryMenu.value;
};

// 从历史对话下拉菜单中选择对话
const selectChatFromHistory = (chatId) => {
  // 关闭下拉菜单
  showHistoryMenu.value = false;
  
  // 选择对话
  chatStore.selectChat(chatId);
  
  // 切换到聊天视图
  uiStore.setActiveContent('chat');
};

// 获取设置页面标题
const getSettingsTitle = () => {
  const activeSection = settingsStore.activeSection || 'general';
  const sectionTitles = {
    general: '基本设置',
    models: '模型配置',
    notifications: '通知设置',
    about: '关于页面',
    rag: '知识库配置',
    mcp: 'MCP服务设置',
  };
  return sectionTitles[activeSection] || '设置';
};

// 获取当前对话标题
const getChatTitle = () => {
  if (props.activeContent === 'chat' && chatStore.currentChat) {
    return chatStore.currentChat.title || '未命名对话';
  }
  if (props.activeContent === 'sendMessage') {
    return '新对话';
  }
  if (props.activeContent === 'settings') {
    return getSettingsTitle();
  }
  if (props.activeContent === 'ragManagement') {
    return '知识库管理';
  }
  if (props.activeContent === 'contextVisualization') {
    return '上下文可视化';
  }
  if (props.activeContent === 'aiSettings') {
    return 'AI配置';
  }
  return '对话';
};

// 处理从设置面板返回聊天
const handleBackToChat = () => {
  uiStore.setActivePanel('history');
  uiStore.setActiveContent('chat');
};

// 处理导出所有对话
const handleExportAll = () => {
  console.log('导出所有对话');
  try {
    // 将对话历史转换为JSON字符串
    const chatData = JSON.stringify(chatStore.chats, null, 2);

    // 创建Blob对象和下载链接
    const blob = new Blob([chatData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_history_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('对话历史导出成功');
  } catch (error) {
    console.error('导出对话历史失败:', error);
    showNotification('导出失败，请重试。', 'error');
  }
};

// 处理删除所有对话
const handleDeleteAll = () => {
  // 这里可以添加删除确认逻辑
  if (confirm('确定要删除所有对话吗？这将删除所有历史对话，无法恢复！')) {
    chatStore.clearAllChats();
    showNotification('所有对话已删除', 'success');
    uiStore.setActiveContent('sendMessage');
  }
};

// 点击外部区域关闭菜单
const closeMenusOnClickOutside = (event) => {
  const menuButtons = document.querySelectorAll('.relative.hover-scale');
  
  let clickedInsideMenu = false;
  menuButtons.forEach(button => {
    if (button.contains(event.target)) {
      clickedInsideMenu = true;
    }
  });
  
  if (!clickedInsideMenu) {
    showHistoryMenu.value = false;
  }
};

// 调整状态
const isResizing = ref(false);
let startX = 0;
let startWidth = 0;
let resizeType = '';
let resizeRequestId = null;

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
    const leftPanelWidth = uiStore.leftNavVisible ? leftPanel.offsetWidth : 0;
    const rightPanelWidth = uiStore.rightPanelVisible ? rightPanel.offsetWidth : 0;
    
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
  if (rightPanel && uiStore.rightPanelVisible) {
    rightPanel.style.width = props.savedRightPanelWidth;
  }
  
  // 添加点击外部事件监听
  document.addEventListener('click', closeMenusOnClickOutside);
});

// 组件卸载时清理
onUnmounted(() => {
  // 确保移除所有事件监听器
  document.removeEventListener('mousemove', resizePanel);
  document.removeEventListener('mouseup', stopResize);
  document.removeEventListener('mouseleave', stopResize);
  document.removeEventListener('click', closeMenusOnClickOutside);
});
</script>