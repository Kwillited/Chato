/**
 * 对话模块的类型定义
 */

/**
 * 聊天消息类型
 * @typedef {Object} ChatMessage
 * @property {string} id - 消息ID
 * @property {'user' | 'ai'} role - 消息角色
 * @property {string} content - 消息内容
 * @property {Date} timestamp - 消息时间戳
 * @property {Object} [metadata] - 消息元数据
 * @property {Array<Object>} [attachments] - 消息附件
 * @property {Array<string>} [references] - 引用的消息ID
 */
export const ChatMessageType = {
  USER: 'user',
  AI: 'ai'
};

/**
 * 聊天会话类型
 * @typedef {Object} ChatSession
 * @property {string} id - 会话ID
 * @property {string} title - 会话标题
 * @property {Array<ChatMessage>} messages - 会话消息
 * @property {Date} createdAt - 创建时间
 * @property {Date} updatedAt - 更新时间
 * @property {Object} [metadata] - 会话元数据
 */

/**
 * 发送消息选项
 * @typedef {Object} SendMessageOptions
 * @property {boolean} [stream=true] - 是否使用流式响应
 * @property {string} [model] - 使用的模型
 * @property {number} [temperature=0.7] - 生成温度
 * @property {number} [maxTokens] - 最大生成令牌数
 * @property {Array<string>} [stop] - 停止词
 * @property {Object} [ragOptions] - RAG相关选项
 * @property {Object} [toolOptions] - 工具调用选项
 */

/**
 * 聊天历史查询选项
 * @typedef {Object} ChatHistoryOptions
 * @property {number} [limit=50] - 返回消息数量限制
 * @property {number} [offset=0] - 消息偏移量
 * @property {boolean} [includeMetadata=false] - 是否包含元数据
 */

/**
 * 聊天API响应类型
 * @typedef {Object} ChatApiResponse
 * @property {boolean} success - 是否成功
 * @property {any} data - 响应数据
 * @property {string} [error] - 错误信息
 * @property {string} [traceId] - 追踪ID
 */
