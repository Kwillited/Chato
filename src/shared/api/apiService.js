import axios from 'axios';

// 导入日志工具
import logger from '../utils/logger.js';

// 统一API配置
const API_CONFIG = {
  BASE_URL: '/api',
  TIMEOUT: 60000, // 增加超时时间到60秒，以确保非流式请求有足够时间完成
  HEALTH_CHECK_TIMEOUT: 3000,
  FALLBACK_HEALTH_CHECK_TIMEOUT: 5000,
  HEADERS: {
    'Content-Type': 'application/json',
  },
  RETRY_CONFIG: {
    maxRetries: 5,
    initialDelay: 500,
    backoffFactor: 1.5,
    maxDelay: 8000,
    jitter: 0.1, // ±10% 随机抖动
    retryableStatusCodes: [500, 502, 503, 504],
    retryableMethods: ['GET', 'POST', 'PUT', 'DELETE'],
  }
};

// 创建axios实例
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    logger.info('API请求', {
      method: config.method?.toUpperCase(),
      url: config.url,
      data: config.method !== 'GET' ? config.data : undefined
    });
    return config;
  },
  (error) => {
    logger.error('API请求错误', error);
    return Promise.reject(error);
  }
);

// API响应适配器 - 统一处理API响应格式
class ApiResponseAdapter {
  /**
   * 标准化API响应格式
   * @param {Object} response - 原始API响应
   * @returns {Object} 标准化后的响应
   */
  static standardizeResponse(response) {
    // 检查是否已经是标准化格式
    if (response && response.success !== undefined && response.data !== undefined) {
      return response;
    }

    // 处理不同的响应格式
    if (Array.isArray(response)) {
      // 兼容数组格式响应 [data, status]
      return {
        success: true,
        data: response[0] || null,
        status: response[1] || 200,
        message: '操作成功',
        version: '1.0.0'
      };
    } else if (response && typeof response === 'object') {
      // 兼容对象格式响应
      return {
        success: response.success !== false,
        data: response.data || response,
        status: response.status || 200,
        message: response.message || (response.success === false ? '操作失败' : '操作成功'),
        version: response.version || '1.0.0'
      };
    } else {
      // 兼容原始数据格式
      return {
        success: true,
        data: response,
        status: 200,
        message: '操作成功',
        version: '1.0.0'
      };
    }
  }

  /**
   * 标准化API错误
   * @param {Error} error - 原始API错误
   * @returns {Error} 标准化后的错误
   */
  static standardizeError(error) {
    // 创建结构化错误信息
    const errorInfo = {
      message: '请求失败',
      details: '',
      type: 'unknown',
      status: error.response?.status || 0
    };

    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response;
      errorInfo.status = status;
      
      switch (status) {
        case 401:
          errorInfo.message = '未授权访问';
          errorInfo.details = '请检查您的身份验证信息';
          errorInfo.type = 'unauthorized';
          break;
        case 403:
          errorInfo.message = '禁止访问';
          errorInfo.details = '您没有权限执行此操作';
          errorInfo.type = 'forbidden';
          break;
        case 404:
          errorInfo.message = '资源不存在';
          errorInfo.details = '请求的资源未找到';
          errorInfo.type = 'not_found';
          break;
        case 500:
          errorInfo.message = '服务器错误';
          errorInfo.details = '服务器内部出现问题，请稍后重试';
          errorInfo.type = 'server_error';
          break;
        case 502:
        case 503:
        case 504:
          errorInfo.message = '服务不可用';
          errorInfo.details = '服务器暂时无法响应，请稍后重试';
          errorInfo.type = 'service_unavailable';
          break;
        default:
          errorInfo.message = '请求失败';
          errorInfo.details = data?.message || '未知错误';
          errorInfo.type = 'http_error';
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorInfo.message = '网络错误';
      errorInfo.details = '请检查您的网络连接';
      errorInfo.type = 'network_error';
    } else {
      // 请求配置错误
      errorInfo.message = '请求配置错误';
      errorInfo.details = error.message;
      errorInfo.type = 'config_error';
    }
    
    // 增强错误对象
    error.errorInfo = errorInfo;
    logger.error('API错误详情', errorInfo);
    
    return error;
  }
}

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    logger.info('API响应', {
      status: response.status,
      url: response.config.url,
      responseTime: response.headers['x-response-time'] || 'Unknown'
    });
    // 标准化API响应
    const standardizedResponse = ApiResponseAdapter.standardizeResponse(response.data);
    return standardizedResponse;
  },
  (error) => {
    // 统一错误处理，标准化错误
    const standardizedError = ApiResponseAdapter.standardizeError(error);
    return Promise.reject(standardizedError);
  }
);

