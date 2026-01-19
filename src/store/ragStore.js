import { defineStore } from 'pinia';
import { generateId } from './utils';
import { eventBus } from '../services/eventBus.js';
import { apiService } from '../services/apiService.js';

export const useRagStore = defineStore('rag', {
  state: () => ({
    // RAG相关文件列表
    files: [],
    // 文件夹列表
    folders: [],
    // 文件夹ID到名称的映射
    folderIdMap: {},
    // 当前文件夹
    currentFolder: null,
    // 当前选中的文件夹（用于RAG检索范围）
    currentSelectedFolder: null,
    // 加载状态
    loading: false,
    // 错误信息
    error: null,
    // 上传进度
    uploadProgress: 0,
    // 支持的文件类型
    supportedFileTypes: ['pdf', 'docx', 'txt', 'csv', 'xlsx', 'pptx', 'md'],
    // 最大文件大小（50MB）
    maxFileSize: 50 * 1024 * 1024,
  }),

  getters: {
    // 获取文件数量
    fileCount: (state) => {
      return state.files.length;
    },

    // 获取加载状态
    isLoading: (state) => {
      return state.loading;
    },

    // 获取错误信息
    getError: (state) => {
      return state.error;
    },

    // 按文件类型分组的文件列表
    filesByType: (state) => {
      return state.files.reduce((groups, file) => {
        const type = file.type || 'other';
        if (!groups[type]) {
          groups[type] = [];
        }
        groups[type].push(file);
        return groups;
      }, {});
    },
  },

  actions: {
    // 设置错误信息
    setError(error) {
      this.error = error;
    },

    // 加载文件夹列表
    async loadFolders() {
      this.loading = true;
      this.clearError();

      try {
        // 从后端API获取文件夹列表
        const response = await apiService.rag.getFolders();
        // 确保正确处理响应格式
        const folders = response.success && response.folders ? response.folders : [];
        
        // 建立文件夹ID到名称的映射
        this.folderIdMap = {};
        folders.forEach(folder => {
          if (folder.id) {
            this.folderIdMap[folder.id] = folder.name;
          }
        });
        
        return folders;
      } catch (error) {
        console.error('加载文件夹失败:', error);
        this.setError(`加载文件夹失败: ${error.message || '未知错误'}`);
        return [];
      } finally {
        this.loading = false;
      }
    },

    // 加载指定文件夹中的文件（只支持通过folder_id获取）
  async loadFilesInFolder(folder) {
    if (!folder || !folder.id) return [];
    this.loading = true;
    this.clearError();

    try {
      // 直接使用folder_id调用API端点
      const response = await apiService.get(`/api/rag/folders/by-id/${encodeURIComponent(folder.id)}/files`);
      
      // 确保正确处理响应格式
      const files = response.success && response.files ? response.files : [];
      
      // 确保currentFolder设置为正确的文件夹名称
      this.currentFolder = this.folderIdMap[folder.id] || folder.name || null;
      
      // 更新文件夹映射（如果API返回了相关信息）
      if (response.data && response.data.folder_id_map) {
        this.folderIdMap = { ...this.folderIdMap, ...response.data.folder_id_map };
      }
      
      return files;
    } catch (error) {
      console.error('加载文件夹中的文件失败:', error);
      this.setError(`加载文件夹中的文件失败: ${error.message || '未知错误'}`);
      return [];
    } finally {
      this.loading = false;
    }
  },
  
  // 根据文件夹ID获取文件夹名称
  getFolderNameById(folderId) {
    return this.folderIdMap[folderId] || null;
  },
  
  // 根据文件夹名称获取文件夹对象（包含ID）
  getFolderByName(folderName) {
    return this.folders.find(folder => folder.name === folderName) || null;
  },

    // 清空错误信息
    clearError() {
      this.error = null;
    },

    // 设置上传进度
    setUploadProgress(progress) {
      this.uploadProgress = progress;
    },

    // 重置上传进度
    resetUploadProgress() {
      this.uploadProgress = 0;
    },

    // 验证文件格式和大小
    validateFile(file) {
      if (!file) {
        return { valid: false, message: '文件不能为空' };
      }

      // 检查文件大小
      if (file.size > this.maxFileSize) {
        return {
          valid: false,
          message: `文件大小不能超过${(this.maxFileSize / (1024 * 1024)).toFixed(0)}MB`,
        };
      }

      // 检查文件类型
      const fileExtension = file.name.split('.').pop().toLowerCase();
      if (!this.supportedFileTypes.includes(fileExtension)) {
        return {
          valid: false,
          message: `不支持的文件类型。支持的类型：${this.supportedFileTypes.join(', ')}`,
        };
      }

      return { valid: true };
    },

    // 加载RAG文件列表 - 从后端API获取
    async loadFiles() {
      this.loading = true;
      this.clearError();

      try {
        // 从后端API获取文件列表
        const response = await apiService.rag.getDocuments();
        // 确保正确处理响应格式
        const documents = response.success && response.documents ? response.documents : [];
        
        if (documents && Array.isArray(documents)) {
          // 处理从API获取的文件数据
          const files = documents.map((file) => ({
            id: generateId('file'),
            name: file.name,
            path: file.path || '',
            size: file.size || 0,
            type: file.type || (file.name ? file.name.split('.').pop()?.toLowerCase() : 'unknown'),
            uploadedAt: file.uploadedAt || Date.now(),
            folderId: file.folderId || null
          }));
          this.files = files;
        }
        
        // 如果API返回了folder_id_map，则更新本地映射
        if (response.data && response.data.folder_id_map) {
          this.folderIdMap = { ...this.folderIdMap, ...response.data.folder_id_map };
        }
      } catch (error) {
        console.error('加载RAG文件失败:', error);
        this.setError(`加载文件失败: ${error.message || '未知错误'}`);
        this.files = [];
      } finally {
        this.loading = false;
      }
    },

    // 删除单个文件
    async deleteFile(fileId, folderParam = '') {
      this.loading = true;
      this.clearError();

      try {
        // 查找要删除的文件
        const fileToDelete = this.files.find(file => file.id === fileId);
        if (fileToDelete) {
          // 确定文件夹名称 - 支持通过id或名称
          let foldername = '';
          
          // 如果folderParam是UUID格式（8位），则认为是folderId，需要转换为folderName
          if (folderParam && /^[a-zA-Z0-9]{8}$/.test(folderParam)) {
            // 遍历folderIdMap获取对应的folderName
            for (const [id, name] of Object.entries(this.folderIdMap)) {
              if (id === folderParam) {
                foldername = name;
                break;
              }
            }
          } else {
            // 否则直接使用folderParam作为foldername
            foldername = folderParam;
          }
          
          // 调用后端API删除文件，传递文件名和文件夹名
          await apiService.rag.deleteDocument(fileToDelete.name, foldername);
          // 从状态中移除文件
          this.files = this.files.filter((file) => file.id !== fileId);
          // 重新加载文件列表以确保同步
          await this.loadFiles();
        }
      } catch (error) {
        console.error('删除文件失败:', error);
        this.setError(`删除文件失败: ${error.message || '未知错误'}`);
      } finally {
        this.loading = false;
      }
    },

    // 删除所有文件和文件夹，并清空向量数据库
    async deleteAllFiles() {
      this.loading = true;
      this.clearError();

      try {
        // 调用后端API删除所有文件
        const response = await apiService.delete('/api/rag/documents/delete-all');
        
        // 清空文件列表和文件夹相关状态
        this.files = [];
        this.folders = [];
        this.folderIdMap = {};
        
        // 重新加载文件列表和文件夹列表以确保同步
        await Promise.all([this.loadFiles(), this.loadFolders()]);
        
        return {
          success: true,
          message: response.data?.message || '所有文件、文件夹和向量数据库已清空',
          deleted_count: response.data?.deleted_count || 0
        };
      } catch (error) {
        console.error('删除所有文件失败:', error);
        const errorMessage = error.response?.data?.error || error.message || '未知错误';
        this.setError(`删除所有文件失败: ${errorMessage}`);
        return {
          success: false,
          error: errorMessage
        };
      } finally {
        this.loading = false;
      }
    },

    // 上传文件
  async uploadFile(file, folder_id = '') {
    // 验证文件
    const validation = this.validateFile(file);
    if (!validation.valid) {
      this.setError(validation.message);
      return false;
    }

    this.loading = true;
    this.clearError();
    this.resetUploadProgress();

    try {
      // 调用后端API上传文件，传递folder_id参数
      await apiService.rag.uploadFile(file, folder_id);
      
      // 重新加载文件列表以确保同步
      await this.loadFiles();
      return true;
    } catch (error) {
      console.error('上传文件失败:', error);
      this.setError(`上传文件失败: ${error.message || '未知错误'}`);
      return false;
    } finally {
      this.loading = false;
      this.resetUploadProgress();
    }
  },

  // 创建知识库
  async createKnowledgeBase(knowledgeBaseName) {
    try {
      let response;
      
      // 尝试使用Tauri invoke调用Rust函数
      try {
        // 动态导入invoke，避免在非Tauri环境中报错
        const { invoke } = await import('@tauri-apps/api/core');
        response = await invoke('create_knowledge_base', {
          name: knowledgeBaseName
        });
      } catch (importError) {
        // 如果导入失败，回退到使用Python API
        console.warn('无法使用Tauri invoke，回退到Python API:', importError);
        response = await apiService.post('/api/rag/folders', {
          name: knowledgeBaseName
        });
      }
      
      // 通知事件总线知识库已创建
      eventBus.emit('knowledge-base-created', {
        id: response.id || null,
        name: response.name || knowledgeBaseName,
        path: response.path || `resources/python/userData/rag/ragFiles/${knowledgeBaseName}`
      });
      
      // 重新加载文件夹列表以确保同步
      await this.loadFolders();
      
      return {
        success: true,
        id: response.id || null,
        name: response.name || knowledgeBaseName,
        path: response.path || `resources/python/userData/rag/ragFiles/${knowledgeBaseName}`
      };
    } catch (error) {
      console.error('创建知识库失败:', error);
      this.setError(`创建知识库失败: ${error.message || '未知错误'}`);
      return {
        success: false,
        error: error.message || String(error)
      };
    }
  },



    // 搜索文件内容
    async searchFileContent(query) {
      if (!query.trim()) return [];

      this.loading = true;
      this.clearError();

      try {
        // 调用后端API搜索文件内容
        const response = await apiService.get('/api/rag/search', {
          params: { query }
        });
        
        // 确保正确处理响应格式
        return response.success && response.results ? response.results : [];
      } catch (error) {
        console.error('搜索文件内容失败:', error);
        this.setError(`搜索失败: ${error.message || '未知错误'}`);
        return [];
      } finally {
        this.loading = false;
      }
    },

    // 获取文件详情
    async getFileDetails(fileId) {
      if (!fileId) return null;

      this.loading = true;
      this.clearError();

      try {
        // 首先根据fileId查找文件
        const file = this.files.find(f => f.id === fileId);
        if (!file) {
          this.setError(`文件不存在: ${fileId}`);
          return null;
        }
        
        // 调用后端API获取文件详情
        const response = await apiService.get(`/api/rag/documents/${fileId}`);
        // 确保正确处理响应格式
        const fileDetails = response.success && response.details ? response.details : null;
        
        return {
          ...file,
          ...fileDetails,
          id: file.id
        };
      } catch (error) {
        console.error('获取文件详情失败:', error);
        this.setError(`获取文件详情失败: ${error.message || '未知错误'}`);
        return null;
      } finally {
        this.loading = false;
      }
    },

    // 设置当前文件夹
    setCurrentFolder(folder) {
      this.currentFolder = folder;
    },

    // 选择文件夹
    selectFolder(folder) {
      this.currentFolder = folder;
    },
    
    // 设置当前选中的文件夹（用于RAG检索范围）
    setCurrentSelectedFolder(folder) {
      this.currentSelectedFolder = folder;
    },

    // 进入文件夹
    async enterFolder(folder) {
      this.currentFolder = folder;
      // 加载文件夹中的文件
      if (folder) {
        await this.loadFilesInFolder(folder);
      }
    },

    // 上传文件到指定文件夹
    async uploadFilesToFolder(folder, files) {
      if (!folder || !files || files.length === 0) return;
      
      // 使用batchUploadFiles方法上传文件到指定文件夹
      await this.batchUploadFiles(files, folder.id || folder.name);
    },

    // 删除文件夹
    async deleteFolder(folder) {
      if (!folder || !folder.id) return;
      
      this.loading = true;
      this.clearError();
      
      try {
        // 调用后端API删除文件夹
        await apiService.delete(`/api/rag/folders/${folder.id}`);
        
        // 重新加载文件夹列表和文件列表以确保同步
        await Promise.all([this.loadFolders(), this.loadFiles()]);
      } catch (error) {
        console.error('删除文件夹失败:', error);
        this.setError(`删除文件夹失败: ${error.message || '未知错误'}`);
      } finally {
        this.loading = false;
      }
    },

    // 批量上传文件
    async batchUploadFiles(files, folder = '') {
      if (!files || files.length === 0) return;

      this.loading = true;
      this.clearError();

      try {
        const successFiles = [];
        const failedFiles = [];
        
        for (const file of files) {
          try {
            // 验证文件
            const validation = this.validateFile(file);
            if (!validation.valid) {
              console.error('文件验证失败:', validation.message);
              failedFiles.push(file.name);
              continue;
            }
            
            // 调用后端API上传单个文件，传递folder参数
            await apiService.rag.uploadFile(file, folder);
            successFiles.push(file.name);
          } catch (error) {
            console.error(`处理文件 ${file.name || '未知文件'} 时出错:`, error);
            failedFiles.push(file.name || '未知文件');
          }
        }
        
        // 重新加载文件列表以确保同步
        await this.loadFiles();
        
        // 检查上传结果
        const hasSuccess = successFiles.length > 0;
        const hasFailed = failedFiles.length > 0;

        if (hasFailed && !hasSuccess) {
          this.setError('所有文件上传失败，请重试');
        } else if (hasFailed) {
          this.setError('部分文件上传失败，请检查');
        }
      } catch (error) {
        console.error('批量上传文件失败:', error);
        this.setError(`批量上传失败: ${error.message || '未知错误'}`);
      } finally {
        this.loading = false;
      }
    },
  },
});
