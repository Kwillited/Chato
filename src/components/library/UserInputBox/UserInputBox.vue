<template>
  
  <!-- 聊天输入区域 - 在切换到图谱视图时添加顶部padding -->
  <div id="UserInputBox" class="border-t-0 pb-4 px-6 transition-colors duration-300 ease-in-out" :class="{ 'pt-4': activeView !== 'chat' }">
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
          
          <!-- 展开/折叠控制按钮 -->
          <div class="flex-1 flex justify-end items-center">
            <button
              class="h-6 w-6 flex items-center justify-center text-sm text-gray-600 dark:text-gray-300 hover:text-primary transition-all duration-300 ease-in-out"
              @click="toggleParamsPanel"
              :class="{ 'rotate-180': showParamsPanel }"
            >
              <i class="fa-solid fa-chevron-down text-xs"></i>
            </button>
          </div>
          
          <!-- 应用控制按钮 -->
          <div class="flex items-center gap-2 pr-2">
            <!-- 直接显示视图按钮 -->
            <Button 
              icon="fa-columns"
              tooltip="视图"
              @click="toggleViewPanel"
              size="sm"
              shape="full"
            />
            
            <!-- 分隔栏 -->
            <div class="h-4 w-px bg-gray-200 dark:bg-dark-700 mx-0.5"></div>
            
            <!-- 主题切换按钮 -->
            <Button 
              :icon="settingsStore.systemSettings.darkMode ? 'fa-sun' : 'fa-moon'"
              tooltip="切换主题"
              @click="handleToggleTheme"
              size="sm"
              shape="full"
            />
            
            <Button 
              icon="fa-gear"
              tooltip="系统设置"
              @click="handleSystemSettingsClick"
              size="sm"
              shape="full"
            />
            
            <Button 
              icon="fa-brain"
              tooltip="AI配置"
              @click="handleAISettingsClick"
              size="sm"
              shape="full"
            />
            
            <!-- 用户按钮带下拉菜单 -->
            <div class="relative hover-scale">
                <Button 
                  icon="fa-user-circle"
                  @click.stop="toggleUserMenu"
                  size="sm"
                  shape="full"
                  class="i:text-base"
                />
              
              <!-- 用户功能下拉菜单 -->
              <div 
                v-if="showUserMenu"
                class="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 w-14 rounded-lg shadow-lg border z-50 dropdown-content flex flex-col items-center py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700"
              >
                <Button 
                  icon="fa-exchange"
                  tooltip="切换账户"
                  @click="handleSwitchAccount"
                  size="lg"
                  shape="full"
                />
                <div class="my-1 w-8 border-t border-gray-200 dark:border-dark-700"></div>
                <Button 
                  icon="fa-arrow-right-from-bracket"
                  tooltip="退出账号"
                  @click="handleLogout"
                  size="lg"
                  shape="full"
                  class="text-red-500"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 可上滑展开的参数设置区域 -->
        <transition name="slide-up">
          <div v-if="showParamsPanel" class="border-b border-gray-200 overflow-hidden transition-all duration-300 ease-in-out">
            <div class="px-3 py-3 flex items-center gap-3">
              <!-- 左换页按钮 -->
              <button
                class="flex items-center justify-center w-8 h-8 text-gray-600 dark:text-gray-300 hover:text-primary transition-colors"
                @click="prevPage"
                :disabled="currentPage === 0"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage === 0 }"
              >
                <i class="fa-solid fa-chevron-left"></i>
              </button>
              
              <!-- 参数设置区域 -->
              <div class="flex-1 grid grid-cols-4 gap-3">
                <!-- 第一页参数 -->
                <template v-if="currentPage === 0">
                  <!-- 温度参数设置 -->
                  <div class="px-2">
                    <div class="flex justify-between items-center mb-1">
                      <div class="flex items-center gap-1">
                        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">温度</label>

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

                        <!-- 悬停提示弹窗 -->
                        <div
                          v-if="activeTooltip === 'topP'"
                          class="click-tooltip absolute z-50 bg-white dark:bg-dark-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                          :style="tooltipStyle"
                        >
                          <div class="font-medium mb-1 dark:text-white">Top-p参数说明</div>
                          <p class="text-gray-700 dark:text-gray-300">控制词汇多样性，只有累积概率超过此阈值的词才会被考虑。</p>
                          <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">范围: 0.1-1</div>
                        </div>
                      </div>
                      <span class="text-xs font-medium text-blue-500 dark:text-blue-400 px-2 py-0.5 bg-blue-500/10 dark:bg-blue-400/10 rounded-full" id="topPValue">{{
                        modelParams.top_p
                      }}</span>
                    </div>
                    <input
                      type="range"
                      min="0.1"
                      max="1"
                      step="0.05"
                      :value="modelParams.top_p"
                      class="slider w-full"
                      id="topPSlider"
                      @input="handleTopPChange"
                    />
                    <div class="flex justify-between text-xs text-neutral dark:text-gray-400 mt-1">
                      <span>0.1</span>
                      <span>1</span>
                    </div>
                  </div>

                  <!-- Top-k参数设置 -->
                  <div class="px-2">
                    <div class="flex justify-between items-center mb-1">
                      <div class="flex items-center gap-1">
                        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">Top-k</label>

                        <!-- 悬停提示弹窗 -->
                        <div
                          v-if="activeTooltip === 'topK'"
                          class="click-tooltip absolute z-50 bg-white dark:bg-dark-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                          :style="tooltipStyle"
                        >
                          <div class="font-medium mb-1 dark:text-white">Top-k参数说明</div>
                          <p class="text-gray-700 dark:text-gray-300">限制每一步考虑的最高概率词汇数量，较小的值会产生更连贯的结果。</p>
                          <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">范围: 1-100</div>
                        </div>
                      </div>
                      <span class="text-xs font-medium text-blue-500 dark:text-blue-400 px-2 py-0.5 bg-blue-500/10 dark:bg-blue-400/10 rounded-full" id="topKValue">{{
                        modelParams.top_k
                      }}</span>
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="100"
                      step="1"
                      :value="modelParams.top_k"
                      class="slider w-full"
                      id="topKSlider"
                      @input="handleTopKChange"
                    />
                    <div class="flex justify-between text-xs text-neutral dark:text-gray-400 mt-1">
                      <span>1</span>
                      <span>100</span>
                    </div>
                  </div>

                  <!-- 最大长度参数设置 -->
                  <div class="px-2">
                    <div class="flex justify-between items-center mb-1">
                      <div class="flex items-center gap-1">
                        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">长度</label>

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
                </template>
                
                <!-- 第二页参数 -->
                <template v-else-if="currentPage === 1">
                  <!-- 检索相关性阈值设置 -->
                  <div class="px-2">
                    <div class="flex justify-between items-center mb-1">
                      <div class="flex items-center gap-1">
                        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">相关性阈值</label>

                        <!-- 悬停提示弹窗 -->
                        <div
                          v-if="activeTooltip === 'threshold'"
                          class="click-tooltip absolute z-50 bg-white dark:bg-dark-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                          :style="tooltipStyle"
                        >
                          <div class="font-medium mb-1 dark:text-white">检索相关性阈值说明</div>
                          <p class="text-gray-700 dark:text-gray-300">控制文档相关性的最低分数要求，较高的值会返回更相关但可能更少的文档。</p>
                          <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">范围: 0-1</div>
                        </div>
                      </div>
                      <span class="text-xs font-medium text-blue-500 dark:text-blue-400 px-2 py-0.5 bg-blue-500/10 dark:bg-blue-400/10 rounded-full" id="thresholdValue">{{
                        vectorStore.config.retrieval.threshold
                      }}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      :value="vectorStore.config.retrieval.threshold"
                      class="slider w-full"
                      id="thresholdSlider"
                      @input="handleThresholdChange"
                    />
                    <div class="flex justify-between text-xs text-neutral dark:text-gray-400 mt-1">
                      <span>0</span>
                      <span>1</span>
                    </div>
                  </div>
                  
                  <!-- 检索文档数量设置 -->
                  <div class="px-2">
                    <div class="flex justify-between items-center mb-1">
                      <div class="flex items-center gap-1">
                        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">检索文档数</label>

                        <!-- 悬停提示弹窗 -->
                        <div
                          v-if="activeTooltip === 'topK'"
                          class="click-tooltip absolute z-50 bg-white dark:bg-dark-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                          :style="tooltipStyle"
                        >
                          <div class="font-medium mb-1 dark:text-white">检索文档数量说明</div>
                          <p class="text-gray-700 dark:text-gray-300">控制每次查询返回的文档数量，较多的文档可以提供更全面的信息，但可能会增加处理时间。</p>
                          <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">范围: 1-20</div>
                        </div>
                      </div>
                      <span class="text-xs font-medium text-blue-500 dark:text-blue-400 px-2 py-0.5 bg-blue-500/10 dark:bg-blue-400/10 rounded-full" id="retrievalTopKValue">{{
                        vectorStore.config.retrieval.topK
                      }}</span>
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="20"
                      step="1"
                      :value="vectorStore.config.retrieval.topK"
                      class="slider w-full"
                      id="retrievalTopKSlider"
                      @input="handleRetrievalTopKChange"
                    />
                    <div class="flex justify-between text-xs text-neutral dark:text-gray-400 mt-1">
                      <span>1</span>
                      <span>20</span>
                    </div>
                  </div>
                  
                  <!-- 文档检索模式设置 -->
                  <div class="px-2">
                    <div class="flex justify-between items-center mb-1">
                      <div class="flex items-center gap-1">
                        <label class="text-xs font-medium text-gray-700 dark:text-gray-300">检索模式</label>

                        <!-- 悬停提示弹窗 -->
                        <div
                          v-if="activeTooltip === 'retrievalMode'"
                          class="click-tooltip absolute z-50 bg-white dark:bg-dark-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                          :style="tooltipStyle"
                        >
                          <div class="font-medium mb-1 dark:text-white">检索模式说明</div>
                          <p class="text-gray-700 dark:text-gray-300">设置知识库的文档检索方式，不同的检索方式会影响检索结果的准确性和速度。</p>
                          <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">选项: 向量检索、关键词检索、混合检索</div>
                        </div>
                      </div>
                      <span class="text-[10px] font-medium text-blue-500 dark:text-blue-400 px-2 py-0.5 bg-blue-500/10 dark:bg-blue-400/10 rounded-full" id="retrievalModeValue">{{
                        getRetrievalModeDisplay(vectorStore.config.retrieval.mode)
                      }}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="1"
                      :value="getRetrievalModeValue(vectorStore.config.retrieval.mode)"
                      class="slider w-full"
                      id="retrievalModeSlider"
                      @input="handleRetrievalModeSliderChange"
                    />
                    <div class="flex justify-between text-xs text-neutral dark:text-gray-400 mt-1">
                      <span>向量</span>
                      <span>关键词</span>
                      <span>混合</span>
                    </div>
                  </div>
                  
                  <!-- 空占位 -->
                  <div class="px-2"></div>
                </template>
              </div>
              
              <!-- 右换页按钮 -->
              <button
                class="flex items-center justify-center w-8 h-8 text-gray-600 dark:text-gray-300 hover:text-primary transition-colors"
                @click="nextPage"
                :disabled="currentPage === 1"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
              >
                <i class="fa-solid fa-chevron-right"></i>
              </button>
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
            <!-- 知识库按钮 - 恢复切换功能 -->
            <Tooltip content="知识库">
              <button
                class="btn-secondary flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ease-in-out"
                :class="{
                    'text-gray-500 dark:text-gray-300 hover:text-primary': uiStore.activePanel !== 'rag',
                    'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/40': uiStore.activePanel === 'rag'
                  }"
                @click="toggleKnowledgeBase"
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
            <!-- 智能体启动按钮 -->
            <Tooltip content="智能体">
              <button
                class="btn-secondary flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ease-in-out"
                :class="{
                    'text-gray-500 dark:text-gray-300 hover:text-primary': !isAgentEnabled,
                    'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/40': isAgentEnabled
                  }"
                @click="toggleAgent"
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
              class="flex items-center justify-center text-black bg-white hover:bg-gray-100 border border-gray-300 rounded-lg transition-all duration-300 ease-in-out hover:scale-105 h-8 px-2 text-xs"
            @click="handleSendMessage"
          >
            <span>Enter</span>
            <span class="ml-1">↵</span>
          </button>
          <Tooltip v-else content="终止输出">
            <button
              class="flex items-center justify-center text-black bg-white hover:bg-gray-100 border border-gray-300 rounded-lg transition-all duration-300 ease-in-out hover:scale-105 h-8 px-2 text-xs"
              @click="handleCancelStreaming"
            >
              <i class="fa-solid fa-circle-notch fa-spin mr-1"></i>
              <span>Stop</span>
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
import { useRouter } from 'vue-router';
import { StorageManager } from '../../../utils/storage.js';
import { formatFileSize } from '../../../utils/file.js';
import { Tooltip } from '../index.js';
import { showNotification } from '../../../utils/notificationUtils.js';
import DragDropZone from '../../common/DragDropZone.vue';
import { Button } from '../../../components/library/index.js';

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
import { useChatStore } from '../../../store/chatStore.js';
import { useSettingsStore } from '../../../store/settingsStore.js';
import { useUiStore } from '../../../store/uiStore.js';
import { useVectorStore } from '../../../store/vectorStore.js';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();
const uiStore = useUiStore();
const modelStore = useSettingsStore();
const vectorStore = useVectorStore();

