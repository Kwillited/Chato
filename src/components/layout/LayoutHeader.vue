<template>
  <div class="panel-header p-3 flex items-center justify-between transition-all duration-300 relative z-50">
    <!-- 左侧：隐藏左侧面板按钮和新增会话按钮 -->
    <div class="flex space-x-2">
      <!-- 隐藏左侧面板按钮和新增会话按钮 - 只在非设置页面显示 -->
      <template v-if="activeContent !== 'settings'">
        <!-- 隐藏左侧面板按钮 -->
        <Tooltip content="隐藏左侧面板">
          <Button 
            shape="full"
            size="md"
            icon="bars"
            @click="handleSideMenuToggle"
          />
        </Tooltip>
        <!-- 新增会话按钮 -->
        <Tooltip content="新对话">
          <Button 
            id="newChat"
            shape="full"
            size="md"
            icon="comment-dots"
            @click="handleNewChat"
          />
        </Tooltip>
      </template>
      <!-- 设置面板：返回按钮和系统设置标题 -->
      <div v-else class="flex items-center space-x-2">
        <!-- 返回按钮 -->
        <Tooltip content="返回上一级">
          <button
            class="flex items-center ml-4 pr-3 py-1.5 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-300 rounded-full"
            @click="handleBack"
          >
            <i class="fa-solid fa-chevron-left text-black dark:text-white transition-colors duration-300"></i>
            <span class="text-lg font-bold transition-all duration-300">系统设置</span>
          </button>
        </Tooltip>
      </div>
    </div>
    
    <!-- 中间：标题容器 -->
      <div v-if="activeContent === 'chat'" ref="titleContainer" class="flex-1 flex justify-center items-center">
        <h2 class="text-lg font-bold text-gray-800 dark:text-white">{{ getChatTitle() }}</h2>
      </div>
      <div v-else ref="titleContainer" class="flex-1 flex justify-center items-center">
        <!-- 非聊天页面不显示标题 -->
      </div>
    
    <!-- 右侧：历史对话按钮 -->
    <div class="flex space-x-2">
      <!-- 视图切换按钮 -->
      <div v-if="activeContent === 'chat'" class="relative flex items-center justify-center">
        <Tooltip :content="`切换到${uiStore.activeView === 'chat' ? '上下文工程可视化' : '对话'}视图`">
          <Button 
            shape="full"
            size="md"
            :icon="uiStore.activeView === 'chat' ? 'sitemap' : 'comments'"
            @click="toggleView"
          />
        </Tooltip>
      </div>
      <!-- 历史对话按钮（带下拉菜单） - 只在非设置页面显示 -->
      <div v-if="activeContent !== 'settings'" class="relative hover-scale">
        <Tooltip content="历史对话">
          <Button 
            id="historyChat"
            shape="full"
            size="md"
            icon="clock-rotate-left"
            @click.stop="toggleHistoryMenu"
          />
        </Tooltip>
        
        <!-- 历史对话下拉菜单 -->
        <div 
          v-if="showHistoryMenu"
          ref="historyMenuRef"
          class="absolute top-full mt-2 right-0 w-64 rounded-lg shadow-lg border z-9999 dropdown-content flex flex-col py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700 max-h-96 overflow-y-auto"
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
      
      <!-- 设置页面选项卡 - 只在设置页面显示 -->
      <div v-if="activeContent === 'settings'" class="items-center w-80">
        <TabSwitcher
          :tabs="[
            { id: 'general', name: '基本设置' },
            { id: 'models', name: '模型配置' },
            { id: 'rag', name: '知识库配置' },
            { id: 'about', name: '关于' }
          ]"
          :active-tab="uiStore.activeSection"
          container-class="items-center w-full"
          @tab-change="handleSettingsTabClick"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useNavigation } from '../../composables/useNavigation.js';
import { useUiStore } from '../../store/uiStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { Button } from '../library/index.js';
import { formatDate } from '../../utils/time.js';
import TabSwitcher from '../common/TabSwitcher.vue';

// Props
const props = defineProps({
  activeContent: {
    type: String,
    default: 'home'
  }
});

// Stores
const uiStore = useUiStore();
const chatStore = useChatStore();

// 路由
const router = useRouter();

// 导航方法
const { navigateToHome, navigateToChat } = useNavigation();

// State
const showHistoryMenu = ref(false);
const titleContainer = ref(null);
const historyMenuRef = ref(null);

// 处理点击外部关闭历史菜单
const handleClickOutside = (event) => {
  if (historyMenuRef.value && !historyMenuRef.value.contains(event.target) && 
      !event.target.closest('#historyChat') && showHistoryMenu.value) {
    showHistoryMenu.value = false;
  }
};

// 获取当前对话标题
const getChatTitle = () => {
  if (props.activeContent === 'chat' && chatStore.currentChat) {
    return chatStore.currentChat.title || '未命名对话';
  }
  if (props.activeContent === 'sendMessage' || props.activeContent === 'home') {
    return '新对话';
  }
  if (props.activeContent === 'settings') {
    return getSettingsTitle();
  }
  if (props.activeContent === 'fileManager') {
    return '文件管理';
  }
  if (props.activeContent === 'contextVisualization') {
    return '上下文可视化';
  }

  return '对话';
};

// 获取设置页面标题
const getSettingsTitle = () => {
  const activeSection = uiStore.activeSection || 'general';
  const sectionTitles = {
    general: '基本设置',
    models: '模型配置',
    notifications: '通知设置',
    about: '关于页面',
    rag: '知识库配置',

  };
  return sectionTitles[activeSection] || '设置';
};

// Methods
const handleSideMenuToggle = () => {
  uiStore.toggleLeftNav();
};

const handleNewChat = () => {
  chatStore.currentChatId = null;
  chatStore.resetUnreadStatus();
  // 跳转到根目录路由
  navigateToHome();
};

const handleBack = () => {
  // 如果当前是设置面板，使用 uiStore 的方法返回
  if (uiStore.activePanel === 'settings') {
    uiStore.navigateFromSettings();
  }
  // 返回上一级路由
  router.back();
};

const toggleHistoryMenu = () => {
  showHistoryMenu.value = !showHistoryMenu.value;
};

const selectChatFromHistory = (chatId) => {
  showHistoryMenu.value = false;
  chatStore.selectChat(chatId);
  // 添加路由跳转逻辑
  navigateToChat(chatId);
};

// 切换视图模式
const toggleView = () => {
  uiStore.setActiveView(uiStore.activeView === 'chat' ? 'Graph' : 'chat');
};

// 处理设置选项卡点击事件
const handleSettingsTabClick = (section) => {
  uiStore.setActiveSection(section);
};



// 生命周期钩子
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// Expose
defineExpose({
  titleContainer
});
</script>

<style scoped>
/* 下拉菜单动画 */
.dropdown-content {
  animation: fadeInDown 0.2s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>