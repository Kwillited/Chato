<template>
  
  <!-- 聊天输入区域 - 在切换到图谱视图时添加顶部padding -->
  <div id="UserInputBox" class="border-t-0 pb-4 px-6 transition-colors duration-300 ease-in-out" :class="{ 'pt-4': activeView !== 'grid' }">
    <div class="relative w-full max-w-4xl mx-auto">
      <DragDropZone @drop="handleDrop">
        <div class="bg-white dark:bg-dark-700 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md focus-within:shadow-md transition-all duration-300 ease-in-out relative">
        <!-- 智能体选择和MCP工具 - 合并到卡片内部 -->
        <div class="px-3 py-1.5 border-b border-gray-200 flex items-center gap-2">
          <div class="flex items-center gap-2">
            <!-- 智能体选择 -->
            <div class="relative inline-block">
              <Tooltip content="选择智能体">
                <button
                  class="h-6 flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-dark-700 px-3 rounded-lg transition-all duration-300 ease-in-out hover:bg-gray-100 dark:hover:bg-dark-600 hover:text-primary cursor-pointer btn-secondary"
                  @click="toggleAgentDropdown"
                >

                  <span>{{ currentAgentDisplayName }}</span>
                  <i class="fa-solid fa-chevron-down text-xs text-neutral"></i>
                </button>
              </Tooltip>
              <div
                ref="agentDropdown"
                class="absolute left-0 bottom-full mb-1 w-48 bg-white dark:bg-dark-700 z-50 rounded-lg border border-gray-200 dark:border-gray-700 shadow-md"
                :class="{ 'hidden': !showAgentDropdown }"
                style="z-index: 1000 !important"
              >
                <div class="py-1">
                  <button
                    v-for="agent in availableAgents"
                    :key="agent.value"
                    class="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors rounded-lg"
                  :class="{ 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/30': agent.value === currentAgent }"
                    @click="selectAgent(agent.value)"
                  >
                    <i :class="['fa-solid', agent.icon, 'mr-2 text-sm']"></i>
                    {{ agent.displayName }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- MCP工具按钮 -->
            <Tooltip content="MCP工具">
              <button
                class="h-6 w-6 flex items-center justify-center transition-colors hover:bg-gray-100 text-gray-500 dark:hover:bg-dark-700 dark:text-gray-300 rounded-full"
                @click="handleMcpService"
              >
                <i class="fa-solid fa-gear text-xs"></i>
              </button>
            </Tooltip>
          </div>
          
          <!-- 展开/折叠控制按钮 + 顶部导航栏迁移按钮 -->
          <div class="flex-1 flex justify-end items-center gap-2">
            <button
              class="h-6 w-6 flex items-center justify-center text-sm text-gray-600 dark:text-gray-300 hover:text-primary transition-all duration-300 ease-in-out"
              @click="toggleParamsPanel"
              :class="{ 'rotate-180': showParamsPanel }"
            >
              <i class="fa-solid fa-chevron-down text-xs"></i>
            </button>
            
            <!-- 迁移自顶部导航栏的功能按钮 -->
            <div class="h-4 w-px bg-gray-200 dark:bg-dark-700"></div>
            <Tooltip content="切换侧边栏">
              <button
                class="h-6 w-6 flex items-center justify-center text-sm text-gray-600 dark:text-gray-300 hover:text-primary transition-all duration-300 ease-in-out"
                @click="toggleViewPanel"
              >
                <i class="fa-solid fa-columns text-xs"></i>
              </button>
            </Tooltip>
            <Tooltip :content="settingsStore.systemSettings.darkMode ? '切换到亮色模式' : '切换到暗色模式'">
              <button
                class="h-6 w-6 flex items-center justify-center text-sm text-gray-600 dark:text-gray-300 hover:text-primary transition-all duration-300 ease-in-out"
                @click="handleToggleTheme"
              >
                <i :class="['fa-solid', settingsStore.systemSettings.darkMode ? 'fa-sun' : 'fa-moon', 'text-xs']"></i>
              </button>
            </Tooltip>
            <Tooltip content="系统设置">
              <button
                class="h-6 w-6 flex items-center justify-center text-sm text-gray-600 dark:text-gray-300 hover:text-primary transition-all duration-300 ease-in-out"
                @click="handleSystemSettingsClick"
              >
                <i class="fa-solid fa-gear text-xs"></i>
              </button>
            </Tooltip>
            
            <div ref="userMenuContainer" class="relative">
              <Tooltip content="用户菜单">
                <button
                  class="h-6 w-6 flex items-center justify-center text-sm text-gray-600 dark:text-gray-300 hover:text-primary transition-all duration-300 ease-in-out"
                  @click="toggleUserMenu"
                >
                  <i class="fa-solid fa-user-circle text-sm"></i>
                </button>
              </Tooltip>
              <div v-if="showUserMenu" class="absolute top-full mt-2 right-0 w-14 rounded-lg shadow-lg border z-50 dropdown-menu flex flex-col items-center py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700">
                <Tooltip content="切换账户">
                  <button
                    class="h-6 w-6 flex items-center justify-center text-sm text-gray-600 dark:text-gray-300 hover:text-primary transition-all duration-300 ease-in-out"
                    @click="handleSwitchAccount"
                  >
                    <i class="fa-solid fa-exchange text-xs"></i>
                  </button>
                </Tooltip>
                <div class="my-1 w-8 border-t border-gray-200 dark:border-dark-700"></div>
                <Tooltip content="退出账号">
                  <button
                    class="h-6 w-6 flex items-center justify-center text-sm text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-300 ease-in-out"
                    @click="handleLogout"
                  >
                    <i class="fa-solid fa-arrow-right-from-bracket text-xs"></i>
                  </button>
                </Tooltip>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 可上滑展开的参数设置区域 -->
        <transition name="slide-up">
          <div v-if="showParamsPanel" class="border-b border-gray-200 overflow-hidden transition-all duration-300 ease-in-out">
            <div class="px-3 py-3 grid grid-cols-4 gap-3">
              <!-- 温度参数设置 -->
              <div class="px-2">
                <div class="flex justify-between items-center mb-1">
                  <div class="flex items-center gap-1">
                    <label class="text-xs font-medium text-gray-700 dark:text-gray-300">温度</label>
                    <button
                      class="text-xs text-neutral dark:text-gray-400 cursor-help p-1 relative"
                      @mouseover="showTooltip('temperature', $event)"
                      @mouseleave="hideTooltip('temperature')"
                    >
                      <i class="fa-solid fa-circle-question"></i>
                    </button>
                    <!-- 悬停提示弹窗 -->
                    <div
                      v-if="activeTooltip === 'temperature'"
                      class="absolute z-50 bg-white dark:bg-dark-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm max-w-xs transition-opacity duration-200"
                      :style="tooltipStyle"
                    >
                      <div class="font-medium mb-1 dark:text-white">温度参数说明</div>
                      <p class="text-gray-700 dark:text-gray-300">控制生成结果的随机性，较低的值产生更确定的结果，较高的值产生更多样的结果。</p>
                      <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">范围: 0-2</div>
                    </div>
                  </div>
                  <span
                    class="text-xs font-medium text-blue-500 dark:text-blue-400 px-2 py-0.5 bg-blue-500/10 dark:bg-blue-400/10 rounded-full"
                    id="temperatureValue"
                  >{{ modelParams.temperature }}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  :value="modelParams.temperature"
                  class="slider w-full"
                  id="temperatureSlider"
                  @input="handleTemperatureChange"
                />
                <div class="flex justify-between text-xs text-neutral dark:text-gray-400 mt-1">
                  <span>0</span>
                  <span>2</span>
                </div>
              </div>

              <!-- Top-p参数设置 -->
              <div class="px-2">
                <div class="flex justify-between items-center mb-1">
                  <div class="flex items-center gap-1">
                    <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Top-p</label>
                    <button
                      class="text-xs text-neutral dark:text-gray-400 cursor-help p-1 relative"
                      @mouseover="showTooltip('topP', $event)"
                      @mouseleave="hideTooltip('topP')"
                    >
                      <i class="fa-solid fa-circle-question"></i>
                    </button>
                    <!-- 悬停提示弹窗 -->
                    <div
                      v-if="activeTooltip === 'topP'"
                      class="click-tooltip absolute z-50 bg-white dark:bg-dark-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                      :style="tooltipStyle"
                    >
                      <div class="font-medium mb-1 dark:text-white">Top-p参数说明</div>
                      <p class="text-gray-700 dark:text-gray-300">控制词汇多样性，只有累积概率超过此阈值的词才会被考虑。</p>
                      <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">范围: 0-1</div>
                    </div>
                  </div>
                  <span class="text-xs font-medium text-blue-500 dark:text-blue-400 px-2 py-0.5 bg-blue-500/10 dark:bg-blue-400/10 rounded-full" id="topPValue">{{
                    modelParams.top_p
                  }}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  :value="modelParams.top_p"
                  class="slider w-full"
                  id="topPSlider"
                  @input="handleTopPChange"
                />
                <div class="flex justify-between text-xs text-neutral dark:text-gray-400 mt-1">
                  <span>0</span>
                  <span>1</span>
                </div>
              </div>

              <!-- Top-k参数设置 -->
              <div class="px-2">
                <div class="flex justify-between items-center mb-1">
                  <div class="flex items-center gap-1">
                    <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Top-k</label>
                    <button
                      class="text-xs text-neutral dark:text-gray-400 cursor-help p-1 relative"
                      @mouseover="showTooltip('topK', $event)"
                      @mouseleave="hideTooltip('topK')"
                    >
                      <i class="fa-solid fa-circle-question"></i>
                    </button>
                    <!-- 悬停提示弹窗 -->
                    <div
                      v-if="activeTooltip === 'topK'"
                      class="click-tooltip absolute z-50 bg-white dark:bg-dark-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                      :style="tooltipStyle"
                    >
                      <div class="font-medium mb-1 dark:text-white">Top-k参数说明</div>
                      <p class="text-gray-700 dark:text-gray-300">限制每一步考虑的最高概率词汇数量，较小的值会产生更连贯的结果。</p>
                      <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">范围: 0-100</div>
                    </div>
                  </div>
                  <span class="text-xs font-medium text-blue-500 dark:text-blue-400 px-2 py-0.5 bg-blue-500/10 dark:bg-blue-400/10 rounded-full" id="topKValue">{{
                    modelParams.top_k
                  }}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  :value="modelParams.top_k"
                  class="slider w-full"
                  id="topKSlider"
                  @input="handleTopKChange"
                />
                <div class="flex justify-between text-xs text-neutral dark:text-gray-400 mt-1">
                  <span>0</span>
                  <span>100</span>
                </div>
              </div>

              <!-- 最大长度参数设置 -->
              <div class="px-2">
                <div class="flex justify-between items-center mb-1">
                  <div class="flex items-center gap-1">
                    <label class="text-xs font-medium text-gray-700 dark:text-gray-300">长度</label>
                    <button
                      class="text-xs text-neutral dark:text-gray-400 cursor-help p-1 relative"
                      @mouseover="showTooltip('maxLength', $event)"
                      @mouseleave="hideTooltip('maxLength')"
                    >
                      <i class="fa-solid fa-circle-question"></i>
                    </button>
                    <!-- 悬停提示弹窗 -->
                    <div
                      v-if="activeTooltip === 'maxLength'"
                      class="click-tooltip absolute z-50 bg-white dark:bg-dark-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                      :style="tooltipStyle"
                    >
                      <div class="font-medium mb-1 dark:text-white">最大长度参数说明</div>
                      <p class="text-gray-700 dark:text-gray-300">控制生成内容的最大长度，较大的值可以生成更长的回复，但可能会导致生成时间延长。</p>
                      <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">范围: 512-8192</div>
                    </div>
                  </div>
                  <span class="text-xs font-medium text-blue-500 dark:text-blue-400 px-2 py-0.5 bg-blue-500/10 dark:bg-blue-400/10 rounded-full" id="maxLengthValue">{{
                    modelParams.max_tokens
                  }}</span>
                </div>
                <input
                  type="range"
                  min="512"
                  max="8192"
                  step="512"
                  :value="modelParams.max_tokens"
                  class="slider w-full"
                  id="maxLengthSlider"
                  @input="handleMaxLengthChange"
                />
                <div class="flex justify-between text-xs text-neutral dark:text-gray-400 mt-1">
                  <span>512</span>
                  <span>8192</span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        
        <div
          v-if="uploadedFiles.length > 0"
          class="flex flex-wrap gap-2 p-2 border-b border-gray-200 pb-3"
        >
          <!-- 显示已上传的文件 -->
          <div
            v-for="(file, index) in uploadedFiles"
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-600 rounded-lg text-xs group transition-colors duration-300 ease-in-out min-w-[120px] max-w-[180px] flex-1"
          >
            <div class="flex items-start gap-2 truncate max-w-[80px]">
              <i :class="['fa', getFileIcon(file.name), 'text-gray-500 mt-0 text-xl']"></i>
              <div class="flex flex-col gap-0.5 truncate">
                <span class="truncate">{{ file.name }}</span>
                <span class="text-gray-400 text-[10px]">{{ formatFileSize(file.size) }}</span>
              </div>
            </div>
            <button
              class="text-gray-400 hover:text-red-500 opacity-70 hover:opacity-100 transition-all duration-300 ease-in-out ml-1 text-xs"
              @click="removeUploadedFile(index)"
            >
              <i class="fa-solid fa-circle-xmark"></i>
            </button>
          </div>
        </div>
        <div class="p-3 pt-4 pb-1 relative">
          <textarea
            v-model="messageInput"
            placeholder="Message Or UploadFile For Chato..."
            class="w-full resize-none border-none focus:ring-0 focus:outline-none text-base leading-relaxed placeholder-gray-400 dark:text-white dark:placeholder-gray-500 bg-transparent transition-all duration-300 ease-in-out"
            rows="2"
            @keydown.enter.exact.prevent="handleSendMessage"

          ></textarea>
        </div>
        <!-- 拖拽提示区域 - 移动到外层，覆盖整个卡片容器 -->
        <div
          v-if="isDragOver"
          class="absolute inset-0 flex flex-col items-center justify-center bg-blue-50 dark:bg-blue-900/20 border-2 border-dashed border-primary dark:border-blue-400 rounded-3xl opacity-100 pointer-events-none transition-all duration-300 z-20 animate-pulse"
        >
          <i class="fa-solid fa-cloud-arrow-up text-primary dark:text-blue-400 text-4xl mb-2"></i>
          <span class="text-primary dark:text-blue-400 font-medium">释放文件以上传</span>
          <span class="text-sm text-gray-600 dark:text-gray-300 mt-1">或点击上传附件按钮</span>
        </div>
        <div class="flex items-center justify-between px-3 py-2 gap-2">
          <div class="flex items-center gap-3">
            <!-- 上传附件按钮 -->
            <Tooltip content="上传附件">
              <button
                  class="btn-secondary w-8 h-8 flex items-center justify-center rounded-lg transition-all duration-300 ease-in-out"
                  :class="{
                      'text-gray-500 dark:text-gray-300 hover:text-primary': uploadedFiles.length === 0,
                      'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/40': uploadedFiles.length > 0
                    }"
                @click="triggerFileUpload"
              >
                <i class="fa-solid fa-paperclip"></i>
              </button>
            </Tooltip>
            <!-- 隐藏的文件输入 -->
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              @change="handleFileInputChange"
              multiple
              accept=".txt,.pdf,.doc,.docx,.md,.jpg,.jpeg,.png,.gif,.csv,.xlsx,.pptx"
            >
            <!-- 深度思考切换按钮 -->
            <Tooltip content="深度思考">
              <button
                class="btn-secondary flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ease-in-out"
                :class="{
                    'text-gray-500 dark:text-gray-300 hover:text-primary': !isDeepThinking,
                    'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/40': isDeepThinking
                  }"
                @click="toggleDeepThinking"
              >
                <i class="fa-solid fa-lightbulb"></i>
              </button>
            </Tooltip>
            <!-- 文件夹列表按钮 -->
            <Tooltip content="文件夹列表">
              <button
                class="btn-secondary flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ease-in-out text-gray-500 dark:text-gray-300 hover:text-primary"
                @click="setActiveSidebar('folder')"
              >
                <i class="fa-solid fa-book-open"></i>
              </button>
            </Tooltip>
            <!-- 联网搜索切换按钮 -->
            <Tooltip content="联网搜索">
              <button
                class="btn-secondary flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ease-in-out"
                :class="{
                    'text-gray-500 dark:text-gray-300 hover:text-primary': !isWebSearchEnabled,
                    'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/40': isWebSearchEnabled
                  }"
                @click="toggleWebSearch"
              >
                <i class="fa-solid fa-globe"></i>
              </button>
            </Tooltip>
            <!-- 消息列表按钮 -->
            <Tooltip content="消息列表">
              <button
                class="btn-secondary flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ease-in-out text-gray-500 dark:text-gray-300 hover:text-primary"
                @click="setActiveSidebar('message')"
              >
                <i class="fa-solid fa-comment-dots"></i>
              </button>
            </Tooltip>
            <!-- MCP启动按钮 -->
            <Tooltip content="MCP工具">
              <button
                class="btn-secondary flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ease-in-out text-gray-500 dark:text-gray-300 hover:text-primary"
                @click="setActiveSidebar('mcp')"
              >
                <i class="fa-solid fa-gear"></i>
              </button>
            </Tooltip>
            <div class="relative">
              <Tooltip :content="availableModels.length > 1 ? '选择AI模型' : '只有一个可用模型'">
                <button
                  class="h-8 flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-dark-700 px-3 rounded-lg transition-all duration-300 ease-in-out"
                  :class="{
                    'btn-secondary hover:bg-gray-100 dark:hover:bg-dark-600 hover:text-primary cursor-pointer': availableModels.length > 1,
                    'cursor-default opacity-70': availableModels.length <= 1
                  }"
                  @click="toggleModelDropdown"
                >
                  <span>{{ currentModelDisplayName }}</span>
                  <i v-if="availableModels.length > 1" class="fa-solid fa-chevron-down text-xs text-neutral"></i>
                </button>
              </Tooltip>
              <div
                ref="modelDropdown"
                class="dropdown absolute left-0 bottom-full mb-2 w-48 bg-white dark:bg-dark-700 z-50 shadow-lg rounded-lg border border-gray-200 dark:border-gray-700 animate-fade-in"
                :class="{ 'hidden': !showModelDropdown }"
                style="z-index: 1000 !important"
              >
                <div class="py-1">
                  <button
                    v-for="model in orderedModels"
                    :key="model.value"
                    class="model-option w-full text-left px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors"
                    :class="{ 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/30': model.value === currentModel }"
                    @click="selectModel(model.value)"
                  >
                    {{ model.displayName }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <button
              v-if="!hasActiveStreaming"
              class="w-8 h-8 flex items-center justify-center text-white bg-primary hover:bg-secondary rounded-full transition-all duration-300 ease-in-out hover:scale-105"
            @click="handleSendMessage"
          >
            <i class="fa-solid fa-arrow-up"></i>
          </button>
          <Tooltip v-else content="终止输出">
            <button
              class="w-8 h-8 flex items-center justify-center text-white bg-red-500 hover:bg-red-600 rounded-full transition-all duration-300 ease-in-out hover:scale-105"
              @click="handleCancelStreaming"
            >
              <i class="fa-solid fa-stop"></i>
            </button>
          </Tooltip>
        </div>
      </div>
      </DragDropZone>
      <div v-if="showShortcutHint" class="text-center text-xs text-gray-400 dark:text-gray-500 mt-[18px] transition-opacity duration-300">
        按Shift+Enter换行，Enter发送
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { StorageManager } from '../../../../shared/utils/storage.js';
import { formatFileSize } from '../../../../shared/utils/helpers.js';
import Tooltip from '../../../../shared/ui/Tooltip.vue';
import DragDropZone from '../../../../shared/ui/DragDropZone.vue';
import logger from '../../../../shared/utils/logger.js';
import { useChatStore } from '../../../../app/store/chatStore.js';
import { useSettingsStore } from '../../../../app/store/settingsStore.js';
import { useNotifications } from '../../composables/useNotifications.js';
import { useNavigation } from '../../../../shared/composables/useNavigation.js';
import { useAppUI } from '../../../../shared/composables/useAppUI.js';

// 接收从父组件传递的视图状态
const _props = defineProps({
  activeView: {
    type: String,
    required: true
  },
  showShortcutHint: {
    type: Boolean,
    default: true
  }
});

// 定义存储键
const STORAGE_KEYS = {
  DEEP_THINKING: 'deepThinkingMode',
  WEB_SEARCH: 'webSearchEnabled'
};

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();
const { handleSystemSettingsClick } = useNavigation();
const { toggleRightPanel, setActiveSidebar } = useAppUI();

// 直接使用settingsStore的模型相关功能
const availableModels = computed(() => settingsStore.availableModels);
const loadModels = settingsStore.loadModels;
const modelList = computed(() => settingsStore.models);
const selectedModel = computed(() => settingsStore.systemSettings.defaultModel);

// 模型相关辅助函数
const getModelById = (modelId) => {
  if (!modelId || !settingsStore.models.length) return null;
  const [modelName, versionName] = modelId.split('-', 2);
  const model = settingsStore.models.find(m => m.name === modelName);
  if (model && model.versions) {
    const version = model.versions.find(v => v.version_name === versionName);
    return { model, version };
  }
  return null;
};

const checkStreamingSupport = (modelId) => {
  const modelData = getModelById(modelId);
  if (!modelData || !modelData.version) return false;
  // 支持多种字段名，兼容不同版本的后端返回格式
  return modelData.version.streaming || modelData.version.streamingConfig || modelData.version.streaming_config || false;
};

const standardizeModelId = (modelId) => {
  return modelId || '';
};

const setSelectedModel = (modelId) => {
  settingsStore.systemSettings.defaultModel = modelId;
};

const getModelDefaultParams = (modelId) => {
  // 默认参数，根据模型可能需要调整
  return {
    temperature: 0.7,
    max_tokens: 2000,
    top_p: 1.0,
    top_k: 50,
    frequency_penalty: 0.0,
  };
};

// 使用通知管理组合函数
const { showSystemNotification } = useNotifications();

// 拖拽状态管理
const dragCounter = ref(0);
const isDragOver = ref(false);

// 使用ref引用DOM元素
const fileInput = ref(null);
const modelDropdown = ref(null);
const agentDropdown = ref(null);

// 顶部导航栏迁移功能的状态管理
const userMenuContainer = ref(null);
const showUserMenu = ref(false);

// 本地UI状态
const showModelDropdown = ref(false);
const showAgentDropdown = ref(false);
const showParamsPanel = ref(false);
// 新增状态：检查是否有活动的流式输出
const hasActiveStreaming = ref(false);
// 深度思考模式状态 - 从存储加载
const isDeepThinking = ref(StorageManager.getItem(STORAGE_KEYS.DEEP_THINKING, false));
// 联网搜索状态 - 从存储加载
const isWebSearchEnabled = ref(StorageManager.getItem(STORAGE_KEYS.WEB_SEARCH, false));
// RAG模式状态 - 从settingsStore获取
const _isRagMode = computed(() => settingsStore.activePanel === 'rag');

// 智能体相关状态
const currentAgent = ref('default');
// 可用智能体列表
const availableAgents = ref([
  { value: 'default', displayName: '默认智能体', icon: 'fa-comment' },
  { value: 'code', displayName: '代码助手', icon: 'fa-code' },
  { value: 'write', displayName: '写作助手', icon: 'fa-pen-to-square' },
  { value: 'research', displayName: '研究助手', icon: 'fa-search' },
  { value: 'translate', displayName: '翻译助手', icon: 'fa-language' },
  { value: 'analyze', displayName: '数据分析助手', icon: 'fa-chart-simple' }
]);

// 当前智能体显示名称
const currentAgentDisplayName = computed(() => {
  const agent = availableAgents.value.find(a => a.value === currentAgent.value);
  return agent ? agent.displayName : '默认智能体';
});

// 工具提示相关状态
const activeTooltip = ref('');
const tooltipStyle = ref({});

// 从useModelConfig获取模型参数
const modelParams = computed(() => {
  // 使用当前模型获取对应的参数
  if (!currentModel.value) return {};
  return getModelDefaultParams(currentModel.value);
});



// 切换深度思考模式
const toggleDeepThinking = () => {
  isDeepThinking.value = !isDeepThinking.value;
  StorageManager.setItem(STORAGE_KEYS.DEEP_THINKING, isDeepThinking.value);
};

// 切换联网搜索模式
const toggleWebSearch = () => {
  isWebSearchEnabled.value = !isWebSearchEnabled.value;
  StorageManager.setItem(STORAGE_KEYS.WEB_SEARCH, isWebSearchEnabled.value);
};

// 从store获取当前聊天的模型，优先使用当前对话的模型，否则使用settingsStore中的默认模型
// 注意：聊天界面选择模型不会修改系统默认设置，只影响当前聊天
const currentModel = ref(chatStore.currentChat?.model || settingsStore.systemSettings.defaultModel);

// 监听系统默认模型变化，更新当前模型（如果用户没有手动选择过）
let userHasSelectedModel = false;

watch(
  () => settingsStore.systemSettings.defaultModel,
  (newDefaultModel) => {
    if (!userHasSelectedModel && newDefaultModel) {
      currentModel.value = newDefaultModel;
    }
  }
);

// 获取当前模型的显示名称，与默认模型下拉框显示规则保持一致
const currentModelDisplayName = computed(() => {
  // 当没有可用模型时显示提示信息
  if ((!availableModels.value || availableModels.value.length === 0)) {
    return '暂无可用模型';
  }
  
  // 当currentModel为空或无效时，使用默认模型名称
  if (!currentModel.value || !modelList.value.length) {
    return currentModel.value || settingsStore.systemSettings.defaultModel || '默认模型';
  }
  
  // 遍历所有模型，找到匹配的模型
  for (const model of modelList.value) {
    if (model.versions) {
      for (const version of model.versions) {
        // 构建select组件使用的模型ID格式：model.name-version_name
        const selectModelId = `${model.name}-${version.version_name}`;
        // 同时检查select组件格式和直接匹配version_name/custom_name
        if (selectModelId === currentModel.value || 
            version.version_name === currentModel.value || 
            version.custom_name === currentModel.value) {
          // 使用模型的name
          const modelDisplay = model.name;
          // 优先使用版本的custom_name，否则使用版本的version_name
          const versionDisplay = version.custom_name || version.version_name;
          // 返回格式：name-versionDisplay（与默认模型下拉框保持一致）
          return `${modelDisplay}-${versionDisplay}`;
        }
      }
    }
  }
  
  // 如果当前模型不在可用模型列表中，返回当前模型值或默认名称
  return currentModel.value || '默认模型';
});

// 获取格式化后的模型列表（包含displayName和原始model值），与默认模型下拉框显示规则保持一致
const formattedModels = computed(() => {
  // 确保availableModels是数组
  const modelsList = availableModels.value || [];
  
  if (!modelList.value.length) {
    return modelsList.map(model => ({ 
      value: model, 
      displayName: model 
    }));
  }
  
  const result = [];
  
  // 遍历availableModels中的每个模型名
  for (const modelName of modelsList) {
    let found = false;
    
    // 遍历所有模型和版本，找到匹配的模型
    for (const model of modelList.value) {
      if (model.versions) {
        for (const version of model.versions) {
          // 构建select组件使用的模型ID格式：model.name-version_name
          const selectModelId = `${model.name}-${version.version_name}`;
          // 同时检查select组件格式和直接匹配version_name/custom_name
          if (selectModelId === modelName || 
              version.version_name === modelName || 
              version.custom_name === modelName) {
            // 使用模型的name
            const modelDisplay = model.name;
            // 优先使用版本的custom_name，否则使用版本的version_name
            const versionDisplay = version.custom_name || version.version_name;
            // 返回格式：name-versionDisplay（与默认模型下拉框保持一致）
            result.push({
              value: modelName,
              displayName: `${modelDisplay}-${versionDisplay}`
            });
            found = true;
            break;
          }
        }
        if (found) break;
      }
    }
    
    // 如果没找到匹配的模型，使用原始名称
    if (!found) {
      result.push({ value: modelName, displayName: modelName });
    }
  }
  
  return result;
});

// availableModels 已从 useModelConfig 组合函数中导入

// 排序模型列表，使当前选中的模型在最底部
const orderedModels = computed(() => {
  // 确保formattedModels是数组
  const models = [...(formattedModels.value || [])];
  const currentModelIndex = models.findIndex(m => m.value === currentModel.value);
  
  if (currentModelIndex !== -1) {
    // 保存当前选中的模型
    const currentModelObj = models[currentModelIndex];
    // 从数组中移除当前选中的模型
    models.splice(currentModelIndex, 1);
    // 将当前选中的模型添加到数组末尾
    models.push(currentModelObj);
  }
  
  return models;
});

const messageInput = computed({
  get: () => chatStore.messageInput,
  set: (value) => chatStore.updateMessageInput(value),
});

// 从store直接获取响应式数据
const uploadedFiles = computed(() => chatStore.uploadedFiles);

// 定义事件
const emit = defineEmits(['sendMessage']);

// 处理发送消息事件
const handleSendMessage = async () => {
  if (messageInput.value.trim() || uploadedFiles.value.length > 0) {
    // 先保存当前需要发送的消息内容和模型
    const messageToSend = messageInput.value;
    const modelToUse = currentModel.value;
    const deepThinking = isDeepThinking.value;
    const webSearchEnabled = isWebSearchEnabled.value;
    
    // 立即发送消息，不等待Ollama服务检查
    emit('sendMessage', messageToSend, modelToUse, deepThinking, webSearchEnabled);
    // 发送消息后立即检查是否有流式输出
    checkForActiveStreaming();
    
    // 如果是Ollama模型，在后台异步检查和启动服务
    if (modelToUse.includes('Ollama')) {
      // 使用setTimeout将检查操作放入事件队列，避免阻塞UI
      setTimeout(async () => {
        try {
          // 使用Python API检查和启动Ollama服务
          // 检查Ollama服务状态
          const ollamaStatus = await apiService.get('/api/ollama/status');
          
          if (!ollamaStatus.installed) {
            // Ollama未安装，显示提示
            showSystemNotification('Ollama未安装，请先安装Ollama后再使用该模型', 'error', 3000);
          } else if (!ollamaStatus.running) {
            // 如果服务没有运行，启动它
            await apiService.post('/api/ollama/start');
            // 显示服务正在启动的提示
            showSystemNotification('Ollama服务正在启动，请稍候...', 'success', 3000);
          }
        } catch (error) {
          logger.error('Ollama服务管理失败:', error);
          // 显示更具体的错误信息
          showSystemNotification(`Ollama服务管理失败: ${error.message || error}`, 'error', 3000);
        }
      }, 0);
    }
  }
};

// 监听当前聊天变化，重置用户选择标志
watch(
  () => chatStore.currentChatId,
  () => {
    // 新聊天时，重置用户选择标志
    userHasSelectedModel = false;
    // 优先使用当前对话保存的模型，如果没有则使用系统默认模型
    currentModel.value = chatStore.currentChat?.model || settingsStore.systemSettings.defaultModel || selectedModel.value;
  }
);

// 处理取消流式输出
const handleCancelStreaming = () => {
  chatStore.cancelStreaming();
  hasActiveStreaming.value = false;
};



// 检查是否有活动的流式输出
const checkForActiveStreaming = () => {
  const currentMessages = chatStore.currentChatMessages;
  if (currentMessages.length > 0) {
    const lastMessage = currentMessages[currentMessages.length - 1];
    const messageData = lastMessage?.value || lastMessage;
    
    // 无论是否启用流式输出，都要检查isTyping状态
    // 只有启用流式输出时，才检查streaming状态
    hasActiveStreaming.value = messageData?.isTyping === true || 
                              (settingsStore.systemSettings.streamingEnabled && messageData?.status === 'streaming');
  } else {
    hasActiveStreaming.value = false;
  }
};

// 监听聊天消息变化，检查流式输出状态
watch(
  () => chatStore.currentChatMessages,
  () => {
    checkForActiveStreaming();
  },
  { deep: true }
);

// 监听isLoading状态变化，检查流式输出状态
watch(
  () => chatStore.isLoading,
  (newVal) => {
    if (!newVal) {
      // 加载完成后，流式输出也应该结束
      setTimeout(() => {
        checkForActiveStreaming();
      }, 100);
    }
  }
);

// 监听模型列表变化，更新当前模型
watch(
  () => modelList.value,
  () => {
    // 模型列表更新后，如果当前模型无效或为空，重新设置当前模型
    if (!currentModel.value || !availableModels.value.includes(currentModel.value)) {
      currentModel.value = chatStore.currentChat?.model || settingsStore.systemSettings.defaultModel || availableModels.value[0];
    }
  },
  { deep: true }
);

// 监听可用模型列表变化，更新当前模型
watch(
  () => availableModels.value,
  (newList) => {
    // 可用模型列表更新后，如果当前模型无效或为空，重新设置当前模型
    if (!currentModel.value || !newList.includes(currentModel.value)) {
      currentModel.value = chatStore.currentChat?.model || settingsStore.systemSettings.defaultModel || newList[0];
    }
  },
  { deep: true }
);

// 切换模型下拉菜单显示状态
const toggleModelDropdown = () => {
  // 只有当可用模型数量大于1时才允许切换下拉菜单
  if (availableModels.value.length > 1) {
    showModelDropdown.value = !showModelDropdown.value;
    // 关闭智能体下拉菜单
    showAgentDropdown.value = false;
  }
};

// 选择模型
const selectModel = (model) => {
  currentModel.value = model;
  // 设置标志，表明用户已经手动选择了模型
  userHasSelectedModel = true;
  showModelDropdown.value = false;
};

// 切换智能体下拉菜单显示状态
const toggleAgentDropdown = () => {
  showAgentDropdown.value = !showAgentDropdown.value;
  // 关闭模型下拉菜单
  showModelDropdown.value = false;
};

// 选择智能体
const selectAgent = (agent) => {
  currentAgent.value = agent;
  showAgentDropdown.value = false;
};

// 切换参数面板显示状态
const toggleParamsPanel = () => {
  showParamsPanel.value = !showParamsPanel.value;
};

// 处理温度参数变化
const handleTemperatureChange = (event) => {
  settingsStore.updateModelParams({ temperature: parseFloat(event.target.value) });
};

// 处理Top-p参数变化
const handleTopPChange = (event) => {
  settingsStore.updateModelParams({ top_p: parseFloat(event.target.value) });
};

// 处理Top-k参数变化
const handleTopKChange = (event) => {
  settingsStore.updateModelParams({ top_k: parseInt(event.target.value) });
};

// 处理最大长度参数变化
const handleMaxLengthChange = (event) => {
  settingsStore.updateModelParams({ max_tokens: parseInt(event.target.value) });
};

// 显示提示信息
const showTooltip = (tooltipId, event) => {
  activeTooltip.value = tooltipId;
  
  // 计算弹窗位置
  if (event) {
    const trigger = event.target;
    const tooltip = trigger.nextElementSibling;
    
    if (tooltip) {
      // 获取触发元素和视口的相对位置
      const triggerRect = trigger.getBoundingClientRect();
      const tooltipRect = tooltip.getBoundingClientRect();
      
      // 计算提示框应该显示的位置
      // 水平方向：显示在触发元素右侧，留出5px间距
      // 垂直方向：与触发元素顶部对齐
      tooltipStyle.value = {
        // 提示框定位到按钮右侧，垂直居中对齐
        top: `-${(tooltipRect.height - triggerRect.height) / 2}px`,
        left: `${triggerRect.width + 5}px`,
        // 移除可能导致定位问题的transform
        transform: 'none'
      };
    }
  }
};

// 隐藏提示信息
const hideTooltip = (tooltipId) => {
  // 如果传入了tooltipId，只隐藏特定的提示
  if (tooltipId) {
    if (activeTooltip.value === tooltipId) {
      activeTooltip.value = '';
    }
  } else {
    // 否则隐藏所有提示
    activeTooltip.value = '';
  }
};

// 处理MCP工具点击事件
const handleMcpService = () => {
  settingsStore.setActivePanel('mcp');
};

// 切换知识库状态
const toggleKnowledgeBase = () => {
  if (settingsStore.activePanel === 'rag') {
    // 如果当前是知识库模式，切换回聊天模式
    settingsStore.setActivePanel('history');
    
    // 主显示区：如果没有聊天消息，显示sendMessage视图，否则显示chat视图
    const hasMessages = chatStore.currentChatMessages && chatStore.currentChatMessages.length > 0;
    settingsStore.setActiveContent(hasMessages ? 'chat' : 'sendMessage');
    
    // 关闭RAG功能
    settingsStore.updateVectorConfig({ enabled: false });
  } else {
    // 如果当前不是知识库模式，切换到知识库模式
    settingsStore.setActivePanel('rag');
    
    // 启用RAG功能
    settingsStore.updateVectorConfig({ enabled: true });
  }
};

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  // 关闭模型下拉菜单
  if (modelDropdown.value && !modelDropdown.value.contains(event.target) &&
      !event.target.closest('button') && showModelDropdown.value) {
    showModelDropdown.value = false;
  }
  
  // 关闭智能体下拉菜单
  if (agentDropdown.value && !agentDropdown.value.contains(event.target) &&
      !event.target.closest('button') && showAgentDropdown.value) {
    showAgentDropdown.value = false;
  }
  
  // 关闭用户菜单
  if (showUserMenu.value && userMenuContainer.value) {
    if (!userMenuContainer.value.contains(event.target)) {
      closeUserMenu();
    }
  }
};

