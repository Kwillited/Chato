<template>
  <div class="text-gray-900 min-h-screen flex flex-col items-center">
    <!-- Main Content -->
    <main class="w-full px-6 py-8">
      <!-- =======================
           VIEW 1: 基本设置
           ======================= -->
      <div v-if="activeTab === 'basic'" class="max-w-5xl mx-auto dark:bg-dark-primary">
        <div class="flex flex-col md:flex-row gap-6 items-stretch">
          <!-- 左侧：个人信息设置区 -->
          <div class="w-full md:w-1/3 space-y-6">
            <!-- 用户信息卡片 -->
            <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800 h-full">
              <!-- 头像 -->
              <div class="flex flex-col items-center mb-4">
                <img src="https://picsum.photos/id/64/100/100" alt="用户头像" class="w-20 h-20 rounded-full mb-4 border-2 border-white shadow-sm">
                <button class="text-xs text-blue-600 dark:text-blue-400 hover:underline">更换头像</button>
              </div>
              
              <!-- 个人信息 -->
              <div class="space-y-4">
                <!-- 用户名 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">用户名</label>
                  <input type="text" value="Administrator" class="w-full text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white">
                </div>
                
                <!-- 邮箱 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">邮箱</label>
                  <input type="email" value="Administrator@example.com" class="w-full text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white">
                </div>
                
                <!-- 密码修改 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">密码</label>
                  <input type="password" placeholder="••••••••" class="w-full text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white">
                  <button class="mt-1 text-xs text-blue-600 dark:text-blue-400 hover:underline">修改密码</button>
                </div>
                
                <!-- 保存按钮 -->
                <button class="w-full py-2 px-3 bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors">保存个人信息</button>
                
                <!-- 历史会话操作按钮 -->
                <div class="flex gap-2 justify-center mt-4">
                  <!-- 导出所有对话按钮 -->
                  <button
                    id="exportAllBtn"
                    class="h-8 w-8 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-blue-400 transition-colors duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-dark-700"
                    @click="chatStore.exportAllChats"
                    title="导出所有对话"
                  >
                    <i class="fa-solid fa-download text-sm"></i>
                  </button>
                  <!-- 删除所有对话按钮 -->
                  <button
                    id="deleteAllBtn"
                    class="h-8 w-8 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-red-500 dark:hover:text-red-400 transition-colors duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-dark-700"
                    @click="handleDeleteAllChats"
                    title="删除所有对话"
                  >
                    <i class="fa-solid fa-trash-can text-sm"></i>
                  </button>
                </div>
              </div>
            </div>
            

          </div>
          
          <!-- 右侧：功能调整区 -->
          <div class="w-full md:w-2/3 space-y-4">
            <!-- 第一行：对话相关设置 -->
            <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
              <h3 class="font-medium text-sm text-gray-900 dark:text-white mb-4">对话设置</h3>
              
              <div class="space-y-4">
                <!-- 启用流式输出 -->
                <div class="flex justify-between items-center">
                  <div>
                    <div class="font-medium text-sm text-gray-900 dark:text-white">启用流式输出</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">启用后，对话将以流式方式输出，而不是等待全部生成完成</div>
                  </div>
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="settingsStore.systemSettings.streamingEnabled" @change="settingsStore.saveSettings()">
                    <span class="toggle-slider bg-gray-300 dark:bg-dark-600"></span>
                  </label>
                </div>
                
                <!-- 默认模型 -->
                <div>
                  <div class="font-medium text-sm text-gray-900 dark:text-white mb-2">默认模型</div>
                  <select class="w-full text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white" v-model="settingsStore.systemSettings.defaultModel" @change="settingsStore.setDefaultModel(settingsStore.systemSettings.defaultModel)">
                    <option disabled="" value="">选择默认模型</option>
                    <option value="Ollama-qwen3:0.6b">Ollama-1</option>
                  </select>
                </div>
              </div>
            </div>
            
            <!-- 第二行：外观相关设置 -->
            <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
              <h3 class="font-medium text-sm text-gray-900 dark:text-white mb-4">外观设置</h3>
              
              <div class="space-y-4">
                <!-- 深色模式 -->
                <div class="flex justify-between items-center">
                  <div>
                    <div class="font-medium text-sm text-gray-900 dark:text-white">深色模式</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">启用后，界面将切换到深色主题，减轻夜间使用时的视觉疲劳</div>
                  </div>
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="settingsStore.systemSettings.darkMode" @change="settingsStore.saveSettings(); settingsStore.applyDarkMode()">
                    <span class="toggle-slider bg-gray-300 dark:bg-dark-600"></span>
                  </label>
                </div>
                
                <!-- 对话样式 -->
                <div>
                  <div class="font-medium text-sm text-gray-900 dark:text-white mb-2">对话样式</div>
                  <div class="flex gap-3">
                    <button class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-100 dark:hover:bg-dark-600" :class="{ 'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-700 text-gray-700 dark:text-gray-300': settingsStore.systemSettings.chatStyleDocument, 'border-blue-600 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 active': !settingsStore.systemSettings.chatStyleDocument }" @click="settingsStore.updateSystemSettings({ chatStyleDocument: false })">
                      <i class="fa-regular fa-comment mr-2"></i> 气泡模式
                    </button>
                    <button class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-100 dark:hover:bg-dark-600" :class="{ 'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-700 text-gray-700 dark:text-gray-300': !settingsStore.systemSettings.chatStyleDocument, 'border-blue-600 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 active': settingsStore.systemSettings.chatStyleDocument }" @click="settingsStore.updateSystemSettings({ chatStyleDocument: true })">
                      <i class="fa-regular fa-file-lines mr-2"></i> 文档样式
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 第三行：文件相关设置 -->
            <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
              <h3 class="font-medium text-sm text-gray-900 dark:text-white mb-4">文件设置</h3>
              
              <div>
                <div class="font-medium text-sm text-gray-900 dark:text-white mb-2">文件视图模式</div>
                <div class="flex gap-3">
                  <button class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-100 dark:hover:bg-dark-600" :class="{ 'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-700 text-gray-700 dark:text-gray-300': settingsStore.systemSettings.viewMode !== 'grid', 'border-blue-600 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 active': settingsStore.systemSettings.viewMode === 'grid' }" @click="settingsStore.updateSystemSettings({ viewMode: 'grid' })">
                    <i class="fa-regular fa-th mr-2"></i> 网格视图
                  </button>
                  <button class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-100 dark:hover:bg-dark-600" :class="{ 'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-700 text-gray-700 dark:text-gray-300': settingsStore.systemSettings.viewMode !== 'list', 'border-blue-600 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 active': settingsStore.systemSettings.viewMode === 'list' }" @click="settingsStore.updateSystemSettings({ viewMode: 'list' })">
                    <i class="fa-regular fa-list mr-2"></i> 列表视图
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- =======================
           VIEW 2: 模型配置
           ======================= -->
      <div v-if="activeTab === 'models'" class="grid grid-cols-1 lg:grid-cols-3 gap-12 dark:bg-dark-primary">
        <!-- LEFT (2/3): Configured Providers (Merged View) -->
        <div class="lg:col-span-2 space-y-8">
          <div class="flex justify-between items-end pb-2 border-b border-gray-100">
            <h2 class="text-xs font-bold text-gray-400 uppercase tracking-widest">活跃供应商</h2>
          </div>

          <!-- Provider Card Template -->
          <div v-for="provider in configuredProviders" :key="provider.id" class="group border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800 transition-all hover:border-gray-400 dark:hover:border-gray-500 overflow-hidden">
            <!-- Card Header: Provider Identity -->
            <div @click="toggleProviderOpen(provider.name)" class="px-5 py-4 flex items-center justify-between cursor-pointer select-none bg-gray-50/30 dark:bg-dark-700/30 hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded border border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-800 flex items-center justify-center text-sm font-bold dark:text-white">{{ provider.name.charAt(0) }}</div>
                <div>
                  <h3 class="font-semibold text-sm text-gray-900 dark:text-white">{{ provider.name }}</h3>
                  <div class="text-[10px] text-gray-500 dark:text-gray-400 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                    已连接
                    <span class="text-gray-300 dark:text-gray-600">|</span>
                    <span>{{ provider.models.length }}</span> 个模型已映射
                  </div>
                </div>
              </div>
              <svg class="w-4 h-4 text-gray-400 dark:text-gray-500 transform transition-transform" :class="provider.open ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>

            <!-- Expandable Body -->
            <div v-if="provider.open" :class="{ open: provider.open }">
              <!-- 1. 凭证部分 (所有模型共享) -->
              <div class="px-5 py-5 grid grid-cols-2 gap-6 hairline-b dark:border-dark-700">
                <div class="col-span-2 md:col-span-1">
                  <label class="block text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1.5">基础 URL</label>
                  <div class="flex gap-2">
                    <input type="text" v-model="provider.apiBaseUrl" class="w-full h-8 text-xs mono bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded px-2.5 py-2 outline-none focus:border-black dark:focus:border-white transition-colors text-gray-900 dark:text-white">
                  </div>
                </div>
                <div class="col-span-2 md:col-span-1">
                  <label class="block text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1.5">API 密钥</label>
                  <div class="flex gap-2">
                    <input type="password" v-model="provider.apiKey" class="w-full h-8 text-xs mono bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded px-2.5 py-2 outline-none focus:border-black dark:focus:border-white transition-colors text-gray-900 dark:text-white">
                    <button class="px-3 h-8 border border-gray-200 dark:border-dark-600 rounded bg-white dark:bg-dark-700 hover:bg-gray-50 dark:hover:bg-dark-600 text-[10px] font-medium text-gray-900 dark:text-white transition-colors flex items-center justify-center">更新</button>
                  </div>
                </div>
              </div>

              <!-- 2. 模型清单 -->
              <div class="px-5 py-4">
                <div class="flex items-center justify-between mb-3">
                  <span class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase">模型清单</span>
                  <button @click="toggleModelForm(provider)" class="text-[10px] font-medium text-blue-600 dark:text-blue-400 hover:underline">+ 映射新模型</button>
                </div>
                
                <!-- 模型映射表单 - 水平布局 -->
                <div v-if="isModelFormVisible && editingProvider?.name === provider.name" class="mb-4 p-3 bg-gray-50 dark:bg-dark-700 rounded-lg border border-gray-200 dark:border-dark-600">
                  <div class="flex flex-wrap items-end gap-3">
                    <!-- 模型类型 -->
                    <div class="min-w-[120px]">
                      <label class="block text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1.5">模型类型</label>
                      <select v-model="newModel.type" class="w-full text-xs bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded px-2.5 py-1.5 outline-none focus:border-primary dark:focus:border-primary transition-colors text-gray-900 dark:text-white">
                        <option value="llm">聊天补全</option>
                        <option value="embed">嵌入</option>
                      </select>
                    </div>
                    <!-- 模型ID -->
                    <div class="flex-1 min-w-[120px]">
                      <label class="block text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1.5">模型ID</label>
                      <input type="text" v-model="newModel.id" class="w-full text-xs bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded px-2.5 py-1.5 outline-none focus:border-primary dark:focus:border-primary transition-colors text-gray-900 dark:text-white" placeholder="例如：gpt-4o">
                    </div>
                    <!-- 自定义模型名字 -->
                    <div class="flex-1 min-w-[120px]">
                      <label class="block text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1.5">自定义模型名字</label>
                      <input type="text" v-model="newModel.customName" class="w-full text-xs bg-gray-100 dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded px-2.5 py-1.5 outline-none focus:border-primary dark:focus:border-primary transition-colors text-gray-900 dark:text-white" placeholder="例如：我的GPT-4o">
                    </div>
                    <!-- 流式输出配置 -->
                    <div class="min-w-[120px] flex items-center justify-between">
                      <label class="block text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1.5">流式输出</label>
                      <label class="toggle-switch">
                        <input type="checkbox" v-model="newModel.streamingConfig">
                        <span class="toggle-slider bg-gray-300 dark:bg-dark-600"></span>
                      </label>
                    </div>
                    <!-- 表单按钮 -->
                    <div class="flex gap-2">
                      <button @click="saveModelMapping()" class="text-xs bg-primary hover:bg-primary/90 text-white rounded px-3 py-1.5 transition-colors whitespace-nowrap">保存</button>
                      <button @click="cancelModelMapping()" class="text-xs bg-gray-200 dark:bg-dark-600 hover:bg-gray-300 dark:hover:bg-dark-500 text-gray-900 dark:text-white rounded px-3 py-1.5 transition-colors whitespace-nowrap">取消</button>
                    </div>
                  </div>
                </div>
                
                <table class="w-full text-left border-collapse">
                  <tbody class="divide-y divide-gray-100 dark:divide-dark-700">
                    <tr v-for="model in provider.models" :key="model.id" class="group/row hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors">
                      <!-- Icon / Type -->
                      <td class="py-2.5 pr-3 w-8">
                        <div class="w-6 h-6 rounded flex items-center justify-center border text-[10px] font-bold"
                             :class="model.type === 'llm' ? 'bg-white dark:bg-dark-700 border-gray-200 dark:border-dark-600 text-gray-600 dark:text-gray-300' : 'bg-purple-50 dark:bg-purple-900/30 border-purple-100 dark:border-purple-800 text-purple-600 dark:text-purple-400'">
                          <span>{{ model.type === 'llm' ? 'T' : 'E' }}</span>
                        </div>
                      </td>
                      <!-- Model ID -->
                      <td class="py-2.5">
                        <div class="text-xs font-medium text-gray-900 dark:text-white">{{ model.customName || model.id }}</div>
                        <div class="text-[10px] text-gray-400 dark:text-gray-500">{{ model.type === 'llm' ? '聊天补全' : '嵌入' }}</div>
                      </td>
                      
                      <!-- Actions Columns (紧凑排列) -->
                      <td class="py-2.5 w-12 text-right pr-1">
                        <label class="relative inline-block w-7 h-3.5 align-middle select-none cursor-pointer">
                        <input type="checkbox" v-model="model.active" class="toggle-checkbox absolute block w-3.5 h-3.5 rounded-full bg-white border-2 border-gray-300 dark:border-dark-600 appearance-none cursor-pointer transition-all duration-300 top-0 left-0"/>
                        <span class="toggle-label block overflow-hidden h-3.5 rounded-full bg-gray-200 dark:bg-dark-700 cursor-pointer"></span>
                      </label>
                      </td>
                      <td class="py-2.5 w-8 text-right pr-0">
                        <button @click="editModelMapping(provider, model)" class="text-[10px] text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors">
                          <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                      </td>
                      <td class="py-2.5 w-8 text-right pl-0 pr-2">
                        <button @click="deleteModelMapping(provider, model)" class="text-[10px] text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors">
                          <i class="fa-solid fa-trash"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <!-- Footer -->
              <div class="bg-gray-50 dark:bg-dark-700 px-5 py-2 border-t border-gray-100 dark:border-dark-800 flex justify-end">
                <button @click="removeProvider(provider)" class="text-[10px] text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium">移除供应商</button>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT (1/3): 可用供应商 (市场) -->
        <div class="lg:col-span-1">
          <div class="sticky top-24 space-y-6">
            <div class="flex justify-between items-end pb-2 border-b border-gray-100 dark:border-dark-700">
              <h2 class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest">添加供应商</h2>
              <span class="text-[10px] text-gray-400 dark:text-gray-500">拖拽或点击</span>
            </div>

            <div class="grid grid-cols-1 gap-3">
              <button v-for="p in availableProviders" :key="p.name" @click="addProvider(p)" class="flex items-center gap-3 w-full p-3 rounded-lg border border-dashed border-gray-300 bg-white text-left hover:bg-gray-100 hover:border-solid hover:border-black hover:shadow-md transition-all cursor-pointer">
                <div class="w-8 h-8 rounded bg-white border border-gray-200 flex items-center justify-center text-xs font-bold">
                  {{ p.name.charAt(0) }}
                </div>
                <div style="min-width: 0; flex: 1;">
                  <div style="font-size: 0.75rem; font-weight: 600; color: #1f2937; display: block !important;">
                    {{ p.name }}
                  </div>
                  <div style="font-size: 0.625rem; color: #6b7280; display: block !important; margin-top: 0.125rem;">
                    {{ p.desc }}
                  </div>
                </div>
                <span style="font-size: 1.125rem; font-weight: 300; color: #6b7280;">+</span>
              </button>
              
              <button class="w-full py-3 text-xs font-medium text-gray-400 border border-transparent hover:text-black transition-colors text-center">
                找不到供应商？配置自定义供应商
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- =======================
           VIEW 2: MCP 工具
           ======================= -->
      <div v-if="activeTab === 'mcp'" class="max-w-5xl mx-auto dark:bg-dark-primary">

        <div class="space-y-4">
          <!-- MCP Server Item: Filesystem -->
          <div class="border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800 p-5 flex flex-col md:flex-row md:items-center gap-6 hover:border-gray-400 dark:hover:border-gray-500 transition-colors group">
            <!-- Icon -->
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-gray-100 dark:bg-dark-700 rounded-lg flex items-center justify-center text-gray-600 dark:text-gray-300">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z"></path></svg>
              </div>
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 mb-1">
                <h3 class="font-bold text-sm text-gray-900 dark:text-white">本地文件系统</h3>
                <span class="px-1.5 py-0.5 rounded bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-[10px] font-mono font-bold border border-green-100 dark:border-green-800">STDIO</span>
                <span class="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-dark-700 text-gray-600 dark:text-gray-300 text-[10px] font-mono border border-gray-200 dark:border-dark-600">活跃</span>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-mono truncate">command: npx -y @modelcontextprotocol/server-filesystem</p>
              
              <!-- Tool Chips -->
              <div class="flex flex-wrap gap-2 mt-3">
                <span class="text-[10px] bg-gray-50 dark:bg-dark-700 border border-gray-100 dark:border-dark-600 px-2 py-1 rounded text-gray-600 dark:text-gray-300">read_file</span>
                <span class="text-[10px] bg-gray-50 dark:bg-dark-700 border border-gray-100 dark:border-dark-600 px-2 py-1 rounded text-gray-600 dark:text-gray-300">write_file</span>
                <span class="text-[10px] bg-gray-50 dark:bg-dark-700 border border-gray-100 dark:border-dark-600 px-2 py-1 rounded text-gray-600 dark:text-gray-300">list_directory</span>
              </div>
            </div>

            <!-- Action -->
            <div class="flex flex-row md:flex-col items-center gap-3 border-t md:border-t-0 md:border-l border-gray-100 dark:border-dark-700 pt-4 md:pt-0 md:pl-6">
              <button class="text-xs font-semibold text-gray-900 dark:text-white hover:underline">配置</button>
              <label class="relative inline-block w-8 h-4 align-middle select-none cursor-pointer">
                <input type="checkbox" checked class="toggle-checkbox absolute block w-4 h-4 rounded-full bg-white border-2 border-gray-300 dark:border-dark-600 appearance-none cursor-pointer top-0 left-0"/>
                <span class="toggle-label block overflow-hidden h-4 rounded-full bg-gray-200 dark:bg-dark-700 cursor-pointer"></span>
              </label>
            </div>
          </div>

          <!-- MCP Server Item: GitHub -->
          <div class="border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800 p-5 flex flex-col md:flex-row md:items-center gap-6 hover:border-gray-400 dark:hover:border-gray-500 transition-colors group">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-black text-white rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" /></svg>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 mb-1">
                <h3 class="font-bold text-sm text-gray-900 dark:text-white">GitHub 集成</h3>
                <span class="px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-[10px] font-mono font-bold border border-blue-100 dark:border-blue-800">SSE</span>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-mono truncate">url: https://mcp-proxy.github.com/v1</p>
              <div class="flex flex-wrap gap-2 mt-3">
                <span class="text-[10px] bg-gray-50 dark:bg-dark-700 border border-gray-100 dark:border-dark-600 px-2 py-1 rounded text-gray-600 dark:text-gray-300">create_issue</span>
                <span class="text-[10px] bg-gray-50 dark:bg-dark-700 border border-gray-100 dark:border-dark-600 px-2 py-1 rounded text-gray-600 dark:text-gray-300">pr_review</span>
              </div>
            </div>
            <div class="flex flex-row md:flex-col items-center gap-3 border-t md:border-t-0 md:border-l border-gray-100 dark:border-dark-700 pt-4 md:pt-0 md:pl-6">
              <button class="text-xs font-semibold text-gray-900 dark:text-white hover:underline">配置</button>
              <label class="relative inline-block w-8 h-4 align-middle select-none cursor-pointer">
                <input type="checkbox" class="toggle-checkbox absolute block w-4 h-4 rounded-full bg-white border-2 border-gray-300 dark:border-dark-600 appearance-none cursor-pointer top-0 left-0"/>
                <span class="toggle-label block overflow-hidden h-4 rounded-full bg-gray-200 dark:bg-dark-700 cursor-pointer"></span>
              </label>
            </div>
          </div>

          <!-- 添加新服务器 -->
          <button class="w-full border-2 border-dashed border-gray-200 dark:border-dark-600 rounded-xl p-4 flex items-center justify-center gap-2 text-gray-400 dark:text-gray-500 hover:text-black dark:hover:text-white hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-dark-700 transition-all">
            <span class="text-sm font-semibold">+ 连接新的 MCP 服务器</span>
          </button>
        </div>
      </div>

      <!-- =======================
           VIEW 5: 知识库配置
           ======================= -->
      <div v-if="activeTab === 'knowledge'" class="max-w-5xl mx-auto dark:bg-dark-primary">
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Embedder模型卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">Embedder模型</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">用于将文本转换为向量的模型</div>
            </div>
            <!-- 内容区域 -->
            <div class="relative">
              <select class="w-full text-sm px-2 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white" v-model="settingsStore.vectorConfig.embedding.model" @change="settingsStore.updateVectorEmbeddingConfig(settingsStore.vectorConfig.embedding)">
                <option value="qwen3-embedding-0.6b">qwen3-embedding-0.6b (推荐)</option>
                <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2 (轻量)</option>
                <option value="all-mpnet-base-v2">all-mpnet-base-v2 (更精确)</option>
                <option value="all-MiniLM-L12-v2">all-MiniLM-L12-v2 (平衡)</option>
              </select>
            </div>
          </div>
          
          <!-- 向量数据库类型卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">向量数据库类型</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">使用的向量数据库类型</div>
            </div>
            <!-- 内容区域 -->
            <div class="relative">
              <select class="w-full text-sm px-2 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white" v-model="settingsStore.vectorConfig.storage.type" @change="settingsStore.updateVectorStorageConfig(settingsStore.vectorConfig.storage)">
                <option value="chroma">Chroma (默认)</option>
              </select>
            </div>
          </div>
          
          <!-- 文档检索模式卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">文档检索模式</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">设置知识库的文档检索方式</div>
            </div>
            <!-- 内容区域 -->
            <div class="relative">
              <select class="w-full text-sm px-2 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white" v-model="settingsStore.vectorConfig.retrieval.mode" @change="settingsStore.updateVectorRetrievalConfig(settingsStore.vectorConfig.retrieval)">
                <option value="vector">向量检索</option>
                <option value="keyword">关键词检索</option>
                <option value="hybrid">混合检索</option>
              </select>
            </div>
          </div>
          
          <!-- 检索文档数量卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">检索文档数量</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">每次查询返回的文档数量</div>
            </div>
            <!-- 内容区域 -->
            <div class="relative">
              <input type="number" class="w-full text-sm px-2 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white" placeholder="例如：3" min="1" max="20" v-model.number="settingsStore.vectorConfig.retrieval.topK" @change="settingsStore.updateVectorRetrievalConfig(settingsStore.vectorConfig.retrieval)">
            </div>
          </div>
          
          <!-- 检索相关性阈值卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800 md:col-span-2">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">检索相关性阈值</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">文档相关性的最低分数要求</div>
            </div>
            <!-- 内容区域 -->
            <div class="relative">
              <input type="number" class="w-full text-sm px-2 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white" placeholder="例如：0.7" step="0.05" min="0" max="1" v-model.number="settingsStore.vectorConfig.retrieval.threshold" @change="settingsStore.updateVectorRetrievalConfig(settingsStore.vectorConfig.retrieval)">
            </div>
          </div>
          
          <!-- 向量数据库路径卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800 md:col-span-2">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">向量数据库路径</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">向量数据的存储位置（留空使用系统默认路径）</div>
            </div>
            <!-- 内容区域 -->
            <div class="relative">
              <input type="text" class="w-full text-sm px-2 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white" placeholder="留空使用默认路径" v-model="settingsStore.vectorConfig.storage.path" @change="settingsStore.updateVectorStorageConfig(settingsStore.vectorConfig.storage)">
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">系统默认路径: 用户数据目录下的 "Retrieval-Augmented Generation\vectorDb"</div>
            </div>
          </div>
          
          <!-- 知识库存储路径卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800 md:col-span-2">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">知识库存储路径</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">知识库文档文件的存储位置（留空使用系统默认路径）</div>
            </div>
            <!-- 内容区域 -->
            <div class="relative">
              <input type="text" class="w-full text-sm px-2 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white" placeholder="留空使用默认路径" v-model="settingsStore.vectorConfig.storage.knowledgeBasePath" @change="settingsStore.updateVectorStorageConfig(settingsStore.vectorConfig.storage)">
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">系统默认路径: 用户数据目录下的 "Retrieval-Augmented Generation\knowledgeBase"</div>
            </div>
          </div>
        </div>
      </div>

      <!-- =======================
           VIEW 6: 通知设置
           ======================= -->
      <div v-if="activeTab === 'notifications'" class="max-w-4xl mx-auto dark:bg-dark-primary">
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 新消息通知卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">新消息通知</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">当收到AI回复时通知</div>
            </div>
            <!-- 内容区域 -->
            <div class="flex justify-between items-center">
              <!-- 开关 -->
              <label class="toggle-switch">
                <input type="checkbox" v-model="settingsStore.notificationsConfig.newMessage" @change="settingsStore.updateNotificationsConfig(settingsStore.notificationsConfig)">
                <span class="toggle-slider bg-gray-300 dark:bg-dark-600"></span>
              </label>
            </div>
          </div>
          
          <!-- 声音提示卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">声音提示</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">新消息通知时播放提示音</div>
            </div>
            <!-- 内容区域 -->
            <div class="flex justify-between items-center">
              <!-- 开关 -->
              <label class="toggle-switch">
                <input type="checkbox" v-model="settingsStore.notificationsConfig.sound" @change="settingsStore.updateNotificationsConfig(settingsStore.notificationsConfig)">
                <span class="toggle-slider bg-gray-300 dark:bg-dark-600"></span>
              </label>
            </div>
          </div>
          
          <!-- 系统通知卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">系统通知</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">显示应用更新等系统通知</div>
            </div>
            <!-- 内容区域 -->
            <div class="flex justify-between items-center">
              <!-- 开关 -->
              <label class="toggle-switch">
                <input type="checkbox" v-model="settingsStore.notificationsConfig.system" @change="settingsStore.updateNotificationsConfig(settingsStore.notificationsConfig)">
                <span class="toggle-slider bg-gray-300 dark:bg-dark-600"></span>
              </label>
            </div>
          </div>
          
          <!-- 通知显示时间卡片 -->
          <div class="card p-5 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800">
            <!-- 标题和描述 -->
            <div class="mb-3">
              <div class="font-medium text-sm text-gray-900 dark:text-white">通知显示时间</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">控制通知在屏幕上停留的时间</div>
            </div>
            <!-- 内容区域 -->
            <div class="relative">
                <select class="w-full text-sm px-2 py-2 focus:outline-none focus:ring-1 focus:ring-blue-600 dark:focus:ring-blue-400 bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white" v-model="settingsStore.notificationsConfig.displayTime" @change="settingsStore.updateNotificationsConfig(settingsStore.notificationsConfig)">
                  <option value="2秒">2秒</option>
                  <option value="5秒">5秒</option>
                  <option value="10秒">10秒</option>
                </select>
              </div>
          </div>
        </div>
      </div>

      <!-- =======================
           VIEW 7: 关于
           ======================= -->
      <div v-if="activeTab === 'about'" class="max-w-5xl mx-auto dark:bg-dark-primary flex justify-center items-center min-h-[calc(100vh-160px)]">

        
        <div class="space-y-6 w-full">
          <!-- 关于应用内容 - 左右布局 -->
          <div class="flex flex-col items-center gap-6">
            <!-- 左右布局容器 -->
            <div class="flex flex-col md:flex-row gap-6 w-full">
              <!-- 左侧：应用图标/版本 + 关于描述 -->
              <div class="w-full md:w-1/2 space-y-6 flex flex-col justify-center">
                <!-- 应用图标和版本信息 -->
              <div class="space-y-4 flex flex-col items-center">
                <div class="w-20 h-20 bg-blue-50 dark:bg-blue-900/20 rounded-full flex items-center justify-center shadow-sm hover:scale-105 transition-transform">
                  <i class="fa-regular fa-comments text-blue-600 dark:text-blue-400 text-3xl"></i>
                </div>
                <h3 class="font-semibold text-xl text-gray-900 dark:text-white">Chato</h3>
                <div class="text-sm text-gray-500 dark:text-gray-400">版本 v1.0.0</div>
              </div>
                
                <!-- 关于应用描述 -->
                <div class="card shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 dark:border-dark-700 rounded-xl bg-white dark:bg-dark-800 p-6">
                  <h4 class="font-medium mb-3 text-gray-900 dark:text-white">关于应用</h4>
                  <p class="text-sm text-gray-700 dark:text-gray-300">Chato新生代全栈AI应用平台，满足你所想、符合你所需</p>
                </div>
              </div>
              
              <!-- 右侧：四个功能按钮 -->
              <div class="w-full md:w-1/2 space-y-3">
                <button class="w-full text-left p-3 rounded-lg text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-colors flex items-center justify-between hover:scale-100 transition-transform">
                  <span><i class="fa-regular fa-file-lines mr-2"></i> 使用条款</span>
                  <i class="fa-solid fa-chevron-right text-xs"></i>
                </button>
                <button class="w-full text-left p-3 rounded-lg text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-colors flex items-center justify-between hover:scale-100 transition-transform">
                  <span><i class="fa-solid fa-shield-halved mr-2"></i> 隐私政策</span>
                  <i class="fa-solid fa-chevron-right text-xs"></i>
                </button>
                <button class="w-full text-left p-3 rounded-lg text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-colors flex items-center justify-between hover:scale-100 transition-transform">
                  <span><i class="fa-solid fa-circle-question mr-2"></i> 帮助中心</span>
                  <i class="fa-solid fa-chevron-right text-xs"></i>
                </button>
                <a href="https://github.com/Kwillited/Chato" target="_blank" rel="noopener noreferrer" class="w-full text-left p-3 rounded-lg text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-colors flex items-center justify-between hover:scale-100 transition-transform">
                  <span><i class="fa-brands fa-github mr-2"></i> 开源仓库</span>
                  <i class="fa-solid fa-chevron-right text-xs"></i>
                </a>
              </div>
            </div>
            
            <!-- 新增底部div存放版权信息 -->
            <div class="w-full flex justify-center mt-6">
              <div class="text-xs text-gray-500 dark:text-gray-400 text-center">© 2025 Chato. 保留所有权利.</div>
            </div>
          </div>
        </div>
      </div>
    
  </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useSettingsStore } from '../../app/store/settingsStore.js';