// 初始化路由
const router = useRouter();

// 拖拽状态管理
const dragCounter = ref(0);
const isDragOver = ref(false);

// 使用ref引用DOM元素
const fileInput = ref(null);
const modelDropdown = ref(null);
const agentDropdown = ref(null);

// 本地UI状态
const showModelDropdown = ref(false);
const showAgentDropdown = ref(false);
const showParamsPanel = ref(false);
// 新增状态：检查是否有活动的流式输出
const hasActiveStreaming = ref(false);
// 用户菜单状态
const showUserMenu = ref(false);
// 命令行窗口状态
const showCommandLine = ref(false);
// 分页状态
const currentPage = ref(0);
// RAG模式状态 - 从settingsStore获取
const _isRagMode = computed(() => uiStore.activePanel === 'rag');

// 分页方法
const prevPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--;
  }
};

const nextPage = () => {
  if (currentPage.value < 1) {
    currentPage.value++;
  }
};

// 从uiStore获取功能按钮状态
const isDeepThinking = computed(() => uiStore.isDeepThinking);
const isWebSearchEnabled = computed(() => uiStore.isWebSearchEnabled);
const isAgentEnabled = computed(() => uiStore.isAgentEnabled);

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

// 从store获取模型参数
const modelParams = computed(() => modelStore.currentModelParams);



