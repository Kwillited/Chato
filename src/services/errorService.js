/**
 * 错误处理服务
 * 负责统一处理应用中的错误
 */

/**
 * 错误类型
 */
export const ErrorTypes = {
  NETWORK: 'network_error',
  API: 'api_error',
  STREAMING: 'streaming_error',
  VALIDATION: 'validation_error',
  UNKNOWN: 'unknown_error'
};

/**
 * 错误处理服务
 */
export const errorService = {
  /**
   * 处理错误
   * @param {Error} error - 错误对象
   * @param {string} context - 错误上下文
   * @returns {Object} 处理后的错误信息
   */
  handleError: (error, context = '') => {
    console.error(`${context} 错误:`, error);
    
    // 创建结构化错误信息
    const errorInfo = {
      message: '操作失败',
      details: '',
      type: ErrorTypes.UNKNOWN,
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
          errorInfo.type = ErrorTypes.API;
          break;
        case 403:
          errorInfo.message = '禁止访问';
          errorInfo.details = '您没有权限执行此操作';
          errorInfo.type = ErrorTypes.API;
          break;
        case 404:
          errorInfo.message = '资源不存在';
          errorInfo.details = '请求的资源未找到';
          errorInfo.type = ErrorTypes.API;
          break;
        case 500:
          errorInfo.message = '服务器错误';
          errorInfo.details = '服务器内部出现问题，请稍后重试';
          errorInfo.type = ErrorTypes.API;
          break;
        case 502:
        case 503:
        case 504:
          errorInfo.message = '服务不可用';
          errorInfo.details = '服务器暂时无法响应，请稍后重试';
          errorInfo.type = ErrorTypes.NETWORK;
          break;
        default:
          errorInfo.message = '请求失败';
          errorInfo.details = data?.message || '未知错误';
          errorInfo.type = ErrorTypes.API;
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorInfo.message = '网络错误';
      errorInfo.details = '请检查您的网络连接';
      errorInfo.type = ErrorTypes.NETWORK;
    } else if (error.name === 'AbortError') {
      // 流式请求被取消
      errorInfo.message = '请求已取消';
      errorInfo.details = '操作已被用户取消';
      errorInfo.type = ErrorTypes.STREAMING;
    } else {
      // 请求配置错误或其他错误
      errorInfo.message = '操作失败';
      errorInfo.details = error.message || '未知错误';
      errorInfo.type = ErrorTypes.UNKNOWN;
    }
    
    // 增强错误对象
    error.errorInfo = errorInfo;
    console.error(`${context} 错误详情:`, errorInfo);
    
    return errorInfo;
  },
  
  /**
   * 处理流式错误
   * @param {Error} error - 错误对象
   * @returns {Object} 处理后的错误信息
   */
  handleStreamingError: (error) => {
    return errorService.handleError(error, '流式处理');
  },
  
  /**
   * 处理API错误
   * @param {Error} error - 错误对象
   * @returns {Object} 处理后的错误信息
   */
  handleApiError: (error) => {
    return errorService.handleError(error, 'API请求');
  },
  
  /**
   * 处理验证错误
   * @param {string} message - 错误消息
   * @returns {Object} 处理后的错误信息
   */
  handleValidationError: (message) => {
    const errorInfo = {
      message: '验证失败',
      details: message,
      type: ErrorTypes.VALIDATION,
      status: 400
    };
    
    console.error('验证错误:', errorInfo);
    return errorInfo;
  }
};