import { useChatStore } from '../../app/store/chatStore.js';
import { useAppUI } from '../../shared/composables/useAppUI.js';
import logger from '../../shared/utils/logger.js';
import SettingsHeader from './SettingsHeader.vue';
import { useNavigation } from '../../shared/composables/useNavigation.js';

// 初始化stores
const settingsStore = useSettingsStore();
const chatStore = useChatStore();
const modelStore = useSettingsStore();
const { navigateToHome } = useNavigation();

// 使用应用UI状态组合式函数
const { activeTab, setActiveTab } = useAppUI();

// 监听activeTab变化
watch(activeTab, (newValue) => {
  console.log('SettingsPage activeTab changed to:', newValue);
});

// 处理标签切换
const handleTabChange = (tabValue) => {
  console.log('SettingsPage handleTabChange called with:', tabValue);
  setActiveTab(tabValue);
};

// 已配置模型列表的展开状态管理
const providerOpenStates = ref({});

// 模型表单状态管理
const editingProvider = ref(null);
const editingModel = ref(null);
const isModelFormVisible = ref(false);
const newModel = ref({
  id: '',
  type: 'llm',
  customName: '',
  context: '8k',
  active: true,
  streamingConfig: false,
  apiKey: '',
  apiBaseUrl: ''
});

