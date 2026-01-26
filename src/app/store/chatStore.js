import { defineStore } from 'pinia';
import { apiService } from '../../shared/api/apiService';
import { generateId } from '../../shared/utils/helpers.js';
import { convertDisplayTimeToMs } from '../../shared/utils/date.js';
import { showNotification } from '../../shared/utils/notificationUtils.js';
import { ref, onUnmounted } from 'vue'; // 引入 ref 和 onUnmounted
import eventBus, { Events } from '../../shared/utils/eventBus.js'; // 引入事件总线
import { ModelAdapter, MessageAdapter } from '../../shared/utils/modelAdapter.js'; // 引入模型和消息适配器
import logger from '../../shared/utils/logger.js'; // 引入日志工具
import { useBaseStore } from './baseStore'; // 引入基础Store功能

// 获取基础Store功能
const baseStore = useBaseStore();

// 定义聊天消息的类型描述 - 统一使用ref包装
/**
 * @typedef {Object} ChatMessageData
 * @property {string} id - 消息ID
 * @property {'user' | 'ai'} role - 消息角色
 * @property {string} content - 消息内容
 * @property {number} timestamp - 消息时间戳
 * @property {string} status - 消息状态 (sent, received, streaming, error)
 * @property {boolean} isTyping - 是否正在输入
 * @property {string} model - 使用的模型
 * @property {string} [error] - 错误信息（可选）
 * @property {Array} files - 附件列表
 * @property {number} lastUpdate - 最后更新时间
 * @property {Object} metadata - 元数据
 */

/**
 * @typedef {ref<ChatMessageData>} ChatMessage - 统一使用ref包装的消息对象
 */

// 定义对话的类型描述
/**
 * @typedef {Object} Chat
 * @property {string} id - 对话ID
 * @property {string} title - 对话标题
 * @property {ChatMessage[]} messages - 统一使用ref包装的消息列表
 * @property {number} createdAt - 创建时间
 * @property {number} updatedAt - 更新时间
 * @property {string} model - 使用的模型
 * @property {boolean} [pinned] - 是否置顶
 * @property {Object} [metadata] - 元数据
 */