// 统一错误处理函数
function handleApiError(error) {
  const standardizedError = ApiResponseAdapter.standardizeError(error);
  const errorInfo = standardizedError.errorInfo;
  
  // 使用logger记录错误，包含更多详细信息
  logger.error('API错误', {
    message: error.message,
    errorInfo: errorInfo,
    url: error.config?.url,
    method: error.config?.method,
    status: error.response?.status,
    stack: error.stack
  });
  
  return errorInfo;
}

/**
 * 构建请求配置
 * @param {Object} options - 请求配置选项
 * @param {string} options.method - HTTP方法
 * @param {string} options.url - 请求URL
 * @param {Object} [options.data] - 请求体数据
 * @param {Object} [options.params] - URL参数
 * @param {Object} [options.headers] - 请求头
 * @param {number} [options.timeout] - 超时时间
 * @param {Object} [options.cancelToken] - 取消令牌
 * @param {Object} [options.auth] - 认证信息
 * @returns {Object} 完整的请求配置对象
 */
function buildRequestConfig(options) {
  const { 
    method = 'GET', 
    url, 
    data, 
    params, 
    headers, 
    timeout, 
    cancelToken, 
    auth 
  } = options;
  
  // 构建基础配置
  const config = {
    method,
    url,
    headers: {
      ...API_CONFIG.HEADERS,
      ...headers
    }
  };
  
  // 添加数据（如果有）
  if (data) {
    config.data = data;
  }
  
  // 添加URL参数（如果有）
  if (params) {
    config.params = params;
  }
  
  // 添加超时时间（如果有）
  if (timeout) {
    config.timeout = timeout;
  }
  
  // 添加取消令牌（如果有）
  if (cancelToken) {
    config.cancelToken = cancelToken;
  }
  
  // 添加认证信息（如果有）
  if (auth) {
    config.auth = auth;
  }
  
  return config;
}

// 导出API响应适配器
export { ApiResponseAdapter };

// 创建API请求重试函数 - 优化版：支持多种重试策略和配置
async function requestWithRetry(config, options = {}) {
  // 默认重试配置
  const defaultOptions = {
    ...API_CONFIG.RETRY_CONFIG,
    onRetry: null, // 重试回调
    ...options
  };
  
  let attempt = 0;
  let lastError;
  const startTime = Date.now();

  while (attempt <= defaultOptions.maxRetries) {
    try {
      attempt++;
      
      logger.info(`API请求尝试 ${attempt}/${defaultOptions.maxRetries + 1}: ${config.method?.toUpperCase()} ${config.url}`);
      
      if (attempt > 1) {
        // 计算重试延迟：指数退避 + 随机抖动
        const delay = Math.min(
          defaultOptions.initialDelay * Math.pow(defaultOptions.backoffFactor, attempt - 2),
          defaultOptions.maxDelay
        );
        // 添加随机抖动，减少重试风暴
        const jitter = delay * defaultOptions.jitter * (Math.random() * 2 - 1); // ±10% 随机抖动
        const finalDelay = Math.max(defaultOptions.initialDelay, delay + jitter);
        
        logger.warn(`请求失败，正在进行第 ${attempt}/${defaultOptions.maxRetries + 1} 次重试，${Math.round(finalDelay/1000)}秒后重试...`);
        
        // 调用重试回调
        if (typeof defaultOptions.onRetry === 'function') {
          defaultOptions.onRetry(attempt, finalDelay, config);
        }
        
        await new Promise(resolve => setTimeout(resolve, finalDelay));
      }

      const response = await api.request(config);
      logger.info(`API请求成功: ${config.method?.toUpperCase()} ${config.url} (耗时: ${Date.now() - startTime}ms)`);
      return response;
    } catch (error) {
      // 增强错误信息
      handleApiError(error);
      
      // 检查是否是可重试的错误
      const isRetryable = 
        // 网络错误或超时
        (!error.response && (error.code === 'ECONNABORTED' || error.message.includes('Network Error') || error.message.includes('fetch failed'))) ||
        // 重试状态码
        (error.response && defaultOptions.retryableStatusCodes.includes(error.response.status)) ||
        // 请求方法允许重试
        defaultOptions.retryableMethods.includes(config.method);
      
      if (!isRetryable || attempt > defaultOptions.maxRetries) {
        logger.error(`API请求失败，已达到最大重试次数 (${defaultOptions.maxRetries}): ${config.method?.toUpperCase()} ${config.url} (耗时: ${Date.now() - startTime}ms)`);
        lastError = error;
        break;
      }

      logger.warn(`API请求失败，将在下次重试: ${config.method?.toUpperCase()} ${config.url} (错误: ${error.message})`);
      lastError = error;
    }
  }

  throw lastError;
}