// 组件挂载时加载模型
onMounted(() => {
  // 如果当前是模型标签页，加载模型数据
  if (activeTab.value === 'models') {
    loadModels();
  }
});

// 处理删除所有对话
const handleDeleteAllChats = () => {
  if (confirm('确定要删除所有对话吗？此操作不可恢复！')) {
    chatStore.clearAllChats();
  }
};

// 监听标签页变化，当切换到模型标签时加载模型数据
watch(
  () => activeTab.value,
  (newTab) => {
    if (newTab === 'models') {
      loadModels();
    }
  }
);

// 加载模型数据
const loadModels = async () => {
  try {
    await modelStore.loadModels();
  } catch (error) {
    logger.error('加载模型数据失败:', error);
  }
};

// 从modelStore获取已配置的供应商数据
const configuredProviders = computed(() => {
  return modelStore.configuredModels.map(model => {
    // 获取第一个版本的API配置作为供应商级别的默认配置
    const firstVersion = model.versions?.[0] || {};
    
    // 初始化展开状态（默认关闭）
    if (!(model.name in providerOpenStates.value)) {
      providerOpenStates.value[model.name] = false;
    }
    
    return {
      id: model.name.toLowerCase().replace(/\s+/g, '-'),
      name: model.name,
      url: model.api_base_url || '',
      apiBaseUrl: model.api_base_url || firstVersion.api_base_url || '',
      apiKey: firstVersion.api_key || '',
      open: providerOpenStates.value[model.name],
      models: model.versions?.map(version => ({
        id: version.version_name,
        type: version.type || 'llm',
        context: '8k', // 默认上下文，实际应从modelStore获取
        active: version.enabled || true,
        customName: version.custom_name,
        apiKey: version.api_key || '',
        apiBaseUrl: version.api_base_url || '',
        streamingConfig: version.streaming_config || false
      })) || [],
      showModelForm: false,
      newModel: {
        id: '',
        type: 'llm',
        customName: '',
        context: '8k',
        active: true,
        apiKey: '',
        apiBaseUrl: '',
        streamingConfig: false
      }
    };
  });
});