export const useChatStore = defineStore('chat', {
  state: () => ({
    // 基础状态
    ...baseStore.state(),
    
    chats: [],
    currentChatId: null,
    messageInput: '',
    uploadedFiles: [],
    searchQuery: '',
    activeView: 'grid', // 视图模式：'grid'为对话视图，'list'为图谱视图
    retryCount: 0, // 重试计数
    maxRetries: 10, // 最大重试次数
    retryInterval: 3000, // 初始重试间隔（毫秒）
    
    // 适配器实例
    modelAdapter: ModelAdapter,
    messageAdapter: MessageAdapter
  }),
  


  getters: {
    // 基础getters
    ...baseStore.getters,
    
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
      if (!state.searchQuery.trim()) {
        return state.chats;
      }

      const query = state.searchQuery.toLowerCase();
      return state.chats.filter(
        (chat) =>
          chat.title.toLowerCase().includes(query) ||
          chat.messages.some((message) => {
            // 统一处理ref包装的消息对象
            const messageValue = message?.value;
            return messageValue && messageValue.content.toLowerCase().includes(query);
          })
      );
    },
    
    // 获取标准化的模型列表
    standardizedModels: (state) => {
      return state.models?.map(model => ModelAdapter.standardizeModelConfig(model)) || [];
    }
  },

  actions: {
    // 基础actions
    ...baseStore.actions,
    
    // 设置搜索关键词
    setSearchQuery(query) {
      this.searchQuery = query;
    },

    // 创建新对话（调用API）
    async createNewChat(model) {
      // 先取消当前会话的选中状态，实现更流畅的过渡效果
      this.currentChatId = null;
      
      // 添加短暂延迟，让样式有时间过渡
      await new Promise(resolve => setTimeout(resolve, 50));
      
      return this.callApi(async () => {
        logger.info('调用API创建新对话...');
        const response = await apiService.chat.createChat('新对话');
        logger.info('API调用成功，响应:', response);
        
        // 处理标准化后的API响应
        let newChat = response?.data?.chat || response?.chat || {};
        
        // 如果传递了模型参数，保存到新对话中
        if (model) {
          newChat = {
            ...newChat,
            model: model
          };
        }
        
        // 确保消息列表使用ref包装
        newChat.messages = MessageAdapter.standardizeMessageList(newChat.messages || []);
        
        // 将新对话添加到本地状态
        this.chats.unshift(newChat); // 添加到开头，保持最新优先
        this.currentChatId = newChat.id;
        this.messageInput = '';
        
        // 发布新对话创建事件
        eventBus.emit(Events.CHAT_CREATED, newChat);

        return newChat;
      }, { handleError: true });
    },

    // 选择对话
    selectChat(chatId) {
      const chat = this.chats.find((c) => c.id === chatId);
      if (chat) {
        this.currentChatId = chatId;
        this.messageInput = '';
        this.uploadedFiles = [];
        
        // 为了确保未读状态正确清除，我们可以在每个对话对象上添加一个显式的未读标记
        // 遍历所有对话，将当前选中的对话未读标记设置为false
        this.chats = this.chats.map(c => ({
          ...c,
          hasUnreadMessage: c.id !== chatId && (c.hasUnreadMessage || false)
        }));
        
        // 发布对话选择事件
        eventBus.emit(Events.CHAT_SELECTED, chat);
        
        // 可以在这里添加加载对话历史的逻辑
        logger.debug('选择对话:', chatId);
      }
    },

    // 发送消息（使用API服务）
    async sendMessage(content, model, deepThinking = false, webSearchEnabled = false) {
      if (!content.trim() && this.uploadedFiles.length === 0) return;
      if (!model) {
        this.setError('请先选择一个AI模型');
        return;
      }
      if (!this.currentChatId) {
        // 如果没有当前对话，创建一个新对话
        await this.createNewChat(model);
      }

      const currentChat = this.currentChat;
      if (!currentChat) return;

      // 立即设置isLoading为true，确保按钮状态立即更新
      this.isLoading = true;
      this.messageInput = '';
      this.clearError();

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
      
      // 发布消息发送事件
      eventBus.emit(Events.MESSAGE_SENT, {
        chatId: currentChat.id,
        message: userMessageRef.value
      });

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
      this.currentChat = { ...this.currentChat };

      try {
        // 动态导入store实例，减少直接依赖
        const { useSettingsStore } = await import('./settingsStore.js');
        
        const settingsStore = useSettingsStore();
        
        // 确保model参数使用name-version.version_name格式
        let formattedModel = model;
        
        // 检查是否需要进行格式转换（如果model不包含'-'，说明可能是旧格式）
        if (!formattedModel.includes('-') && settingsStore.models.length > 0) {
          // 尝试找到对应的模型和版本
          for (const m of settingsStore.models) {
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
        
        const systemStreamingEnabled = settingsStore.systemSettings.streamingEnabled || false;
        
        // 检查模型版本是否支持流式输出
    let modelStreamingEnabled = false;
    if (formattedModel && formattedModel.includes('-')) {
      const [modelName, versionName] = formattedModel.split('-', 2);
      const model = settingsStore.models.find(m => m.name === modelName);
      if (model && model.versions) {
        const version = model.versions.find(v => v.version_name === versionName);
        if (version) {
          // 支持多种字段名，兼容不同版本的后端返回格式
          modelStreamingEnabled = version.streaming || version.streamingConfig || version.streaming_config || false;
        }
      }
    }
        
        // 只有当系统设置启用且模型版本支持流式输出时，才使用流式API
        const shouldUseStreaming = systemStreamingEnabled && modelStreamingEnabled;
        
        // 从settingsStore获取RAG配置
        const vectorConfig = settingsStore.vectorConfig;
        
        // 构建后端需要的ragConfig格式
        let ragConfigToUse = {
          enabled: vectorConfig.enabled,
          topK: vectorConfig.retrieval.topK,
          scoreThreshold: vectorConfig.retrieval.threshold,
          searchType: vectorConfig.retrieval.mode,
          selectedFolders: [],
          selectedKnowledgeBases: []
        };
        
        // 动态导入fileStore，减少直接依赖
        const { useFileStore } = await import('./fileStore.js');
        const fileStore = useFileStore();
        
        // 如果有选中的文件夹，设置检索范围为该文件夹
        if (fileStore.currentFolder) {
          const targetFolder = fileStore.currentFolder;
          ragConfigToUse.selectedFolders = targetFolder && targetFolder.id ? [targetFolder.id] : [];
        }
        
        // 添加调试日志，查看实际发送给后端的ragConfig
        logger.debug('🔍 RAG配置调试:', {
          currentSelectedFolder: fileStore.currentFolder,
          selectedFolders: ragConfigToUse.selectedFolders,
          ragEnabled: ragConfigToUse.enabled
        });
        
        if (shouldUseStreaming) {
        // 使用流式消息发送
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
              webSearchEnabled: webSearchEnabled // 使用传递的联网搜索参数
            },
              // 处理接收到的消息
              (data) => {
                logger.debug('处理流式消息数据块:', data); // 添加日志追踪
                
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
                    timestamp: Date.now(),
                    status: 'streaming',
                    isTyping: false,
                    lastUpdate: Date.now(), // 初始化lastUpdate字段
                    model: formattedModel // 设置模型名称
                  });
                  
                  aiMessage = messageContent;
                  currentChat.messages.push(messageContent);
                  
                  // 发布AI消息创建事件
                  eventBus.emit(Events.MESSAGE_RECEIVED, {
                    chatId: currentChat.id,
                    message: messageContent.value
                  });
                }
                
                // 处理后端返回的流式数据格式
                let contentToAdd = '';
                // 只处理data.chunk字段
                if (data.chunk) {
                  contentToAdd = data.chunk;
                }
                
                // 确保内容更新能够触发Vue响应式更新
                if (contentToAdd) {
                  // 使用ref.value直接更新属性，确保任何变化都能触发响应式更新
                  aiMessage.value.content = aiMessage.value.content + contentToAdd;
                  aiMessage.value.lastUpdate = Date.now(); // 更新lastUpdate以触发ChatMessage组件重新渲染
                  
                  // 发布消息更新事件
                  eventBus.emit(Events.MESSAGE_UPDATED, {
                    chatId: currentChat.id,
                    messageId: aiMessage.value.id,
                    content: aiMessage.value.content,
                    status: 'streaming'
                  });
                  
                  // 由于使用了ref，不需要额外的splice操作来强制更新数组
                }
                
                // 检查是否完成
                if (data.done || data.completed || data.type === 'end') {
                  // 确保消息状态正确
                  if (aiMessage && aiMessage.value.status === 'streaming') {
                    aiMessage.value.status = 'received';
                    
                    // 添加：确保响应式系统能够检测到变化，同时确保model字段存在
                    const updatedMessage = { ...aiMessage.value };
                    updatedMessage.status = 'received';
                    updatedMessage.isTyping = false;
                    // 确保model字段存在，使用data.ai_message.model或fallback到formattedModel
                    updatedMessage.model = data.ai_message?.model || formattedModel;
                    aiMessage.value = updatedMessage;
                    
                    // 发布消息更新事件（完成）
                    eventBus.emit(Events.MESSAGE_UPDATED, {
                      chatId: currentChat.id,
                      messageId: aiMessage.value.id,
                      content: aiMessage.value.content,
                      status: 'received',
                      model: updatedMessage.model
                    });
                    
                    // 添加：强制更新currentChat，确保所有组件都能感知到变化
                    this.currentChat = { ...this.currentChat };
                    
                    // 如果用户当前没有查看该对话，设置未读标记并显示通知
                    if (this.currentChatId !== currentChat.id) {
                      this.chats = this.chats.map(c => 
                c.id === currentChat.id ? { ...c, hasUnreadMessage: true } : c
              );
              // 获取通知显示时间设置
              let displayTimeMs = convertDisplayTimeToMs(settingsStore.notificationsConfig?.displayTime);
              // 显示新消息通知
              showNotification(`新消息: ${currentChat.title}`, 'success', displayTimeMs, true);
              // 播放未读消息通知声音
              this.playNotificationSound();
                    }
                  }
                }
                
                currentChat.updatedAt = Date.now();
              },
              // 处理错误
              (error) => {
                logger.error('流式消息错误:', error);
                this.setError(`流式消息失败: ${error.message || '未知错误'}`);
              },
              // 处理完成
                  () => {
                    logger.debug('流式消息完成');
                    
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
                  this.currentChat = { ...this.currentChat };
                  
                  // 如果用户当前没有查看该对话，设置未读标记并显示通知
                  if (this.currentChatId !== currentChat.id) {
                    this.chats = this.chats.map(c => 
              c.id === currentChat.id ? { ...c, hasUnreadMessage: true } : c
            );
            // 获取通知显示时间设置
            let displayTimeMs = convertDisplayTimeToMs(settingsStore.notificationsConfig?.displayTime);
            // 显示新消息通知
            showNotification(`新消息: ${currentChat.title}`, 'success', displayTimeMs, true);
            // 播放未读消息通知声音
            this.playNotificationSound();
                  }
                }
              }
            );
            
            // 确保消息状态正确
            if (aiMessage && aiMessage.status === 'streaming') {
              aiMessage.status = 'received';
            }
          } catch (error) {
            logger.error('发送流式消息失败:', error);
            this.setError(`发送消息失败: ${error.message || '未知错误'}`);
            
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
          }
        } else {
          // 使用普通消息发送
          // 立即清空上传文件列表，提供更好的用户体验
          const filesToSend = [...this.uploadedFiles]; // 保存要发送的文件
          this.uploadedFiles = []; // 立即清空
          
          let response = await apiService.chat.sendMessage(
            currentChat.id,         // chatId
            content.trim(),         // message
            filesToSend,            // 使用保存的文件列表
            {
              model: formattedModel, // 确保使用name-version.version_name格式的模型名称
              stream: false,  // 非流式输出
              deepThinking: deepThinking, // 使用传递的深度思考参数
              ragConfig: ragConfigToUse, // 使用动态调整的RAG配置
              webSearchEnabled: webSearchEnabled // 使用传递的联网搜索参数
            }
          );
          
          // 添加调试日志，查看实际响应格式
          logger.debug('非流式API响应:', JSON.stringify(response, null, 2));
          
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
            if (this.currentChatId !== currentChat.id) {
              this.chats = this.chats.map(c => 
                c.id === currentChat.id ? { ...c, hasUnreadMessage: true } : c
              );
              // 获取通知显示时间设置
              let displayTimeMs = convertDisplayTimeToMs(settingsStore.notificationsConfig?.displayTime);
              // 显示新消息通知
              showNotification(`新消息: ${currentChat.title}`, 'success', displayTimeMs, true);
              // 播放未读消息通知声音
              this.playNotificationSound();
            }
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
        }

        // 不再需要本地保存，所有数据已通过API同步到后端
      } catch (error) {
        logger.error('发送消息失败:', error);
        this.setError(`发送消息失败: ${error.message || '未知错误'}`);

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
      } finally {
        this.isLoading = false;
        this.uploadedFiles = [];
      }
    },

    // 删除对话（调用API）
    async deleteChat(chatId) {
      return this.callApi(async () => {
        // 先调用API删除对话
        await apiService.chat.deleteChat(chatId);
        logger.info('API删除对话成功:', chatId);

        // API调用成功后，从本地状态中删除对话
        const chatIndex = this.chats.findIndex((chat) => chat.id === chatId);
        if (chatIndex !== -1) {
          const deletedChat = this.chats[chatIndex];
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
          
          // 发布对话删除事件
          eventBus.emit(Events.CHAT_DELETED, { chatId: chatId, deletedChat: deletedChat });
        }
      }, { handleError: true });
    },

    // 清空所有对话（调用API）
    async clearAllChats() {
      return this.callApi(async () => {
        // 调用API删除所有对话
        await apiService.chat.deleteAllChats();
        logger.info('API删除所有对话成功');

        // API调用成功后，清空本地状态
        this.chats = [];
        this.currentChatId = null;
      }, { handleError: true });
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
      this.messageInput = content;
    },

    // 从后端API获取对话历史
    async loadChatHistory(_manualRetry = false) {
      return this.callApi(async () => {
        logger.info('调用API获取对话历史...');
        // 调用API获取对话历史 - 使用统一的requestWithRetry机制
        const response = await apiService.chat.getHistory();
        logger.info('API调用成功，响应:', response);
        
        // 处理标准化后的API响应
        const chatsData = response?.data?.chats || response?.chats || [];
        
        if (Array.isArray(chatsData)) {
          // 标准化对话历史，确保消息使用ref包装
          this.chats = chatsData.map(chat => ({
            ...chat,
            // 标准化消息列表，统一使用ref包装
            messages: MessageAdapter.standardizeMessageList(chat.messages || [])
          }));
          
          // 确保数据一致性
          this.ensureDataIntegrity();
          
          // 如果有对话历史，不自动选择任何对话
          this.currentChatId = null;
          
          // 发布聊天历史加载完成事件
          eventBus.emit(Events.CHAT_HISTORY_LOADED, this.chats);
        } else {
          // 没有对话历史，清空当前状态
          this.chats = [];
          this.currentChatId = null;
          
          // 发布聊天历史加载完成事件（空）
          eventBus.emit(Events.CHAT_HISTORY_LOADED, []);
        }
      }, { handleError: true });
    },

    // 确保数据一致性
    async ensureDataIntegrity() {
      // 动态导入settingsStore，减少直接依赖
      const { useSettingsStore } = await import('./settingsStore.js');
      const settingsStore = useSettingsStore();
      
      // 过滤无效对话
      this.chats = this.chats.filter((chat) => chat && chat.id && chat.messages && Array.isArray(chat.messages));

      // 确保所有对话和消息有必要的字段
      this.chats = this.chats.map((chat) => {
        // 确保消息有必要的字段，并统一使用ref包装
        const processedMessages = chat.messages.map((message) => {
          // 使用MessageAdapter标准化消息格式，统一使用ref包装
          return MessageAdapter.standardizeMessage(message);
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
          hasUnreadMessage: chat.hasUnreadMessage || false
        };
      });
    },

    // 导出模型适配器和消息适配器
    getModelAdapter() {
      return ModelAdapter;
    },

    getMessageAdapter() {
      return MessageAdapter;
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
        logger.error('导出对话失败:', error);
        this.setError('导出对话失败');
        return null;
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
          logger.error('更新对话置顶状态失败:', error);
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
            logger.error('后端服务不可用，无法进行批量删除:', error);
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
            logger.info('API删除对话成功:', chatId);
          } catch (error) {
            logger.error('单个对话删除失败:', chatId, error);
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
        logger.error('批量删除对话过程出错:', error);
        this.setError('批量删除失败，请检查后端服务是否运行中');
        // 后端服务不可用时，不执行本地删除操作，直接返回报错
        throw error;
      }
    },
    
    // 取消流式响应
    cancelStreaming() {
      try {
        apiService.chat.closeStreamingConnection();
        logger.debug('流式连接已关闭');
      } catch (error) {
        logger.error('关闭流式连接失败:', error);
      }
    },
    
    // 播放未读消息通知声音
async playNotificationSound() {
  try {
    // 动态导入settingsStore，减少直接依赖
    const { useSettingsStore } = await import('./settingsStore.js');
    const settingsStore = useSettingsStore();
    const notificationsConfig = settingsStore.currentNotificationsConfig;
    
    // 检查是否启用了通知声音，并且在浏览器环境中
    if (notificationsConfig && notificationsConfig.sound && typeof window !== 'undefined' && typeof window.Audio !== 'undefined') {
      // 使用项目中已有的通知音频文件
      const audio = new window.Audio('/src/assets/notice.mp3');
      // 播放声音，并捕获可能的错误
      audio.play().catch(err => {
        logger.warn('播放通知声音失败:', err);
      });
    }
  } catch (error) {
    logger.error('处理通知声音时出错:', error);
  }
},

    // 获取当前对话标题
    getCurrentChatTitle() {
      const currentChat = this.chats.find(chat => chat.id === this.currentChatId);
      return currentChat ? currentChat.title : '新对话';
    },
  },
});