// 处理SSE流式响应的方法（使用传统fetch）
export function handleStreamingResponse(url, data, onMessage, onError, onComplete) {
  // 创建AbortController用于取消请求
  const controller = new AbortController();
  const signal = controller.signal;
  
  // 用于存储累积的数据
  let buffer = '';
  
  // 发送流式请求
  fetch('/api' + url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data),
    signal: signal
  }).then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // 检查响应是否支持流式处理
    if (!response.body) {
      throw new Error('响应体不支持流式处理');
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    // 处理流式响应数据
    function processStream() {
      reader.read().then(({ done, value }) => {
        if (done) {
          // 处理缓冲区中剩余的数据
          if (buffer.trim()) {
            processStreamData('');
          }
          onComplete?.();
          return;
        }
        
        try {
          // 解码二进制数据
          const chunk = decoder.decode(value, { stream: true });
          if (chunk) {
            processStreamData(chunk);
          }
        } catch (error) {
          logger.error('解码数据失败:', error);
          onError?.(error);
        }
        
        // 继续处理下一块数据
        processStream();
      }).catch(error => {
        if (!signal.aborted) {
          logger.error('读取流数据失败:', error);
          onError?.(error);
        }
      });
    }
    
    // 开始处理流式数据
    processStream();
  }).catch(error => {
    if (!signal.aborted) {
      logger.error('流式请求失败:', error);
      onError?.(error);
    }
  });
  
  // 处理流式数据的函数
  function processStreamData(text) {
    buffer += text;
    
    // 分割数据块（根据SSE格式）
    const lines = buffer.split('\n\n');
    
    // 处理所有完整的数据行
    for (let i = 0; i < lines.length - 1; i++) {
      const line = lines[i];
      if (line.startsWith('data: ')) {
        const dataPart = line.slice(6); // 移除 'data: ' 前缀
        
        try {
          const parsedData = JSON.parse(dataPart);
          logger.debug('接收到流式数据块:', parsedData); // 添加日志追踪
          onMessage(parsedData);
        } catch (error) {
          logger.error('解析SSE消息失败:', error);
          onError?.(error);
        }
      }
    }
    
    // 保留不完整的行在缓冲区
    buffer = lines[lines.length - 1];
  }
  
  // 返回关闭函数
  return () => {
    controller.abort(); // 取消请求
  };
}

// 提取公共文件处理函数
async function processFiles(files) {
  return await Promise.all(
    files.map(async (file) => {
      if (file instanceof File) {
        // 将File对象转换为base64
        const content = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            // 移除data URL前缀，只保留base64内容
            const base64Content = reader.result.split(',')[1];
            resolve(base64Content);
          };
          reader.readAsDataURL(file);
        });
        return {
          name: file.name,
          content: content,
          type: file.type,
          size: file.size
        };
      }
      return file;
    })
  );
}