// 切换供应商卡片展开状态
const toggleProviderOpen = (providerName) => {
  providerOpenStates.value[providerName] = !providerOpenStates.value[providerName];
};

// 添加供应商函数 - 打开模型配置表单
const addProvider = async (provider) => {
  // 找到对应供应商的配置对象
  let providerConfig = configuredProviders.value.find(p => p.name === provider.name);
  
  // 如果供应商尚未配置，先添加到已配置列表
  if (!providerConfig) {
    // 将供应商添加到已配置列表（不生成默认版本）
    await modelStore.saveModelConfig(provider.name, {
      customName: '',
      apiKey: '',
      apiBaseUrl: '',
      versionName: '', // 空versionName不会触发默认版本生成
      streamingConfig: false
    });
    
    // 重新加载模型列表，确保数据更新
    await modelStore.loadModels();
    
    // 重新查找供应商配置
    providerConfig = configuredProviders.value.find(p => p.name === provider.name);
  }
  
  // 如果找到供应商配置，打开模型配置表单
  if (providerConfig) {
    // 确保供应商配置对象有open属性并设置为true
    if (!providerConfig.open) {
      providerConfig.open = true;
    }
    // 打开模型配置表单，让用户输入模型详细信息
    toggleModelForm(providerConfig);
  }
};

