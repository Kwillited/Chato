/**
 * RAG增强模块的类型定义
 */

/**
 * 知识库类型
 * @typedef {Object} KnowledgeBase
 * @property {string} id - 知识库ID
 * @property {string} name - 知识库名称
 * @property {string} description - 知识库描述
 * @property {number} fileCount - 文件数量
 * @property {Date} createdAt - 创建时间
 * @property {Date} updatedAt - 更新时间
 * @property {Object} [metadata] - 知识库元数据
 */

/**
 * 知识库文件类型
 * @typedef {Object} KnowledgeBaseFile
 * @property {string} id - 文件ID
 * @property {string} name - 文件名
 * @property {string} extension - 文件扩展名
 * @property {number} size - 文件大小（字节）
 * @property {string} status - 文件状态（pending, processing, completed, failed）
 * @property {number} chunkCount - 分块数量
 * @property {Date} uploadedAt - 上传时间
 * @property {Date} [processedAt] - 处理完成时间
 * @property {Object} [metadata] - 文件元数据
 */

/**
 * 文件上传进度类型
 * @typedef {Object} FileUploadProgress
 * @property {number} percentage - 上传百分比 (0-100)
 * @property {number} loaded - 已上传字节数
 * @property {number} total - 总字节数
 * @property {string} status - 上传状态 (idle, uploading, completed, error)
 * @property {string} [error] - 错误信息
 */

/**
 * RAG查询选项类型
 * @typedef {Object} RagQueryOptions
 * @property {string[]} knowledgeBaseIds - 知识库ID列表
 * @property {number} [topK=5] - 返回的相关片段数量
 * @property {number} [scoreThreshold=0.5] - 相关性分数阈值
 * @property {boolean} [includeMetadata=false] - 是否包含元数据
 * @property {Object} [filter] - 过滤条件
 */

/**
 * RAG检索结果类型
 * @typedef {Object} RagRetrievalResult
 * @property {string} id - 结果ID
 * @property {string} content - 检索到的内容
 * @property {number} score - 相关性分数
 * @property {string} knowledgeBaseId - 知识库ID
 * @property {string} fileId - 文件ID
 * @property {string} fileName - 文件名
 * @property {Object} [metadata] - 元数据
 * @property {number} [startIndex] - 内容起始位置
 * @property {number} [endIndex] - 内容结束位置
 */

export const FileStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed'
};

export const UploadStatus = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  COMPLETED: 'completed',
  ERROR: 'error'
};
