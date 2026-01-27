import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // 增加超时时间到60秒，以确保非流式请求有足够时间完成
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    console.log('API请求:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.status, response.config.url);
    return response.data;
  },
  (error) => {
    // 统一错误处理
    handleApiError(error);
    return Promise.reject(error);
  }
);

// 统一错误处理函数
function handleApiError(error) {
  console.error('API错误:', error.message);
  
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
  console.error('API错误详情:', errorInfo);
  
  return errorInfo;
}

// 创建API请求重试函数 - 优化版：支持多种重试策略和配置
async function requestWithRetry(config, options = {}) {
  // 默认重试配置
  const defaultOptions = {
    maxRetries: 5,
    initialDelay: 500,
    backoffFactor: 1.5,
    maxDelay: 8000,
    jitter: 0.1, // ±10% 随机抖动
    retryableStatusCodes: [500, 502, 503, 504],
    retryableMethods: ['GET', 'POST', 'PUT', 'DELETE'],
    onRetry: null, // 重试回调
    ...options
  };
  
  let attempt = 0;
  let lastError;
  const startTime = Date.now();

  while (attempt <= defaultOptions.maxRetries) {
    try {
      attempt++;
      
      console.log(`API请求尝试 ${attempt}/${defaultOptions.maxRetries + 1}: ${config.method?.toUpperCase()} ${config.url}`);
      
      if (attempt > 1) {
        // 计算重试延迟：指数退避 + 随机抖动
        const delay = Math.min(
          defaultOptions.initialDelay * Math.pow(defaultOptions.backoffFactor, attempt - 2),
          defaultOptions.maxDelay
        );
        // 添加随机抖动，减少重试风暴
        const jitter = delay * defaultOptions.jitter * (Math.random() * 2 - 1); // ±10% 随机抖动
        const finalDelay = Math.max(defaultOptions.initialDelay, delay + jitter);
        
        console.warn(`请求失败，正在进行第 ${attempt}/${defaultOptions.maxRetries + 1} 次重试，${Math.round(finalDelay/1000)}秒后重试...`);
        
        // 调用重试回调
        if (typeof defaultOptions.onRetry === 'function') {
          defaultOptions.onRetry(attempt, finalDelay, config);
        }
        
        await new Promise(resolve => setTimeout(resolve, finalDelay));
      }

      const response = await api.request(config);
      console.log(`API请求成功: ${config.method?.toUpperCase()} ${config.url} (耗时: ${Date.now() - startTime}ms)`);
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
        console.error(`API请求失败，已达到最大重试次数 (${defaultOptions.maxRetries}): ${config.method?.toUpperCase()} ${config.url} (耗时: ${Date.now() - startTime}ms)`);
        lastError = error;
        break;
      }

      console.warn(`API请求失败，将在下次重试: ${config.method?.toUpperCase()} ${config.url} (错误: ${error.message})`);
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
  
  // 确保URL以/api开头
  const apiUrl = url.startsWith('/api') ? url : `/api${url}`;
  
  // 发送流式请求
  fetch(apiUrl, {
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
          console.error('解码数据失败:', error);
          onError?.(error);
        }
        
        // 继续处理下一块数据
        processStream();
      }).catch(error => {
        if (!signal.aborted) {
          console.error('读取流数据失败:', error);
          onError?.(error);
        }
      });
    }
    
    // 开始处理流式数据
    processStream();
  }).catch(error => {
    if (!signal.aborted) {
      console.error('流式请求失败:', error);
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
          console.log('接收到流式数据块:', parsedData); // 添加日志追踪
          onMessage(parsedData);
        } catch (error) {
          console.error('解析SSE消息失败:', error);
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

// API服务方法
export const apiService = {
  // 健康检查方法 - 优化版：使用已有端点作为健康检查，避免404
  healthCheck: async () => {
    try {
      // 首先尝试调用健康检查端点
      try {
        const healthResponse = await api.get('/health', {
          timeout: 3000
        });
        console.log('使用 /health 端点进行健康检查，服务正常');
        return healthResponse;
      } catch {
        // 如果健康检查端点不存在，尝试使用模型列表端点作为替代
        console.log('使用备用端点 /models 进行健康检查...');
        
        const modelsResponse = await api.get('/models', {
          timeout: 5000
        });
        
        console.log('使用 /models 端点进行健康检查，服务正常');
        return { status: 'healthy', message: 'Backend service is running (fallback check)' };
      }
    } catch (error) {
      console.warn('健康检查失败:', error.message || error);
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
        url: '/chats',
        data: { title },
      });
    },
    
    sendMessage: async (chatId, message, files, options = {}) => {
      const { model = 'GPT-4', stream = false, modelParams = {}, ragConfig = {}, deepThinking = false } = options;
      
      // 使用合并后的单个端点，通过stream参数控制响应类型
      const endpoint = `/chats/${chatId}/messages`;
      
      // 处理文件，转换为可序列化的格式
      const processedFiles = await Promise.all(
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
              type: file.type,  // 保留文件类型
              size: file.size  // 保留文件大小
            };
          }
          return file;
        })
      );
      
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
      const processedFiles = await Promise.all(
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
              size: file.size  // 保留文件大小
            };
          }
          return file;
        })
      );
      
      const url = `/chats/${chatId}/messages`;
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
          console.error('创建流式连接失败:', error);
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
        url: '/chats',
      });
    },
    deleteChat: async (chatId) => {
      return await requestWithRetry({
        method: 'DELETE',
        url: `/chats/${chatId}`,
      });
    },
    
    // 删除所有对话
    deleteAllChats: async () => {
      return await requestWithRetry({
        method: 'DELETE',
        url: '/chats/delete-all',
      });
    },
    
    // 更新对话置顶状态
    updateChatPin: async (chatId, pinned) => {
      return await requestWithRetry({
        method: 'PATCH',
        url: `/chats/${chatId}/pin`,
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
          url: '/files/upload',
          data: formData,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      },
    getDocuments: async () => {
      return await requestWithRetry({
        method: 'GET',
        url: '/files/documents',
      });
    },
    deleteDocument: async (filename, foldername = '') => {
      return await requestWithRetry({
        method: 'DELETE',
        url: `/files/${foldername}/${filename}`,
      });
    },
    getFolders: async () => {
      return await requestWithRetry({
        method: 'GET',
        url: '/files/folders',
      });
    },
  },

  // 模型相关API
  models: {
    getModels: async () => {
      return await requestWithRetry({
        method: 'GET',
        url: '/models',
      });
    },
  },

  // 通用请求方法
  get: async (url, params = {}) => {
    return await requestWithRetry({ method: 'GET', url, params });
  },
  post: async (url, data = {}) => {
    return await requestWithRetry({ method: 'POST', url, data });
  },
  put: async (url, data = {}) => {
    return await requestWithRetry({ method: 'PUT', url, data });
  },
  delete: async (url) => {
      return await requestWithRetry({ method: 'DELETE', url });
    },
  };

export default api;