// 移除供应商函数 - 现在通过modelStore处理
const removeProvider = (provider) => {
  // 调用modelStore的deleteModelConfig方法来移除供应商
  modelStore.deleteModelConfig(provider.name);
};

// 切换模型表单显示状态
const toggleModelForm = (provider) => {
  editingProvider.value = provider;
  editingModel.value = null;
  // 初始化新模型数据
  newModel.value = {
    id: '',
    type: 'llm',
    customName: '',
    context: '8k',
    active: true,
    streamingConfig: false,
    apiKey: '',
    apiBaseUrl: ''
  };
  isModelFormVisible.value = true;
};

// 保存模型映射
const saveModelMapping = async () => {
  if (!editingProvider.value) return;
  
  // 验证模型ID是否为空
  if (!newModel.value.id.trim()) {
    return;
  }
  
  try {
    // 构建请求数据，使用供应商级别的API配置作为默认值
    const requestData = {
      customName: newModel.value.customName,
      versionName: newModel.value.id,
      apiKey: editingProvider.value.apiKey, // 使用供应商级别的API密钥
      apiBaseUrl: editingProvider.value.apiBaseUrl, // 使用供应商级别的API基础URL
      streamingConfig: newModel.value.streamingConfig
    };
    
    if (editingModel.value) {
      // 更新现有模型
      await modelStore.updateModelVersion(
        editingProvider.value.name,
        editingModel.value.id,
        requestData
      );
    } else {
      // 添加新模型
      await modelStore.addModelVersion(
        editingProvider.value.name,
        requestData
      );
    }
    
    // 关闭表单
    isModelFormVisible.value = false;
    editingProvider.value = null;
    editingModel.value = null;
  } catch (error) {
    logger.error('保存模型映射失败:', error);
  }
};