// 切换深度思考模式
const toggleDeepThinking = () => {
  uiStore.toggleDeepThinking();
};

// 切换联网搜索模式
const toggleWebSearch = () => {
  uiStore.toggleWebSearch();
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
  if (!currentModel.value || !modelStore.allModels.length) {
    return currentModel.value || settingsStore.systemSettings.defaultModel || '默认模型';
  }
  
  // 遍历所有模型，找到匹配的模型
  for (const model of modelStore.allModels) {
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
  
  if (!modelStore.allModels.length) {
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
    for (const model of modelStore.allModels) {
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

// 获取可用模型列表，确保始终返回数组
const availableModels = computed(() => modelStore.availableModelList || []);

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
// 计算属性：消息输入框内容
const messageInput = computed({
  get: () => uiStore.messageInput,
  set: (value) => uiStore.updateMessageInput(value),
});

// 从store直接获取响应式数据
const uploadedFiles = computed(() => chatStore.uploadedFiles);

// 定义事件
const emit = defineEmits(['messageSubmitted']);

// 处理发送消息事件
const handleSendMessage = async () => {
  if (messageInput.value.trim() || uploadedFiles.value.length > 0) {
    // 先保存当前需要发送的消息内容和模型
    const messageToSend = messageInput.value;
    const modelToUse = currentModel.value;
    const deepThinking = isDeepThinking.value;
    const webSearchEnabled = isWebSearchEnabled.value;
    const agent = isAgentEnabled.value; // 根据当前状态设置agent字段
    
    // 立即发送消息，不等待Ollama服务检查
    emit('messageSubmitted', messageToSend, modelToUse, deepThinking, webSearchEnabled, agent);
    // 发送消息后立即检查是否有流式输出
    checkForActiveStreaming();
    
    // 如果是Ollama模型，在后台异步检查和启动服务
    if (modelToUse.includes('Ollama')) {
      // 使用setTimeout将检查操作放入事件队列，避免阻塞UI
      setTimeout(async () => {
        try {
          // 这里可以通过 API 调用 Python 后端来检查和启动 Ollama 服务
          // 暂时显示提示信息
          showNotification('Ollama服务检查功能已迁移到 Python 后端', 'info', 3000);
        } catch (error) {
          console.error('Ollama服务管理失败:', error);
          // 显示更具体的错误信息
          showNotification(`Ollama服务管理失败: ${error.message || error}`, 'error', 3000);
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
    currentModel.value = chatStore.currentChat?.model || settingsStore.systemSettings.defaultModel || modelStore.currentSelectedModel;
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
  () => modelStore.allModels,
  () => {
    // 模型列表更新后，如果当前模型无效或为空，重新设置当前模型
    if (!currentModel.value || !availableModels.value.includes(currentModel.value)) {
      currentModel.value = chatStore.currentChat?.model || settingsStore.systemSettings.defaultModel || modelStore.availableModelList[0];
    }
  },
  { deep: true }
);

// 监听可用模型列表变化，更新当前模型
watch(
  () => modelStore.availableModelList,
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
  modelStore.updateModelParams({ temperature: parseFloat(event.target.value) });
};

// 处理Top-p参数变化
const handleTopPChange = (event) => {
  modelStore.updateModelParams({ top_p: parseFloat(event.target.value) });
};

// 处理Top-k参数变化
const handleTopKChange = (event) => {
  modelStore.updateModelParams({ top_k: parseInt(event.target.value) });
};

// 处理最大长度参数变化
const handleMaxLengthChange = (event) => {
  modelStore.updateModelParams({ max_tokens: parseInt(event.target.value) });
};

// 处理检索相关性阈值变化
const handleThresholdChange = (event) => {
  vectorStore.updateRetrievalConfig({ threshold: parseFloat(event.target.value) });
};

// 处理检索文档数量变化
const handleRetrievalTopKChange = (event) => {
  vectorStore.updateRetrievalConfig({ topK: parseInt(event.target.value) });
};

// 处理检索模式变化
const handleRetrievalModeSliderChange = (event) => {
  const modeValue = parseInt(event.target.value);
  let mode;
  switch (modeValue) {
    case 0:
      mode = 'vector';
      break;
    case 1:
      mode = 'keyword';
      break;
    case 2:
      mode = 'hybrid';
      break;
    default:
      mode = 'vector';
  }
  vectorStore.updateRetrievalConfig({ mode });
};

// 获取检索模式的滑块值
const getRetrievalModeValue = (mode) => {
  const modeMap = {
    vector: 0,
    keyword: 1,
    hybrid: 2
  };
  return modeMap[mode] || 0;
};

// 获取检索模式的显示文本
const getRetrievalModeDisplay = (mode) => {
  const modeMap = {
    vector: '向量检索',
    keyword: '关键词检索',
    hybrid: '混合检索'
  };
  return modeMap[mode] || mode;
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
  if (uiStore.activePanel === 'mcp') {
    // 如果当前是MCP面板，切换回之前的面板
    uiStore.setActivePanel(uiStore.previousPanel || 'history');
  } else {
    // 如果当前不是MCP面板，保存当前面板并切换到MCP面板
    uiStore.previousPanel = uiStore.activePanel;
    uiStore.setActivePanel('mcp');
  }
};

// 切换智能体状态
const toggleAgent = () => {
  uiStore.toggleAgent();
};

// 切换知识库状态
const toggleKnowledgeBase = () => {
  if (uiStore.activePanel === 'rag') {
    // 如果当前是知识库模式，切换回聊天模式
    uiStore.setActivePanel('history');
    
    // 主显示区：如果没有聊天消息，显示sendMessage视图，否则显示chat视图
    const hasMessages = chatStore.currentChatMessages && chatStore.currentChatMessages.length > 0;
    uiStore.setActiveContent(hasMessages ? 'chat' : 'home');
    
    // 关闭RAG功能
    vectorStore.setRagConfig({ enabled: false });
  } else {
    // 如果当前不是知识库模式，切换到知识库模式
    uiStore.setActivePanel('rag');
    
    // 启用RAG功能
    vectorStore.setRagConfig({ enabled: true });
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
};

// 生命周期钩子
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  // 添加点击外部区域关闭用户菜单的事件监听
  document.addEventListener('click', closeMenusOnClickOutside);
  
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

// 处理视图按钮点击事件 - 切换右侧面板
const toggleViewPanel = () => {
  uiStore.toggleRightPanel();
};

// 处理系统设置按钮点击事件
const handleSystemSettingsClick = () => {
  router.push('/setting');
};

// 处理AI配置按钮点击事件
const handleAISettingsClick = () => {
  router.push('/setting');
};

// 切换主题
const handleToggleTheme = () => {
  settingsStore.toggleDarkMode();
};

// 切换用户菜单显示状态
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

// 处理切换账户点击
const handleSwitchAccount = () => {
  showUserMenu.value = false;
  console.log('切换账户');
};

// 处理退出账号点击
const handleLogout = () => {
  showUserMenu.value = false;
  showNotification('退出账号功能待实现', 'info');
};

// 关闭命令行窗口
const closeCommandLine = () => {
  showCommandLine.value = false;
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
    showUserMenu.value = false;
  }
};

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  document.removeEventListener('click', closeMenusOnClickOutside);
});

// 处理文件拖放
const handleDrop = (files) => {
  dragCounter.value = 0;
  isDragOver.value = false;
  if (files && files.length > 0) {
    handleFileUpload(files);
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

/* 下拉菜单动画 */
.dropdown-content {
  animation: fadeInDown 0.2s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translate(-50%, -10px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>