// 顶部导航栏迁移功能的函数
const toggleViewPanel = () => toggleRightPanel();
const handleToggleTheme = () => settingsStore.toggleDarkMode();

const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value; };
const closeUserMenu = () => { showUserMenu.value = false; };
const handleSwitchAccount = () => {
  closeUserMenu();
  logger.info('切换账户');
};
const handleLogout = () => {
  closeUserMenu();
  showSystemNotification('退出账号功能待实现', 'info');
};

// 生命周期钩子
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  
  // 立即检查isTyping状态，确保按钮显示正确
  checkForActiveStreaming();
  
  // 监听chatStore.isLoading状态变化，立即更新按钮状态
  watch(
    () => chatStore.isLoading,
    () => {
      // 无论isLoading状态如何变化，都立即检查isTyping状态
      checkForActiveStreaming();
    }
  );
  
  // 额外添加一个定时器，确保在组件完全渲染后再次检查状态
  setTimeout(() => {
    checkForActiveStreaming();
  }, 0);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// 处理文件拖放
const handleDrop = (e) => {
  dragCounter.value = 0;
  isDragOver.value = false;
  if (e.dataTransfer.files.length > 0) {
    handleFileUpload(e.dataTransfer.files);
  }
};



// 触发文件上传对话框
const triggerFileUpload = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// 处理文件输入变化事件
const handleFileInputChange = (e) => {
  if (e.target.files.length > 0) {
    handleFileUpload(e.target.files);
    // 重置输入，以便可以重复上传同一个文件
    e.target.value = '';
  }
};

