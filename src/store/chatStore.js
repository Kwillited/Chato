import { defineStore } from 'pinia';
import { apiService } from '../services/apiService';
import { generateId } from '../utils/data.js';
import { useSettingsStore } from './settingsStore.js';
import { useVectorStore } from './vectorStore.js';
import { useUiStore } from './uiStore.js';
import { showNotification } from '../utils/notificationUtils.js';
import { errorUtils, loadingUtils, notificationUtils as notifyUtils, apiUtils, stateUtils } from '../utils/storeUtils.js';
import { ref } from 'vue'; // 引入 ref

// 定义聊天消息的类型描述
/**
 * @typedef {Object} ChatMessage
 * @property {string} id - 消息ID
 * @property {'user' | 'ai'} role - 消息角色
 * @property {string} content - 消息内容
 * @property {number} timestamp - 消息时间戳
 * @property {string} [error] - 错误信息（可选）
 */

// 定义对话的类型描述
/**
 * @typedef {Object} Chat
 * @property {string} id - 对话ID
 * @property {string} title - 对话标题
 * @property {ChatMessage[]} messages - 消息列表
 * @property {number} createdAt - 创建时间
 * @property {number} updatedAt - 更新时间
 * @property {string} model - 使用的模型
 */

export const useChatStore = defineStore('chat', {
  state: () => ({
    chats: [],
    currentChatId: null,
    uploadedFiles: [],
    error: null,
    retryCount: 0, // 重试计数
    maxRetries: 10, // 最大重试次数
    retryInterval: 3000, // 初始重试间隔（毫秒）
  }),

  getters: {
    // 获取当前对话
    currentChat: (state) => {
      if (!state.currentChatId) return null;
      return state.chats.find((chat) => chat.id === state.currentChatId);
    },

    // 获取当前对话的消息列表
    currentChatMessages: (state) => {
      const currentChat = state.chats.find((chat) => chat.id === state.currentChatId);
      return currentChat ? currentChat.messages : [];
    },

    // 获取对话历史列表（按更新时间排序）
    chatHistory: (state) => {
      return [...state.chats].sort((a, b) => b.updatedAt - a.updatedAt);
    },

    // 获取过滤后的对话列表
    getFilteredChats: (state) => {
      // 使用 uiStore 获取 searchQuery
      const uiStore = useUiStore();
      const searchQuery = uiStore.searchQuery;
      
      if (!searchQuery.trim()) {
        return state.chats;
      }

      const query = searchQuery.toLowerCase();
      return state.chats.filter(
        (chat) =>
          chat.title.toLowerCase().includes(query) ||
          chat.messages.some((message) => message.content.toLowerCase().includes(query))
      );
    },
  },

  actions: {
    // 设置错误信息
    setError(error) {
      errorUtils.setError(this, error);
    },

    // 清空错误信息
    clearError() {
      errorUtils.clearError(this);
    },

    // 设置搜索关键词
    setSearchQuery(query) {
      // 使用 uiStore 更新 searchQuery
      const uiStore = useUiStore();
      uiStore.setSearchQuery(query);
    },

    // 创建新对话（调用API）
    async createNewChat(model) {
      try {
        // 先取消当前会话的选中状态，实现更流畅的过渡效果
        this.currentChatId = null;
        
        // 添加短暂延迟，让样式有时间过渡
        await new Promise(resolve => setTimeout(resolve, 50));
        
        console.log('调用API创建新对话...');
        const response = await apiService.chat.createChat('新对话');
        console.log('API调用成功，响应:', response);
        let newChat = response.chat;
        
        // 如果传递了模型参数，保存到新对话中
        if (model) {
          newChat = {
            ...newChat,
            model: model
          };
        }
        
        // 将新对话添加到本地状态
        this.chats.unshift(newChat); // 添加到开头，保持最新优先
        this.currentChatId = newChat.id;
        
        // 使用 uiStore 更新 messageInput
        const uiStore = useUiStore();
        uiStore.updateMessageInput('');

        return newChat;
      } catch (error) {
        console.error('创建新对话失败:', error);
        console.error('错误详情:', error.message, error.stack, error.response);
        errorUtils.setError(this, '创建新对话失败，请检查后端服务是否运行中');
        // 后端服务不可用时，不执行本地创建操作，直接返回报错
        throw error;
      }
    },

    // 选择对话
    selectChat(chatId) {
      const chat = this.chats.find((c) => c.id === chatId);
      if (chat) {
        this.currentChatId = chatId;
        
        // 使用 uiStore 更新 messageInput
        const uiStore = useUiStore();
        uiStore.updateMessageInput('');
        
        this.uploadedFiles = [];
        
        // 为了确保未读状态正确清除，我们可以在每个对话对象上添加一个显式的未读标记
        // 遍历所有对话，将当前选中的对话未读标记设置为false
        this.chats = this.chats.map(c => ({
          ...c,
          hasUnreadMessage: c.id !== chatId && (c.hasUnreadMessage || false)
        }));
        
        // 可以在这里添加加载对话历史的逻辑
        console.log('选择对话:', chatId);
      }
    },

    // 验证消息参数
    validateMessageParams(content, model) {
      if (!content.trim() && this.uploadedFiles.length === 0) return false;
      if (!model) {
        this.setError('请先选择一个AI模型');
        return false;
      }
      return true;
    },

    // 准备消息状态
    prepareMessageState(currentChat, content, model) {
      // 添加用户消息，并使用ref包装确保完整响应式
      const userMessageRef = ref({
        id: generateId('msg'),
        role: 'user',
        content: content.trim(),
        files: this.uploadedFiles.length > 0 ? [...this.uploadedFiles] : [],
        timestamp: Date.now(),
        status: 'sent',
      });

      currentChat.messages.push(userMessageRef);
      currentChat.updatedAt = Date.now();
      currentChat.model = model;

      // 如果是第一条消息，设置对话标题
      if (currentChat.messages.length === 1 && currentChat.title === '新对话') {
        currentChat.title = content.trim().substring(0, 30) + (content.length > 30 ? '...' : '');
      }

      // 添加一个带有isTyping=true的AI消息，用于显示加载动画，并使用ref包装
      const typingMessageRef = ref({
        id: generateId('msg'),
        role: 'ai',
        content: '',
        timestamp: Date.now(),
        status: 'typing',
        isTyping: true,
        model: model // 使用传入的model参数，避免显示默认的"NeoVAI"
      });
      currentChat.messages.push(typingMessageRef);
      
      // 强制更新currentChat，确保所有组件都能感知到变化
      stateUtils.forceUpdate(this, 'currentChat', this.currentChat);

      return typingMessageRef;
    },

    // 格式化模型名称
    formatModelName(model) {
      const modelStore = useSettingsStore();
      let formattedModel = model;
      
      // 检查是否需要进行格式转换（如果model不包含'-'，说明可能是旧格式）
      if (!formattedModel.includes('-') && modelStore.models.length > 0) {
        // 尝试找到对应的模型和版本
        for (const m of modelStore.models) {
          if (m.versions && Array.isArray(m.versions)) {
            for (const version of m.versions) {
              if (version.version_name === formattedModel) {
                // 只使用version_name字段
                formattedModel = `${m.name}-${version.version_name}`;
                break;
              }
            }
            if (formattedModel.includes('-')) break;
          }
        }
      }
      return formattedModel;
    },

    // 检查流式输出支持
    checkStreamingSupport(formattedModel) {
      const settingsStore = useSettingsStore();
      const systemStreamingEnabled = settingsStore.systemSettings.streamingEnabled || false;
      
      // 检查模型版本是否支持流式输出
      let modelStreamingEnabled = false;
      if (formattedModel && formattedModel.includes('-')) {
        const modelStore = useSettingsStore();
        const [modelName, versionName] = formattedModel.split('-', 2);
        const model = modelStore.models.find(m => m.name === modelName);
        if (model && model.versions) {
          const version = model.versions.find(v => v.version_name === versionName);
          if (version) {
            // 支持多种字段名，兼容不同版本的后端返回格式
            modelStreamingEnabled = version.streaming || version.streamingConfig || version.streaming_config || false;
          }
        }
      }
      
      // 只有当系统设置启用且模型版本支持流式输出时，才使用流式API
      return systemStreamingEnabled && modelStreamingEnabled;
    },

    // 准备RAG配置
    prepareRagConfig() {
      // 获取vectorStore实例
      const vectorStore = useVectorStore();
      
      // 从vectorStore获取RAG配置
      const vectorConfig = vectorStore.config;
      
      // 构建后端需要的ragConfig格式
      let ragConfigToUse = {
        enabled: vectorConfig.enabled,
        topK: vectorConfig.retrieval.topK,
        scoreThreshold: vectorConfig.retrieval.threshold,
        searchType: vectorConfig.retrieval.mode,
        selectedFolders: [],
        selectedKnowledgeBases: []
      };
      
      // 如果有选中的文件夹，设置检索范围为该文件夹
      if (vectorStore.currentSelectedFolder) {
        const targetFolder = vectorStore.currentSelectedFolder;
        ragConfigToUse.selectedFolders = targetFolder && targetFolder.id ? [targetFolder.id] : [];
      }
      
      // 添加调试日志，查看实际发送给后端的ragConfig
      console.log('🔍 RAG配置调试:', {
        currentSelectedFolder: vectorStore.currentSelectedFolder,
        selectedFolders: ragConfigToUse.selectedFolders,
        ragEnabled: ragConfigToUse.enabled
      });
      
      return ragConfigToUse;
    },

    // 发送流式消息
    async sendStreamingMessage(currentChat, content, formattedModel, deepThinking, ragConfigToUse, webSearchEnabled, agent) {
      let aiMessage = null;

      // 立即清空上传文件列表，提供更好的用户体验
      const filesToSend = [...this.uploadedFiles]; // 保存要发送的文件
      this.uploadedFiles = []; // 立即清空

      try {
        await apiService.chat.sendStreamingMessage(
          currentChat.id,         // chatId
          content.trim(),         // message
          filesToSend,            // 使用保存的文件列表
          {
            model: formattedModel, // 确保使用name-version.version_name格式的模型名称
            deepThinking: deepThinking, // 使用传递的深度思考参数
            ragConfig: ragConfigToUse, // 使用动态调整的RAG配置
            webSearchEnabled: webSearchEnabled, // 使用传递的联网搜索参数
            agent: agent // 使用传递的智能体参数
          },
            // 处理接收到的消息
            (data) => {
              console.log('处理流式消息数据块:', data); // 添加日志追踪
              
              if (!aiMessage) {
                // 更新之前添加的typing消息，替换为实际的AI回复
                const typingMessageIndex = currentChat.messages.findIndex(msg => msg && msg.value && msg.value.isTyping === true);
                if (typingMessageIndex !== -1) {
                  // 移除typing消息
                  currentChat.messages.splice(typingMessageIndex, 1);
                }
                
                // 创建AI消息，并使用ref包装确保完整响应式
                const messageContent = ref({
                  id: generateId('msg'),
                  role: 'ai',
                  content: '',
                  thinking: '',
                  timestamp: Date.now(),
                  status: 'streaming',
                  isTyping: false,
                  lastUpdate: Date.now(), // 初始化lastUpdate字段
                  model: formattedModel // 设置模型名称
                });
                
                aiMessage = messageContent;
                currentChat.messages.push(messageContent);
              }
              
              // 处理工具开始执行事件
              if (data.event === 'on_tool_start') {
                console.log('工具开始执行:', data.name, '参数:', data.data.input);
                
                // 确保aiMessage存在
                if (!aiMessage) {
                  // 创建AI消息
                  const messageContent = ref({
                    id: generateId('msg'),
                    role: 'ai',
                    content: '',
                    thinking: '',
                    timestamp: Date.now(),
                    status: 'tool_executing',
                    isTyping: false,
                    lastUpdate: Date.now(),
                    model: formattedModel,
                    currentTool: data.name,
                    toolInput: data.data.input,
                    toolExecutions: [] // 添加工具执行记录数组
                  });
                  
                  aiMessage = messageContent;
                  currentChat.messages.push(messageContent);
                } else {
                  // 添加工具执行记录
                  if (!aiMessage.value.toolExecutions) {
                    aiMessage.value.toolExecutions = [];
                  }
                  
                  // 保存当前工具信息到执行记录
                  aiMessage.value.toolExecutions.push({
                    name: data.name,
                    input: data.data.input,
                    status: 'executing',
                    timestamp: Date.now()
                  });
                  
                  // 更新AI消息，设置工具执行状态
                  aiMessage.value.status = 'tool_executing';
                  aiMessage.value.currentTool = data.name;
                  aiMessage.value.toolInput = data.data.input;
                  aiMessage.value.lastUpdate = Date.now();
                }
                
                // 强制更新currentChat
                stateUtils.forceUpdate(this, 'currentChat', this.currentChat);
                return;
              }
              
              // 处理工具执行完成事件
              if (data.event === 'on_tool_end') {
                console.log('工具执行完成:', data.name);
                
                // 更新AI消息，将工具执行状态设置为成功
                if (aiMessage) {
                  // 更新最新的工具执行记录状态
                  if (aiMessage.value.toolExecutions && aiMessage.value.toolExecutions.length > 0) {
                    const lastToolExecution = aiMessage.value.toolExecutions[aiMessage.value.toolExecutions.length - 1];
                    if (lastToolExecution.name === data.name) {
                      lastToolExecution.status = 'completed';
                      lastToolExecution.completedAt = Date.now();
                    }
                  }
                  
                  aiMessage.value.status = 'tool_executed';
                  aiMessage.value.lastUpdate = Date.now();
                }
                
                // 强制更新currentChat
                stateUtils.forceUpdate(this, 'currentChat', this.currentChat);
                return;
              }
              
              // 处理智能体流程开始事件
              if (data.event === 'on_chain_start' && data.name === 'LangGraph') {
                console.log('智能体流程开始:', data.name);
                
                // 更新AI消息，设置为智能体等待状态
                if (aiMessage) {
                  aiMessage.value.status = 'agent_waiting';
                  aiMessage.value.lastUpdate = Date.now();
                }
                
                // 强制更新currentChat
                stateUtils.forceUpdate(this, 'currentChat', this.currentChat);
                return;
              }
              
              // 处理后端返回的流式数据格式
              let contentToAdd = '';
              // 只处理data.chunk字段
              if (data.chunk) {
                contentToAdd = data.chunk;
              }
              
              // 确保内容更新能够触发Vue响应式更新
              if (contentToAdd) {
                // 检查并处理think标签
                const chunk = contentToAdd;
                
                // 检查是否在think标签内
                if (aiMessage.value._inThinkingTag !== undefined) {
                  // 已经在think标签内，检查是否结束
                  const endTagIndex = chunk.indexOf('</think>');
                  if (endTagIndex !== -1) {
                    // 找到结束标签，更新思考内容并退出think标签模式
                    aiMessage.value.thinking = aiMessage.value.thinking + chunk.substring(0, endTagIndex);
                    // 标记思考内容已完成，用于自动折叠
                    aiMessage.value.thinkingCompleted = true;
                    // 更新实际内容（结束标签之后的内容）
                    const actualContent = chunk.substring(endTagIndex + 8); // 8是</think>的长度
                    if (actualContent) {
                      aiMessage.value.content = aiMessage.value.content + actualContent;
                    }
                    // 退出think标签模式
                    delete aiMessage.value._inThinkingTag;
                  } else {
                    // 未找到结束标签，继续累积思考内容
                    aiMessage.value.thinking = aiMessage.value.thinking + chunk;
                  }
                } else {
                  // 不在think标签内，检查是否开始think标签
                  const startTagIndex = chunk.indexOf('<think>');
                  if (startTagIndex !== -1) {
                    // 找到开始标签
                    // 先处理开始标签之前的内容（如果有）
                    const beforeThink = chunk.substring(0, startTagIndex);
                    if (beforeThink) {
                      aiMessage.value.content = aiMessage.value.content + beforeThink;
                    }
                    // 开始think标签模式，累积开始标签之后的内容
                    aiMessage.value._inThinkingTag = true;
                    aiMessage.value.thinking = chunk.substring(startTagIndex + 7); // 7是<think>的长度
                  } else {
                    // 没有think标签，直接更新实际内容
                    aiMessage.value.content = aiMessage.value.content + chunk;
                  }
                }
                
                aiMessage.value.lastUpdate = Date.now(); // 更新lastUpdate以触发ChatMessage组件重新渲染
              }
              
              // 检查是否完成
              if (data.done || data.completed || data.type === 'end') {
                // 确保消息状态正确
                if (aiMessage && (aiMessage.value.status === 'streaming' || aiMessage.value.status === 'tool_executing' || aiMessage.value.status === 'tool_executed')) {
                  // 根据当前状态设置最终状态
                  const finalStatus = aiMessage.value.status === 'tool_executing' || aiMessage.value.status === 'tool_executed' 
                    ? 'tool_executed' 
                    : 'received';
                  
                  aiMessage.value.status = finalStatus;
                  
                  // 清理临时状态
                  delete aiMessage.value._inThinkingTag;
                  
                  // 添加：确保响应式系统能够检测到变化，同时确保model字段存在
                  const updatedMessage = { ...aiMessage.value };
                  updatedMessage.status = finalStatus;
                  updatedMessage.isTyping = false;
                  // 确保model字段存在，使用data.ai_message.model或fallback到formattedModel
                  updatedMessage.model = data.ai_message?.model || formattedModel;
                  // 如果后端已经处理了think标签，使用后端的结果
                  if (data.ai_message && data.ai_message.thinking) {
                    updatedMessage.thinking = data.ai_message.thinking;
                    updatedMessage.content = data.ai_message.content;
                  }
                  aiMessage.value = updatedMessage;
                  
                  // 添加：强制更新currentChat，确保所有组件都能感知到变化
                  stateUtils.forceUpdate(this, 'currentChat', this.currentChat);
                  
                  // 如果用户当前没有查看该对话，设置未读标记并显示通知
                  this.handleNewMessageNotification(currentChat);
                }
              }
              
              currentChat.updatedAt = Date.now();
            },
            // 处理错误
            (error) => {
              console.error('流式消息错误:', error);
              errorUtils.setError(this, `流式消息失败: ${error.message || '未知错误'}`);
            },
            // 处理完成
                () => {
                  console.log('流式消息完成');
                  
                  // 添加：在Promise完成回调中再次确保状态更新和model字段存在
                  if (aiMessage && aiMessage.value) {
                    // 创建新对象以确保响应式系统能够检测到变化
                    const updatedMessage = { ...aiMessage.value };
                    updatedMessage.status = 'received';
                    updatedMessage.isTyping = false;
                    // 确保model字段存在，fallback到formattedModel
                    updatedMessage.model = updatedMessage.model || formattedModel;
                    aiMessage.value = updatedMessage;
                
                // 强制更新currentChat
                stateUtils.forceUpdate(this, 'currentChat', this.currentChat);
                
                // 如果用户当前没有查看该对话，设置未读标记并显示通知
                this.handleNewMessageNotification(currentChat);
              }
            }
          );
          
          // 确保消息状态正确
          if (aiMessage && aiMessage.status === 'streaming') {
            aiMessage.status = 'received';
          }
      } catch (error) {
        console.error('发送流式消息失败:', error);
        errorUtils.setError(this, `发送消息失败: ${error.message || '未知错误'}`);
        
        // 处理错误消息
        this.handleMessageError(currentChat, error);
      }
    },

    // 发送非流式消息
    async sendNonStreamingMessage(currentChat, content, formattedModel, deepThinking, ragConfigToUse, webSearchEnabled, agent) {
      // 立即清空上传文件列表，提供更好的用户体验
      const filesToSend = [...this.uploadedFiles]; // 保存要发送的文件
      this.uploadedFiles = []; // 立即清空
      
      try {
        let response = await apiService.chat.sendMessage(
          currentChat.id,         // chatId
          content.trim(),         // message
          filesToSend,            // 使用保存的文件列表
          {
            model: formattedModel, // 确保使用name-version.version_name格式的模型名称
            stream: false,  // 非流式输出
            deepThinking: deepThinking, // 使用传递的深度思考参数
            ragConfig: ragConfigToUse, // 使用动态调整的RAG配置
            webSearchEnabled: webSearchEnabled, // 使用传递的联网搜索参数
            agent: agent // 使用传递的智能体参数
          }
        );
        
        // 添加调试日志，查看实际响应格式
        console.log('非流式API响应:', JSON.stringify(response, null, 2));
        
        // 修复：处理API返回的数组格式 [response_data, status_code]
        if (Array.isArray(response) && response.length >= 1) {
          response = response[0]; // 获取实际的响应数据对象
        }
        
        // 更新之前添加的typing消息，替换为实际的AI回复
        const typingMessageIndex = currentChat.messages.findIndex(msg => msg && msg.value && msg.value.isTyping === true);
        if (typingMessageIndex !== -1) {
          // 移除typing消息
          currentChat.messages.splice(typingMessageIndex, 1);
        }
        
        // 添加AI回复，并使用ref包装
        if (response && response.error) {
          // 处理后端返回的错误响应
          const aiMessageRef = ref({
            id: generateId('msg'),
            role: 'ai',
            content: '',
            timestamp: Date.now(),
            error: `⚠️ 发送失败: ${response.error}`,
            status: 'error',
            isTyping: false,
          });
          
          currentChat.messages.push(aiMessageRef);
          currentChat.updatedAt = Date.now();
        } else if (response && response.ai_message) {
          // 确保ai_message存在，无论content是否为空
          const aiMessageRef = ref({
            id: generateId('msg'),
            role: 'ai',
            content: response.ai_message.content || '（空回复）', // 处理空内容情况
            timestamp: Date.now(),
            status: 'received',
            isTyping: false,
            model: response.ai_message.model || formattedModel // 设置模型名称
          });
          
          currentChat.messages.push(aiMessageRef);
          currentChat.updatedAt = Date.now();
          
          // 如果用户当前没有查看该对话，设置未读标记并显示通知
          this.handleNewMessageNotification(currentChat);
        } else {
          // 处理其他情况，显示更详细的调试信息
          const aiMessageRef = ref({
            id: generateId('msg'),
            role: 'ai',
            content: '',
            timestamp: Date.now(),
            error: `⚠️ 发送失败: 无效的API响应格式 ${JSON.stringify(response)}`,
            status: 'error',
            isTyping: false,
          });
          
          currentChat.messages.push(aiMessageRef);
          currentChat.updatedAt = Date.now();
        }
      } catch (error) {
        console.error('发送非流式消息失败:', error);
        errorUtils.setError(this, `发送消息失败: ${error.message || '未知错误'}`);
        
        // 处理错误消息
        this.handleMessageError(currentChat, error);
      }
    },

    // 处理消息错误
    handleMessageError(currentChat, error) {
      // 更新之前添加的typing消息，替换为错误消息
      const typingMessageIndex = currentChat.messages.findIndex(msg => msg && msg.value && msg.value.isTyping === true);
      if (typingMessageIndex !== -1) {
        // 移除typing消息
        currentChat.messages.splice(typingMessageIndex, 1);
      }
      
      // 添加错误消息，并使用ref包装
      const errorMessageRef = ref({
        id: (Date.now() + 2).toString(),
        role: 'ai',
        content: '',
        timestamp: Date.now(),
        error: `⚠️ 发送失败: ${error.message || '服务器连接错误'}`,
        isTyping: false,
      });
      
      currentChat.messages.push(errorMessageRef);
    },

    // 清理消息发送后的状态
    cleanupAfterMessage() {
      // 使用 uiStore 更新加载状态
      const uiStore = useUiStore();
      uiStore.setLoading(false);
      this.uploadedFiles = [];
    },

    // 发送消息（使用API服务）
    async sendMessage(content, model, deepThinking = false, webSearchEnabled = false, agent = false) {
      // 验证消息参数
      if (!this.validateMessageParams(content, model)) return;
      
      // 如果没有当前对话，创建一个新对话
      if (!this.currentChatId) {
        await this.createNewChat(model);
      }

      const currentChat = this.currentChat;
      if (!currentChat) return;

      // 使用 uiStore 更新加载状态和消息输入
      const uiStore = useUiStore();
      uiStore.setLoading(true);
      uiStore.updateMessageInput('');
      this.clearError();

      // 准备消息状态
      this.prepareMessageState(currentChat, content, model);

      try {
        // 格式化模型名称
        const formattedModel = this.formatModelName(model);
        
        // 检查流式输出支持
        const shouldUseStreaming = this.checkStreamingSupport(formattedModel);
        
        // 准备RAG配置
        const ragConfigToUse = this.prepareRagConfig();
        
        // 根据是否支持流式输出选择发送方式
        if (shouldUseStreaming) {
          // 发送流式消息
          await this.sendStreamingMessage(currentChat, content, formattedModel, deepThinking, ragConfigToUse, webSearchEnabled, agent);
        } else {
          // 发送非流式消息
          await this.sendNonStreamingMessage(currentChat, content, formattedModel, deepThinking, ragConfigToUse, webSearchEnabled, agent);
        }

        // 不再需要本地保存，所有数据已通过API同步到后端
      } catch (error) {
        console.error('发送消息失败:', error);
        errorUtils.setError(this, `发送消息失败: ${error.message || '未知错误'}`);

        // 处理消息错误
        this.handleMessageError(currentChat, error);
      } finally {
        // 清理消息发送后的状态
        this.cleanupAfterMessage();
      }
    },

    // 删除对话（调用API）
    async deleteChat(chatId) {
      try {
        // 先调用API删除对话
        await apiService.chat.deleteChat(chatId);
        console.log('API删除对话成功:', chatId);

        // API调用成功后，从本地状态中删除对话
        const chatIndex = this.chats.findIndex((chat) => chat.id === chatId);
        if (chatIndex !== -1) {
          this.chats.splice(chatIndex, 1);

          // 如果删除的是当前对话，选择第一个对话或设置 currentChatId 为 null
          if (this.currentChatId === chatId) {
            if (this.chats.length > 0) {
              this.selectChat(this.chats[0].id);
            } else {
              this.currentChatId = null;
            }
          }
          
          // 新增：无论删除的是不是当前对话，只要删除后chats数组为空，就将currentChatId设置为null
          if (this.chats.length === 0) {
            this.currentChatId = null;
          }
        }
      } catch (error) {
        console.error('API删除对话失败:', error);
        errorUtils.setError(this, '删除对话失败，请检查后端服务是否运行中');
        // 后端服务不可用时，不执行本地删除操作，直接返回报错
        throw error;
      }
    },

    // 清空所有对话（调用API）
    async clearAllChats() {
      try {
        // 调用API删除所有对话
        await apiService.chat.deleteAllChats();
        console.log('API删除所有对话成功');

        // API调用成功后，清空本地状态
        this.chats = [];
        this.currentChatId = null;
      } catch (error) {
        console.error('API删除所有对话失败:', error);
        errorUtils.setError(this, '删除所有对话失败，请检查后端服务是否运行中');
        // 后端服务不可用时，不执行本地清空操作，直接返回报错
        throw error;
      }
    },

    // 添加上传文件
    addUploadedFile(file) {
      this.uploadedFiles.push(file);
    },

    // 移除上传文件
    removeUploadedFile(index) {
      if (index >= 0 && index < this.uploadedFiles.length) {
        this.uploadedFiles.splice(index, 1);
      }
    },

    // 更新消息输入
    updateMessageInput(content) {
      // 使用 uiStore 更新 messageInput
      const uiStore = useUiStore();
      uiStore.updateMessageInput(content);
    },

    // 从后端API获取对话历史
    async loadChatHistory(_manualRetry = false) {
      // 使用 uiStore 更新加载状态
      const uiStore = useUiStore();
      uiStore.setLoading(true);
      this.clearError();

      try {
        console.log('调用API获取对话历史...');
        // 调用API获取对话历史 - 使用统一的requestWithRetry机制
        const response = await apiService.chat.getHistory();
        console.log('API调用成功，响应:', response);
        
        if (response && response.chats) {
          // 确保chats是数组
          this.chats = Array.isArray(response.chats) ? response.chats : [];
          
          // 确保数据一致性
          this.ensureDataIntegrity();
          
          // 如果有对话历史，不自动选择任何对话
          this.currentChatId = null;
        } else {
          // 没有对话历史，清空当前状态
          this.chats = [];
          this.currentChatId = null;
        }
      } catch (error) {
        console.error('获取对话历史失败:', error);
        errorUtils.setError(this, '获取对话历史失败，请检查后端服务是否运行中');
        this.currentChatId = null;
        // 统一的重试机制已在apiService中实现，这里不再需要额外的重试逻辑
        throw error;
      } finally {
        // 使用 uiStore 更新加载状态
        const uiStore = useUiStore();
        uiStore.setLoading(false);
      }
    },



    // 确保数据一致性
    ensureDataIntegrity() {
      // 获取settingsStore实例
      const settingsStore = useSettingsStore();
      // 过滤无效对话
      this.chats = this.chats.filter((chat) => chat && chat.id && chat.messages && Array.isArray(chat.messages));

      // 确保所有对话和消息有必要的字段
      this.chats = this.chats.map((chat) => {
        // 确保消息有必要的字段
        const processedMessages = chat.messages.map((message) => {
          // 处理ref包装的消息
          const messageData = message?.value || message;
          
          // 对于历史消息，使用对话的createdAt或updatedAt作为基准时间，避免所有消息都显示为"刚刚"
          // 对于新消息，使用messageData.timestamp或messageData.time
          let messageTimestamp = messageData.timestamp || messageData.time;
          if (!messageTimestamp) {
            // 如果没有时间戳，使用对话的createdAt或updatedAt，并根据消息索引调整时间
            const baseTime = chat.createdAt || chat.updatedAt || Date.now();
            // 为每条消息添加一个递增的时间偏移，避免所有消息显示同一时间
            const messageIndex = chat.messages.indexOf(message);
            messageTimestamp = baseTime + (messageIndex * 1000); // 每条消息间隔1秒
          }
          
          return {
            ...messageData,
            // 确保timestamp字段存在
            timestamp: messageTimestamp,
            // 确保role字段存在
            role: messageData.role || 'ai',
            // 确保content字段存在
            content: messageData.content || '',
            // 确保model字段存在，使用正确的默认值，避免硬编码GPT4
            model: messageData.model || chat.model || settingsStore.systemSettings.defaultModel || 'Chato',
            // 确保files字段存在（默认为空数组）
            files: Array.isArray(messageData.files) ? messageData.files : []
          };
        });

        return {
          id: chat.id,
          title: chat.title || '未命名对话',
          messages: processedMessages,
          createdAt: chat.createdAt || Date.now(),
          updatedAt: chat.updatedAt || Date.now(),
          model: chat.model || settingsStore.systemSettings.defaultModel || 'Chato',
          pinned: chat.pinned || false,
          metadata: chat.metadata || {},
        };
      });
    },

    // 导出对话历史
    exportChatHistory(chatId) {
      const chat = this.chats.find((c) => c.id === chatId);
      if (!chat) return null;

      try {
        const exportData = {
          title: chat.title,
          createdAt: chat.createdAt,
          updatedAt: chat.updatedAt,
          model: chat.model,
          messages: chat.messages,
        };

        return JSON.stringify(exportData, null, 2);
      } catch (error) {
        console.error('导出对话失败:', error);
        errorUtils.setError(this, '导出对话失败');
        return null;
      }
    },

    // 导出所有对话
    exportAllChats() {
      try {
        // 将对话历史转换为JSON字符串
        const chatData = JSON.stringify(this.chats, null, 2);

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
        errorUtils.setError(this, '导出对话历史失败');
        throw error;
      }
    },

    // 切换对话置顶状态
    async togglePinChat(chatId) {
      const chat = this.chats.find((chat) => chat.id === chatId);
      if (chat) {
        const newPinnedState = !chat.pinned;
        chat.pinned = newPinnedState;

        // 重新排序对话列表，置顶的对话在前
        this.chats.sort((a, b) => {
          if (a.pinned && !b.pinned) return -1;
          if (!a.pinned && b.pinned) return 1;
          return b.updatedAt - a.updatedAt;
        });

        // 调用API同步到后端
        try {
          await apiService.chat.updateChatPin(chatId, newPinnedState);
        } catch (error) {
          console.error('更新对话置顶状态失败:', error);
          // 如果API调用失败，恢复原始状态
          chat.pinned = !newPinnedState;
          // 重新排序对话列表
          this.chats.sort((a, b) => {
            if (a.pinned && !b.pinned) return -1;
            if (!a.pinned && b.pinned) return 1;
            return b.updatedAt - a.updatedAt;
          });
        }
      }
    },

    // 重置所有对话的未读状态
    resetUnreadStatus() {
      this.chats = this.chats.map(chat => ({
        ...chat,
        hasUnreadMessage: false
      }));
    },

    // 批量删除对话（调用API）
    async batchDeleteChats(chatIds) {
      try {
        // 先检查后端服务是否可用（通过尝试删除第一个对话）
        if (chatIds.length > 0) {
          try {
            await apiService.chat.deleteChat(chatIds[0]);
          } catch (error) {
            console.error('后端服务不可用，无法进行批量删除:', error);
            this.setError('后端服务不可用，批量删除失败');
            throw error; // 后端服务不可用时，直接返回报错
          }
        }

        // 后端服务可用，继续删除剩余对话
        const successfullyDeleted = [chatIds[0]]; // 第一个对话已成功删除
        for (const chatId of chatIds.slice(1)) {
          try {
            await apiService.chat.deleteChat(chatId);
            successfullyDeleted.push(chatId);
            console.log('API删除对话成功:', chatId);
          } catch (error) {
            console.error('单个对话删除失败:', chatId, error);
            // 记录错误但继续删除其他对话
          }
        }

        // API调用成功后，从本地状态中删除成功删除的对话
        this.chats = this.chats.filter((chat) => !successfullyDeleted.includes(chat.id));

        // 如果当前对话被删除，选择第一个对话或设置 currentChatId 为 null
        if (successfullyDeleted.includes(this.currentChatId)) {
          if (this.chats.length > 0) {
            this.selectChat(this.chats[0].id);
          } else {
            this.currentChatId = null;
          }
        }

        // 不再需要本地保存，所有数据已通过API同步到后端
      } catch (error) {
        console.error('批量删除对话过程出错:', error);
        errorUtils.setError(this, '批量删除失败，请检查后端服务是否运行中');
        // 后端服务不可用时，不执行本地删除操作，直接返回报错
        throw error;
      }
    },
    
    // 取消流式响应
    cancelStreaming() {
      try {
        apiService.chat.closeStreamingConnection();
        console.log('流式连接已关闭');
      } catch (error) {
        console.error('关闭流式连接失败:', error);
      }
    },
    
    // 处理新消息通知
    handleNewMessageNotification(chat) {
      // 如果用户当前没有查看该对话，设置未读标记并显示通知
      if (this.currentChatId !== chat.id) {
        this.chats = this.chats.map(c => 
          c.id === chat.id ? { ...c, hasUnreadMessage: true } : c
        );
        // 获取通知显示时间设置
        const settingsStore = useSettingsStore();
        let displayTimeMs = 3000; // 默认3秒
        const displayTimeSetting = settingsStore.notificationsConfig?.displayTime;
        if (displayTimeSetting === '2秒') {
          displayTimeMs = 2000;
        } else if (displayTimeSetting === '5秒') {
          displayTimeMs = 5000;
        } else if (displayTimeSetting === '10秒') {
          displayTimeMs = 10000;
        }
        // 显示新消息通知
        showNotification(`新消息: ${chat.title}`, 'success', displayTimeMs, true);
        // 播放未读消息通知声音
        this.playNotificationSound();
      }
    },
    
    // 播放未读消息通知声音
playNotificationSound() {
  try {
    const settingsStore = useSettingsStore();
    const notificationsConfig = settingsStore.currentNotificationsConfig;
    
    // 检查是否启用了通知声音，并且在浏览器环境中
    if (notificationsConfig && notificationsConfig.sound && typeof window !== 'undefined' && typeof window.Audio !== 'undefined') {
      // 使用项目中已有的通知音频文件
      const audio = new window.Audio('/src/assets/notice.mp3');
      // 播放声音，并捕获可能的错误
      audio.play().catch(err => {
        console.warn('播放通知声音失败:', err);
      });
    }
  } catch (error) {
    console.error('处理通知声音时出错:', error);
  }
},
  },
});