// 取消模型映射
const cancelModelMapping = () => {
  // 关闭表单
  isModelFormVisible.value = false;
  editingProvider.value = null;
  editingModel.value = null;
};

// 编辑模型映射
const editModelMapping = (provider, model) => {
  editingProvider.value = provider;
  editingModel.value = model;
  // 填充表单数据
  newModel.value = {
    id: model.id,
    type: model.type,
    customName: model.customName || '',
    context: model.context,
    active: model.active,
    streamingConfig: model.streamingConfig || false,
    apiKey: model.apiKey || '',
    apiBaseUrl: model.apiBaseUrl || ''
  };
  isModelFormVisible.value = true;
};

// 删除模型映射
const deleteModelMapping = async (provider, model) => {
  try {
    await modelStore.deleteModelVersion(provider.name, model.id);
  } catch (error) {
    logger.error('删除模型映射失败:', error);
  }
};

// 从modelStore获取可用的供应商数据（未配置的模型）
const availableProviders = computed(() => {
  // 确保返回的数据结构与模板期望的一致
  return modelStore.unconfiguredModels.map(model => ({
    name: model.name,
    desc: model.description || '',
    // 保留原始模型对象的所有属性
    ...model
  }));
});
</script>

<style scoped>
body {
  font-family: 'Inter', sans-serif;
  background-color: #ffffff;
}

