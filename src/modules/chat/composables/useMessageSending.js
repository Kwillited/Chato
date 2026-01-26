import { ref, computed } from 'vue';
import { useChatStore } from '../../../app/store/chatStore.js';
import { useSettingsStore } from '../../../app/store/settingsStore.js';
import { useFileStore } from '../../../app/store/fileStore.js';
import logger from '../../../shared/utils/logger.js';
import { generateId } from '../../../shared/utils/helpers.js';
import { ref as vueRef } from 'vue'; // 重命名避免冲突

/**
 * 聊天消息发送管理组合函数，封装消息发送的复杂逻辑
 * @returns {Object} 包含消息发送相关的状态和方法
 */
export function useMessageSending() {
  const chatStore = useChatStore();
  const settingsStore = useSettingsStore();
  const fileStore = useFileStore();
  
  // 响应式状态
  const isSending = ref(false);
  const sendProgress = ref(0);
  const messageError = ref(null);
  
  /**
   * 发送消息的核心方法
   * @param {string} content - 消息内容
   * @param {string} model - 模型名称
   * @param {boolean} deepThinking - 是否启用深度思考
   * @param {boolean} webSearchEnabled - 是否启用网络搜索
   * @param {Array} files - 上传的文件列表
   * @returns {Promise<Object>} 发送结果
   */
  const sendMessage = async (content, model, deepThinking = false, webSearchEnabled = false, files = []) => {
    try {
      isSending.value = true;
      sendProgress.value = 0;
      messageError.value = null;
      
      // 检查参数
      if (!content.trim() && files.length === 0) {
        throw new Error('消息内容不能为空');
      }
      
      if (!model) {
        throw new Error('请先选择一个AI模型');
      }
      
      // 确保有当前对话
      if (!chatStore.currentChatId) {
        await chatStore.createNewChat(model);
      }
      
      const currentChat = chatStore.currentChat;
      if (!currentChat) {
        throw new Error('当前对话不存在');
      }
      
      // 创建用户消息
      const userMessage = createUserMessage(content, files);
      
      // 添加用户消息到当前对话
      currentChat.messages.push(vueRef(userMessage));
      currentChat.updatedAt = Date.now();
      currentChat.model = model;
      
      // 如果是第一条消息，设置对话标题
      if (currentChat.messages.length === 1 && currentChat.title === '新对话') {
        currentChat.title = content.trim().substring(0, 30) + (content.length > 30 ? '...' : '');
      }
      
      // 创建并添加typing消息
      const typingMessage = createTypingMessage(model);
      currentChat.messages.push(vueRef(typingMessage));
      
      // 准备模型格式
      const formattedModel = prepareModelFormat(model);
      
      // 检查是否支持流式输出
      const shouldUseStreaming = checkStreamingSupport(formattedModel);
      
      // 准备RAG配置
      const ragConfig = prepareRagConfig();
      
      // 根据是否支持流式输出选择发送方式
      if (shouldUseStreaming) {
        await sendStreamingMessage(currentChat, content, files, formattedModel, deepThinking, webSearchEnabled, ragConfig);
      } else {
        await sendRegularMessage(currentChat, content, files, formattedModel, deepThinking, webSearchEnabled, ragConfig);
      }
      
      sendProgress.value = 100;
      return { success: true };
      
    } catch (error) {
      messageError.value = error.message;
      logger.error('发送消息失败:', error);
      throw error;
    } finally {
      isSending.value = false;
    }
  };
  
  /**
   * 创建用户消息对象
   * @param {string} content - 消息内容
   * @param {Array} files - 上传的文件列表
   * @returns {Object} 用户消息对象
   */
  const createUserMessage = (content, files) => {
    return {
      id: generateId('msg'),
      role: 'user',
      content: content.trim(),
      files: files.length > 0 ? [...files] : [],
      timestamp: Date.now(),
      status: 'sent'
    };
  };
  
  /**
   * 创建正在输入的AI消息对象
   * @param {string} model - 模型名称
   * @returns {Object} 正在输入的AI消息对象
   */
  const createTypingMessage = (model) => {
    return {
      id: generateId('msg'),
      role: 'ai',
      content: '',
      timestamp: Date.now(),
      status: 'typing',
      isTyping: true,
      model: model
    };
  };
  
  /**
   * 准备模型格式
   * @param {string} model - 原始模型名称
   * @returns {string} 格式化后的模型名称
   */
  const prepareModelFormat = (model) => {
    let formattedModel = model;
    
    // 确保model参数使用name-version.version_name格式
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
    
    return formattedModel;
  };
  
  /**
   * 检查是否支持流式输出
   * @param {string} formattedModel - 格式化后的模型名称
   * @returns {boolean} 是否支持流式输出
   */
  const checkStreamingSupport = (formattedModel) => {
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
    return systemStreamingEnabled && modelStreamingEnabled;
  };
  
  /**
   * 准备RAG配置
   * @returns {Object} RAG配置对象
   */
  const prepareRagConfig = () => {
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
    
    return ragConfigToUse;
  };
  
  /**
   * 发送流式消息
   * @param {Object} currentChat - 当前对话对象
   * @param {string} content - 消息内容
   * @param {Array} files - 上传的文件列表
   * @param {string} formattedModel - 格式化后的模型名称
   * @param {boolean} deepThinking - 是否启用深度思考
   * @param {boolean} webSearchEnabled - 是否启用网络搜索
   * @param {Object} ragConfig - RAG配置
   */
  const sendStreamingMessage = async (currentChat, content, files, formattedModel, deepThinking, webSearchEnabled, ragConfig) => {
    logger.info('使用流式API发送消息');
    
    try {
      // 动态导入API服务
      const { apiService } = await import('../../../shared/api/apiService.js');
      const { eventBus, Events } = await import('../../../shared/utils/eventBus.js');
      const { showNotification } = await import('../../../shared/utils/notificationUtils.js');
      const { convertDisplayTimeToMs } = await import('../../../shared/utils/date.js');
      
      let aiMessage = null;
      
      // 使用传入的文件列表
      const filesToSend = [...files];
      
      // 动态导入settingsStore
      const { useSettingsStore } = await import('../../../app/store/settingsStore.js');
      const settingsStore = useSettingsStore();
      
      await apiService.chat.sendStreamingMessage(
        currentChat.id,         // chatId
        content.trim(),         // message
        filesToSend,            // 使用保存的文件列表
        {
          model: formattedModel, // 确保使用name-version.version_name格式的模型名称
          deepThinking: deepThinking, // 使用传递的深度思考参数
          ragConfig: ragConfig, // 使用动态调整的RAG配置
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
              const messageContent = vueRef({
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
                
                // 创建新对象以确保响应式系统能够检测到变化
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
                chatStore.currentChat = { ...chatStore.currentChat };
                
                // 如果用户当前没有查看该对话，设置未读标记并显示通知
                if (chatStore.currentChatId !== currentChat.id) {
                  chatStore.chats = chatStore.chats.map(c => 
                    c.id === currentChat.id ? { ...c, hasUnreadMessage: true } : c
                  );
                  // 获取通知显示时间设置
                  let displayTimeMs = convertDisplayTimeToMs(settingsStore.notificationsConfig?.displayTime);
                  // 显示新消息通知
                  showNotification(`新消息: ${currentChat.title}`, 'success', displayTimeMs, true);
                  // 播放未读消息通知声音
                  if (typeof chatStore.playNotificationSound === 'function') {
                    chatStore.playNotificationSound();
                  }
                }
              }
            }
            
            currentChat.updatedAt = Date.now();
          },
          // 处理错误
          (error) => {
            logger.error('流式消息错误:', error);
            // 这里可以考虑将错误信息传递给上层
          },
          // 处理完成
              () => {
                logger.debug('流式消息完成');
                
                // 在Promise完成回调中再次确保状态更新和model字段存在
                if (aiMessage && aiMessage.value) {
                  // 创建新对象以确保响应式系统能够检测到变化
                  const updatedMessage = { ...aiMessage.value };
                  updatedMessage.status = 'received';
                  updatedMessage.isTyping = false;
                  // 确保model字段存在，fallback到formattedModel
                  updatedMessage.model = updatedMessage.model || formattedModel;
                  aiMessage.value = updatedMessage;
              
                  // 强制更新currentChat
                  chatStore.currentChat = { ...chatStore.currentChat };
              
                  // 如果用户当前没有查看该对话，设置未读标记并显示通知
                  if (chatStore.currentChatId !== currentChat.id) {
                    chatStore.chats = chatStore.chats.map(c => 
                      c.id === currentChat.id ? { ...c, hasUnreadMessage: true } : c
                    );
                    // 获取通知显示时间设置
                    let displayTimeMs = convertDisplayTimeToMs(settingsStore.notificationsConfig?.displayTime);
                    // 显示新消息通知
                    showNotification(`新消息: ${currentChat.title}`, 'success', displayTimeMs, true);
                    // 播放未读消息通知声音
                    if (typeof chatStore.playNotificationSound === 'function') {
                      chatStore.playNotificationSound();
                    }
                  }
                }
              }
        );
        
        // 确保消息状态正确
        if (aiMessage && aiMessage.status === 'streaming') {
          aiMessage.status = 'received';
        }
        
      } catch (err) {
        logger.error('发送流式消息失败:', err);
        
        // 更新之前添加的typing消息，替换为错误消息
        const typingMessageIndex = currentChat.messages.findIndex(msg => msg && msg.value && msg.value.isTyping === true);
        if (typingMessageIndex !== -1) {
          // 移除typing消息
          currentChat.messages.splice(typingMessageIndex, 1);
        }
        
        // 添加错误消息，并使用ref包装
        const errorMessageRef = vueRef({
          id: generateId('msg'),
          role: 'ai',
          content: '',
          timestamp: Date.now(),
          error: `⚠️ 发送失败: ${err.message || '服务器连接错误'}`,
          isTyping: false,
        });
        
        currentChat.messages.push(errorMessageRef);
        throw err;
      }
  };
  
  /**
   * 发送普通消息
   * @param {Object} currentChat - 当前对话对象
   * @param {string} content - 消息内容
   * @param {Array} files - 上传的文件列表
   * @param {string} formattedModel - 格式化后的模型名称
   * @param {boolean} deepThinking - 是否启用深度思考
   * @param {boolean} webSearchEnabled - 是否启用网络搜索
   * @param {Object} ragConfig - RAG配置
   */
  const sendRegularMessage = async (currentChat, content, files, formattedModel, deepThinking, webSearchEnabled, ragConfig) => {
    logger.info('使用普通API发送消息');
    
    try {
      // 动态导入API服务
      const { apiService } = await import('../../../shared/api/apiService.js');
      const { eventBus, Events } = await import('../../../shared/utils/eventBus.js');
      const { showNotification } = await import('../../../shared/utils/notificationUtils.js');
      const { convertDisplayTimeToMs } = await import('../../../shared/utils/date.js');
      
      // 动态导入settingsStore
      const { useSettingsStore } = await import('../../../app/store/settingsStore.js');
      const settingsStore = useSettingsStore();
      
      // 使用传入的文件列表
      const filesToSend = [...files];
      
      let response = await apiService.chat.sendMessage(
        currentChat.id,         // chatId
        content.trim(),         // message
        filesToSend,            // 使用保存的文件列表
        {
          model: formattedModel, // 确保使用name-version.version_name格式的模型名称
          stream: false,  // 非流式输出
          deepThinking: deepThinking, // 使用传递的深度思考参数
          ragConfig: ragConfig, // 使用动态调整的RAG配置
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
      
      let aiMessageRef;
      
      // 添加AI回复，并使用ref包装
      if (response && response.error) {
        // 处理后端返回的错误响应
        aiMessageRef = vueRef({
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
        aiMessageRef = vueRef({
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
        
        // 发布AI消息创建事件
        eventBus.emit(Events.MESSAGE_RECEIVED, {
          chatId: currentChat.id,
          message: aiMessageRef.value
        });
        
        // 发布消息更新事件（完成）
        eventBus.emit(Events.MESSAGE_UPDATED, {
          chatId: currentChat.id,
          messageId: aiMessageRef.value.id,
          content: aiMessageRef.value.content,
          status: 'received',
          model: aiMessageRef.value.model
        });
        
        // 如果用户当前没有查看该对话，设置未读标记并显示通知
        if (chatStore.currentChatId !== currentChat.id) {
          chatStore.chats = chatStore.chats.map(c => 
            c.id === currentChat.id ? { ...c, hasUnreadMessage: true } : c
          );
          // 获取通知显示时间设置
          let displayTimeMs = convertDisplayTimeToMs(settingsStore.notificationsConfig?.displayTime);
          // 显示新消息通知
          showNotification(`新消息: ${currentChat.title}`, 'success', displayTimeMs, true);
          // 播放未读消息通知声音
          if (typeof chatStore.playNotificationSound === 'function') {
            chatStore.playNotificationSound();
          }
        }
      } else {
        // 处理其他情况，显示更详细的调试信息
        aiMessageRef = vueRef({
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
      
      // 强制更新currentChat，确保所有组件都能感知到变化
      chatStore.currentChat = { ...chatStore.currentChat };
      
    } catch (err) {
      logger.error('发送普通消息失败:', err);
      
      // 更新之前添加的typing消息，替换为错误消息
      const typingMessageIndex = currentChat.messages.findIndex(msg => msg && msg.value && msg.value.isTyping === true);
      if (typingMessageIndex !== -1) {
        // 移除typing消息
        currentChat.messages.splice(typingMessageIndex, 1);
      }
      
      // 添加错误消息，并使用ref包装
      const errorMessageRef = vueRef({
        id: generateId('msg'),
        role: 'ai',
        content: '',
        timestamp: Date.now(),
        error: `⚠️ 发送失败: ${err.message || '服务器连接错误'}`,
        isTyping: false,
      });
      
      currentChat.messages.push(errorMessageRef);
      currentChat.updatedAt = Date.now();
      
      // 强制更新currentChat，确保所有组件都能感知到变化
      chatStore.currentChat = { ...chatStore.currentChat };
      
      throw err;
    }
  };
  
  /**
   * 取消正在发送的消息
   */
  const cancelSend = () => {
    // TODO: 实现取消发送逻辑
    logger.info('取消发送消息');
    isSending.value = false;
    sendProgress.value = 0;
    messageError.value = '发送已取消';
  };
  
  return {
    // 状态
    isSending,
    sendProgress,
    messageError,
    
    // 方法
    sendMessage,
    cancelSend
  };
}
