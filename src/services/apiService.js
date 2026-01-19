import axios from 'axios';
import { useSettingsStore } from '../store/settingsStore.js';

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
    const settingsStore = useSettingsStore();

    // 显示全局加载状态（如果需要）
    if (settingsStore) {
      settingsStore.setLoading(true);
    }

    console.log('API请求:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    // 请求错误时隐藏加载状态
    const settingsStore = useSettingsStore();
    if (settingsStore) {
      settingsStore.setLoading(false);
    }

    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 隐藏全局加载状态
    const settingsStore = useSettingsStore();
    if (settingsStore) {
      settingsStore.setLoading(false);
    }

    console.log('API响应:', response.status, response.config.url);
    return response.data;
  },
  (error) => {
    // 隐藏全局加载状态
    const settingsStore = useSettingsStore();
    if (settingsStore) {
      settingsStore.setLoading(false);
    }

    // 统一错误处理
    handleApiError(error);
    return Promise.reject(error);
  }
);

// 统一错误处理函数
function handleApiError(error) {
  console.error('API错误:', error.message);

  if (error.response) {
    // 服务器返回错误状态码
    const { status, data } = error.response;

    switch (status) {
      case 401:
        console.error('未授权访问，请登录');
        // 可以在这里跳转到登录页面
        break;
      case 403:
        console.error('禁止访问');
        break;
      case 404:
        console.error('请求的资源不存在');
        break;
      case 500:
        console.error('服务器内部错误');
        break;
      default:
        console.error(`请求失败: ${data?.message || '未知错误'}`);
    }
  } else if (error.request) {
    // 请求已发送但没有收到响应
    console.error('网络错误，请检查您的网络连接');
  } else {
    // 请求配置错误
    console.error('请求配置错误:', error.message);
  }
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
    ...options
  };
  
  let attempt = 0;
  let lastError;

  while (attempt <= defaultOptions.maxRetries) {
    try {
      attempt++;
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
        await new Promise(resolve => setTimeout(resolve, finalDelay));
      }

      return await api.request(config);
    } catch (error) {
      // 检查是否是可重试的错误
      const isRetryable = 
        // 网络错误或超时
        (!error.response && (error.code === 'ECONNABORTED' || error.message.includes('Network Error') || error.message.includes('fetch failed'))) ||
        // 重试状态码
        (error.response && defaultOptions.retryableStatusCodes.includes(error.response.status)) ||
        // 请求方法允许重试
        defaultOptions.retryableMethods.includes(config.method);
      
      if (!isRetryable || attempt > defaultOptions.maxRetries) {
        lastError = error;
        break;
      }

      lastError = error;
    }
  }

  throw lastError;
}

// 判断是否为可重试的错误 - 保留此函数以兼容现有代码
function isRetryableError(error) {
  // 网络错误、超时、500系列错误可以重试
  return (
    !error.response || error.code === 'ECONNABORTED' || (error.response.status >= 500 && error.response.status < 600)
  );
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
      // 使用较短的超时时间进行健康检查
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      
      try {
        // 首先尝试调用健康检查端点
        const healthResponse = await fetch('/api/health', {
          method: 'GET',
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (healthResponse.ok) {
          console.log('使用 /api/health 端点进行健康检查，服务正常');
          return await healthResponse.json();
        }
      } catch (healthError) {
        // 如果健康检查端点不存在，尝试使用模型列表端点作为替代
        console.log('使用备用端点 /api/models 进行健康检查...');
        
        // 重置控制器和超时
        clearTimeout(timeoutId);
        const fallbackController = new AbortController();
        const fallbackTimeoutId = setTimeout(() => fallbackController.abort(), 5000);
        
        // 尝试调用模型列表端点
        const modelsResponse = await fetch('/api/models', {
          method: 'GET',
          signal: fallbackController.signal
        });
        
        clearTimeout(fallbackTimeoutId);
        
        if (modelsResponse.ok) {
          console.log('使用 /api/models 端点进行健康检查，服务正常');
          return { status: 'healthy', message: 'Backend service is running (fallback check)' };
        }
        throw new Error(`Fallback health check failed with status: ${modelsResponse.status}`);
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
        url: '/api/chats',
        data: { title },
      });
    },
    
    sendMessage: async (chatId, message, files, options = {}) => {
      const { model = 'GPT-4', stream = false, modelParams = {}, ragConfig = {}, deepThinking = false } = options;
      
      // 使用合并后的单个端点，通过stream参数控制响应类型
      const endpoint = `/api/chats/${chatId}/messages`;
      
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
    // 验证向量数据库路径是否有效
    validateVectorDbPath: async (path) => {
      return await requestWithRetry({
        method: 'POST',
        url: '/api/rag/validate-path',
        data: { path, type: 'vector_db' },
      });
    },
    // 验证知识库路径是否有效
    validateKnowledgeBasePath: async (path) => {
      return await requestWithRetry({
        method: 'POST',
        url: '/api/rag/validate-path',
        data: { path, type: 'knowledge_base' },
      });
    },
    // 获取系统实际使用的路径信息
    getActualPaths: async () => {
      return await requestWithRetry({
        method: 'GET',
        url: '/api/rag/paths',
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
    
    updateModelParams: async (model, params) => {
      return await requestWithRetry({
        method: 'POST',
        url: `/api/models/${model}/params`,
        data: params,
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