// API服务方法
export const apiService = {
  // 健康检查方法 - 优化版：使用已有端点作为健康检查，避免404
  healthCheck: async () => {
    try {
      // 使用较短的超时时间进行健康检查
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.HEALTH_CHECK_TIMEOUT);
      
      try {
        // 首先尝试调用健康检查端点，使用axios统一API调用方式
        // 注意：axios实例已经配置了baseURL: '/api'，所以这里不需要再添加/api前缀
        const healthResponse = await api.get('/health', {
          signal: controller.signal,
          timeout: API_CONFIG.HEALTH_CHECK_TIMEOUT
        });
        
        clearTimeout(timeoutId);
        
        logger.info('使用 /health 端点进行健康检查，服务正常');
        return healthResponse;
      } catch {
        // 如果健康检查端点不存在，尝试使用模型列表端点作为替代
        logger.info('使用备用端点 /models 进行健康检查...');
        
        // 重置控制器和超时
        clearTimeout(timeoutId);
        
        try {
          // 使用axios调用模型列表端点，不需要添加/api前缀
          await api.get('/models', {
            timeout: API_CONFIG.FALLBACK_HEALTH_CHECK_TIMEOUT
          });
          
          logger.info('使用 /models 端点进行健康检查，服务正常');
          return { status: 'healthy', message: 'Backend service is running (fallback check)' };
        } catch (error) {
          throw new Error(`Fallback health check failed with status: ${error.response?.status || 0}`);
        }
      }
    } catch (error) {
      logger.warn('健康检查失败:', error.message || error);
      throw error;
    }
  },
  
  // 暴露请求重试方法，以便在需要时直接使用
  requestWithRetry: requestWithRetry,
  // 聊天相关API
  chat: {
    createChat: async (title = '新对话') => {
      return await requestWithRetry({
        method: 'POST',
        url: '/api/chats',
        data: { title },
      });
    },
    
    sendMessage: async (chatId, message, files, options = {}) => {
      const { model = 'GPT-4', stream = false, modelParams = {}, ragConfig = {}, deepThinking = false } = options;
      
      // 使用合并后的单个端点，通过stream参数控制响应类型
      const endpoint = `/api/chats/${chatId}/messages`;
      
      // 处理文件，转换为可序列化的格式
      const processedFiles = await processFiles(files);
      
      return await requestWithRetry({
        method: 'POST',
        url: endpoint,
        data: {
          message,
          model,
          modelParams,
          ragConfig,
          files: processedFiles,
          stream, // 传递stream参数给后端
          deepThinking // 传递deepThinking参数给后端
        },
      });
    },
    
    // 发送流式消息
    sendStreamingMessage: async (chatId, message, files, options = {}, onMessage, onError, onComplete) => {
      const { model = 'GPT-4', modelParams = {}, ragConfig = {}, deepThinking = false } = options;
      
      // 处理文件，转换为可序列化的格式
      const processedFiles = await processFiles(files);
      
      const url = `/api/chats/${chatId}/messages`;
      const data = {
        message,
        files: processedFiles,
        model,
        modelParams,
        ragConfig,
        stream: true,  // 传递stream参数给后端
        deepThinking // 传递deepThinking参数给后端
      };
      
      // 创建一个Promise来包装流式请求
      return new Promise((resolve, reject) => {
        try {
          const closeConnection = handleStreamingResponse(url, data, onMessage, onError, () => {
            onComplete?.();
            resolve();
          });
          
          // 存储关闭连接的方法，以便在需要时手动关闭
          apiService.chat.activeStreamingConnection = closeConnection;
        } catch (error) {
          logger.error('创建流式连接失败:', error);
          reject(error);
        }
      });
    },
    
    // 关闭活动的流式连接
    closeStreamingConnection: () => {
      if (apiService.chat.activeStreamingConnection) {
        apiService.chat.activeStreamingConnection();
        apiService.chat.activeStreamingConnection = null;
      }
    },
    getHistory: async () => {
      return await requestWithRetry({
        method: 'GET',
        url: '/api/chats',
      });
    },
    deleteChat: async (chatId) => {
      return await requestWithRetry({
        method: 'DELETE',
        url: `/api/chats/${chatId}`,
      });
    },
    
    // 删除所有对话
    deleteAllChats: async () => {
      return await requestWithRetry({
        method: 'DELETE',
        url: '/api/chats/delete-all',
      });
    },
    
    // 更新对话置顶状态
    updateChatPin: async (chatId, pinned) => {
      return await requestWithRetry({
        method: 'PATCH',
        url: `/api/chats/${chatId}/pin`,
        data: { pinned },
      });
    },
  },
  
  // RAG相关API
  rag: {
      uploadFile: async (file, folder_id = '') => {
        const formData = new FormData();
        formData.append('file', file);
        // 如果提供了folder_id参数，将其添加到FormData中
        if (folder_id) {
          formData.append('folder_id', folder_id);
        }

        return await requestWithRetry({
          method: 'POST',
          url: '/api/files/upload',
          data: formData,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      },
    getDocuments: async () => {
      return await requestWithRetry({
        method: 'GET',
        url: '/api/files/documents',
      });
    },
    deleteDocument: async (filename, foldername = '') => {
      return await requestWithRetry({
        method: 'DELETE',
        url: `/api/files/${foldername}/${filename}`,
      });
    },
    getFolders: async () => {
      return await requestWithRetry({
        method: 'GET',
        url: '/api/files/folders',
      });
    },
  },

  // 模型相关API
  models: {
    getModels: async () => {
      return await requestWithRetry({
        method: 'GET',
        url: '/api/models',
      });
    },
  },

  // 通用请求方法
  get: async (url, params = {}) => {
    const config = buildRequestConfig({ method: 'GET', url, params });
    return await requestWithRetry(config);
  },
  post: async (url, data = {}) => {
    const config = buildRequestConfig({ method: 'POST', url, data });
    return await requestWithRetry(config);
  },
  put: async (url, data = {}) => {
    const config = buildRequestConfig({ method: 'PUT', url, data });
    return await requestWithRetry(config);
  },
  delete: async (url) => {
      const config = buildRequestConfig({ method: 'DELETE', url });
      return await requestWithRetry(config);
    },
  };

export default api;