// 处理上传文件事件
const handleFileUpload = (files) => {
  // 将文件添加到上传列表
  Array.from(files).forEach((file) => {
    chatStore.addUploadedFile(file);
  });
};

// 移除已上传的文件
const removeUploadedFile = (index) => {
  chatStore.removeUploadedFile(index);
};

// 获取文件图标
const getFileIcon = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase();
  
  const iconMap = {
    txt: 'fa-file-lines',
    pdf: 'fa-file-pdf',
    doc: 'fa-file-word',
    docx: 'fa-file-word',
    md: 'fa-file-lines',
    jpg: 'fa-file-image',
    jpeg: 'fa-file-image',
    png: 'fa-file-image',
    gif: 'fa-file-image',
    csv: 'fa-file-excel',
    xlsx: 'fa-file-excel',
    pptx: 'fa-file-powerpoint'
  };
  
  return iconMap[extension] || 'fa-file';
};



</script>

<style scoped>
/* 参数面板滑入滑出动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  opacity: 1;
  transform: translateY(0);
}

.slide-up-enter-from,
.slide-up-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

/* 滑块样式 */
.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  outline: none;
  transition: background 0.3s ease;
}

.slider:hover {
  background: #9ca3af;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.slider::-moz-range-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

/* 深色模式滑块样式 */
.dark .slider {
  background: #374151;
}

.dark .slider:hover {
  background: #6b7280;
}

.dark .slider::-webkit-slider-thumb {
  background: #60a5fa;
  box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2);
}

.dark .slider::-webkit-slider-thumb:hover {
  background: #3b82f6;
  transform: scale(1.2);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.dark .slider::-moz-range-thumb {
  background: #60a5fa;
  box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2);
}

.dark .slider::-moz-range-thumb:hover {
  background: #3b82f6;
  transform: scale(1.2);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.2s ease-in-out;
}
</style>