.mono {
  font-family: 'JetBrains Mono', monospace;
}

/* 标签页切换过渡效果 */
main > div {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 紧凑型 Switch */
.toggle-checkbox {
  transition: all 0.3s ease;
  right: auto;
  left: 0;
  background-color: white;
}

.toggle-checkbox:checked {
  transform: translateX(calc(100% - 1px));
  border-color: #000;
}

.toggle-checkbox:checked + .toggle-label {
  background-color: #000;
}

.dark .toggle-checkbox {
  background-color: white;
}

.dark .toggle-checkbox:checked + .toggle-label {
  background-color: #3b82f6;
}

.dark .toggle-checkbox + .toggle-label {
  background-color: #374151;
}

.toggle-checkbox + .toggle-label {
  background-color: #e5e7eb;
}

/* 卡片悬停效果增强 */
.card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* 输入框和选择框交互效果 */
input, select {
  transition: all 0.2s ease;
}

input:focus, select:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 按钮点击反馈 */
button {
  transition: all 0.2s ease;
}

button:active {
  transform: scale(0.98);
}

/* 极细边框 */
.hairline-b {
  border-bottom: 1px solid #f1f1f1;
}

.hairline-t {
  border-top: 1px solid #f1f1f1;
}

.hairline-border {
  border: 1px solid #e5e7eb;
}

/* 可展开卡片动画 */
.group > div:nth-child(2) {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}

.group > div:nth-child(2).open {
  max-height: 500px;
  transition: max-height 0.5s ease-in;
}

/* 平滑滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.dark ::-webkit-scrollbar-thumb {
  background: #475569;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* Toggle Switch Styles */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e5e7eb;
  transition: .4s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #000;
}

input:focus + .toggle-slider {
  box-shadow: 0 0 1px #000;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

/* Dark mode for toggle switch */
.dark .toggle-slider {
  background-color: #374151;
}

.dark .toggle-slider:before {
  background-color: white;
}

.dark input:checked + .toggle-slider {
  background-color: #3b82f6;
}

.dark input:checked + .toggle-slider:before {
  background-color: white;
}
</style>