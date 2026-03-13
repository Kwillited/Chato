/**
 * 流式处理服务
 * 负责处理SSE流式响应和相关逻辑
 */

import { handleStreamingResponse } from './apiService.js';
import { errorService } from './errorService.js';

/**
 * 将File对象转换为base64字符串
 * @param {File} file - File对象
 * @returns {Promise<string>} base64字符串
 */
export async function fileToBase64(file) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      // 移除data URL前缀，只保留base64内容
      const base64Content = reader.result.split(',')[1];
      resolve(base64Content);
    };
    reader.readAsDataURL(file);
  });
}

/**
 * 处理文件数组，转换为可序列化的格式
 * @param {Array} files - 文件数组
 * @returns {Promise<Array>} 处理后的文件数组
 */
export async function processFiles(files) {
  return await Promise.all(
    files.map(async (file) => {
      if (file instanceof File) {
        const content = await fileToBase64(file);
        return {
          name: file.name,
          content: content,
          type: file.type,  // 保留文件类型
          size: file.size  // 保留文件大小
        };
      }
      return file;
    })
  );
}

/**
 * 处理SSE响应格式
 * @param {Object} data - 解析后的SSE数据
 * @returns {Object} 统一格式的数据
 */
export function processSSEFormat(data) {
  if (data.chunk) {
    // 标准格式
    return data;
  } else if (data.content) {
    // LangChain 原始格式
    return { chunk: data.content, done: false };
  } else if (data.event && data.data) {
    // 事件流格式
    if (data.event === 'on_chat_model_end') {
      // 结束事件，视为结束标志
      return { ...data, done: true };
    } else if (data.event === 'on_chat_model_stream') {
      // 流事件，提取chunk内容，保留node和step信息
      if (data.data.content !== undefined) {
        // data包含content字段
        return { 
          event: data.event, 
          node: data.node, 
          agent_step: data.agent_step, 
          chunk: data.data.content, 
          reasoning_content: data.data.reasoning_content, // 从data对象中提取reasoning_content字段
          done: false 
        };
      } else if (data.data.chunk) {
        // 兼容旧格式：data包含chunk字段
        const chunkData = data.data.chunk;
        if (chunkData.content) {
          // chunk包含content字段
          return { 
            event: data.event, 
            node: data.node, 
            agent_step: data.agent_step, 
            chunk: chunkData.content, 
            reasoning_content: data.data.reasoning_content, // 从data对象中提取reasoning_content字段
            done: false 
          };
        } else {
          // chunk直接是内容
          return { 
            event: data.event, 
            node: data.node, 
            agent_step: data.agent_step, 
            chunk: chunkData, 
            reasoning_content: data.data.reasoning_content, // 从data对象中提取reasoning_content字段
            done: false 
          };
        }
      } else if (data.data.content) {
        // data直接包含content字段
        return { 
          event: data.event, 
          node: data.node, 
          agent_step: data.agent_step, 
          chunk: data.data.content, 
          reasoning_content: data.data.reasoning_content, // 从data对象中提取reasoning_content字段
          done: false 
        };
      }
    } else {
      // 其他事件流格式，直接传递
      return data;
    }
  } else if (data.done) {
    // 结束标志
    return data;
  } else if (typeof data === 'string') {
    // 纯文本格式
    return { chunk: data, done: false };
  } else {
    // 其他格式，直接传递
    return data;
  }
}

/**
 * 流式消息发送服务
 */
export const streamingService = {
  /**
   * 发送流式消息
   * @param {string} chatId - 对话ID
   * @param {string} message - 消息内容
   * @param {Array} files - 文件数组
   * @param {Object} options - 选项
   * @param {Function} onMessage - 消息回调
   * @param {Function} onError - 错误回调
   * @param {Function} onComplete - 完成回调
   * @returns {Promise} 流式请求Promise
   */
  sendStreamingMessage: async (chatId, message, files, options = {}, onMessage, onError, onComplete) => {
    const { model = 'GPT-4', modelParams = {}, ragConfig = {}, deepThinking = false, agent = false, webSearchEnabled = false, selectedMessageIds = [] } = options;
    
    try {
      // 处理文件，转换为可序列化的格式
      const processedFiles = await processFiles(files);
      
      const url = `/chats/${chatId}/messages`;
      const data = {
        message,
        files: processedFiles,
        model,
        modelParams,
        ragConfig,
        stream: true,  // 传递stream参数给后端
        deepThinking, // 传递deepThinking参数给后端
        agent, // 传递agent参数给后端
        webSearchEnabled, // 传递webSearchEnabled参数给后端
        selectedMessageIds // 传递selectedMessageIds参数给后端
      };
      
      // 创建一个Promise来包装流式请求
      return new Promise((resolve, reject) => {
        try {
          const closeConnection = handleStreamingResponse(url, data, 
            (data) => {
              // 处理SSE格式
              const processedData = processSSEFormat(data);
              onMessage(processedData);
            }, 
            (error) => {
              const processedError = errorService.handleStreamingError(error);
              onError?.(processedError);
            }, 
            () => {
              onComplete?.();
              resolve();
            }
          );
          
          // 存储关闭连接的方法，以便在需要时手动关闭
          streamingService.activeStreamingConnection = closeConnection;
        } catch (error) {
          const processedError = errorService.handleStreamingError(error);
          reject(processedError);
        }
      });
    } catch (error) {
      const processedError = errorService.handleError(error, '处理文件');
      throw processedError;
    }
  },
  
  /**
   * 关闭活动的流式连接
   */
  closeStreamingConnection: () => {
    if (streamingService.activeStreamingConnection) {
      streamingService.activeStreamingConnection();
      streamingService.activeStreamingConnection = null;
    }
  },
  
  // 活动的流式连接
  activeStreamingConnection: null
};
