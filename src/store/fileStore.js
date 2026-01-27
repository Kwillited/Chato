import { defineStore } from 'pinia';
import { apiService } from '../services/apiService';
import { showNotification } from '../utils/notificationUtils.js';
import eventBus from '../services/eventBus.js';
import { errorUtils, loadingUtils, notificationUtils as notifyUtils, apiUtils } from '../utils/storeUtils.js';

export const useFileStore = defineStore('file', {
  state: () => ({
    // 状态
    files: [],
    folders: [],
    folderIdMap: {},
    currentFolder: null,
    currentFiles: [],
    loading: false,
    error: null,
    fileUploadProgress: null,
  }),
  
  getters: {
    // 获取当前文件夹中的文件数量
    currentFileCount: (state) => state.currentFiles.length,
    
    // 获取文件夹总数
    folderCount: (state) => state.folders.length,
    
    // 获取文件总数
    fileCount: (state) => state.files.length,
  },
  
  actions: {
    // 设置错误
    setError(message) {
      errorUtils.setError(this, message);
    },
    
    // 清除错误
    clearError() {
      errorUtils.clearError(this);
    },
    
    // 加载文件列表
    async loadFiles() {
      try {
        const response = await apiUtils.wrapApiCall(this, async () => {
          const res = await apiService.rag.getDocuments();
          if (res.success) {
            this.files = res.documents || [];
            this.folderIdMap = res.folder_id_map || {};
          } else {
            throw new Error('加载文件列表失败');
          }
          return res;
        }, '加载文件列表失败');
      } catch (error) {
        // 错误已在 wrapApiCall 中处理
      }
    },
    
    // 加载文件夹列表
    async loadFolders() {
      try {
        const response = await apiUtils.wrapApiCall(this, async () => {
          const res = await apiService.rag.getFolders();
          if (res.success) {
            this.folders = res.folders || [];
          } else {
            throw new Error('加载文件夹列表失败');
          }
          return res;
        }, '加载文件夹列表失败');
      } catch (error) {
        // 错误已在 wrapApiCall 中处理
      }
    },
    
    // 加载文件夹中的文件
    async loadFilesInFolder(folder) {
      try {
        const files = await apiUtils.wrapApiCall(this, async () => {
          // 直接使用folder_id调用API端点
          const response = await apiService.get(`/files/folders/by-id/${encodeURIComponent(folder.id)}/files`);
          
          // 确保正确处理响应格式
          const files = response.success && response.files ? response.files : [];
          
          // 确保currentFolder设置为完整的文件夹对象，而不是字符串
          this.currentFolder = folder;
          
          // 更新文件夹映射（如果API返回了相关信息）
          if (response.data && response.data.folder_id_map) {
            this.folderIdMap = { ...this.folderIdMap, ...response.data.folder_id_map };
          }
          
          this.currentFiles = files;
          return files;
        }, '加载文件夹中的文件失败');
        return files;
      } catch (error) {
        return [];
      }
    },
    
    // 上传文件
    async uploadFile(file, folderId = '') {
      loadingUtils.startLoading(this);
      this.fileUploadProgress = 0;
      
      try {
        const response = await apiUtils.wrapApiCall(this, async () => {
          const response = await apiService.rag.uploadFile(file, folderId);
          
          if (response.success) {
            notifyUtils.showSuccess(`文件上传成功: ${file.name}`);
            
            // 重新加载文件列表和文件夹列表以确保同步
            await Promise.all([this.loadFiles(), this.loadFolders()]);
            
            return { success: true };
          } else {
            throw new Error(response.message || '文件上传失败');
          }
        }, '上传文件失败');
        
        return response;
      } catch (error) {
        return { success: false, error: error.message };
      } finally {
        loadingUtils.setLoadingFalse(this);
        this.fileUploadProgress = null;
      }
    },
    
    // 批量上传文件
    async batchUploadFiles(files, folderId = '') {
      loadingUtils.startLoading(this);
      
      try {
        const uploadResults = [];
        let successCount = 0;
        let failCount = 0;
        
        for (const file of files) {
          const result = await this.uploadFile(file, folderId);
          uploadResults.push({ filename: file.name, ...result });
          
          if (result.success) {
            successCount++;
          } else {
            failCount++;
          }
        }
        
        // 显示汇总结果
        if (successCount > 0) {
          notifyUtils.showSuccess(`成功上传 ${successCount} 个文件`);
        }
        if (failCount > 0) {
          notifyUtils.showError(`上传失败 ${failCount} 个文件`);
        }
        
        return { successCount, failCount, uploadResults };
      } catch (error) {
        console.error('批量上传文件失败:', error);
        errorUtils.setError(this, `批量上传文件失败: ${error.message || '未知错误'}`);
        return { successCount: 0, failCount: files.length, uploadResults: [] };
      } finally {
        loadingUtils.setLoadingFalse(this);
      }
    },
    
    // 删除文件
    async deleteDocument(filename, foldername = '') {
      try {
        const response = await apiUtils.wrapApiCall(this, async () => {
          const response = await apiService.rag.deleteDocument(filename, foldername);
          
          if (response.success) {
            notifyUtils.showSuccess(`文件删除成功: ${filename}`);
            
            // 重新加载文件列表和文件夹列表以确保同步
            await Promise.all([this.loadFiles(), this.loadFolders()]);
            
            return { success: true };
          } else {
            throw new Error(response.message || '文件删除失败');
          }
        }, '删除文件失败');
        
        return response;
      } catch (error) {
        return { success: false, error: error.message };
      }
    },
    
    // 删除所有文档
    async deleteAllDocuments() {
      try {
        const result = await apiUtils.wrapApiCall(this, async () => {
          // 调用后端API删除所有文件
          const response = await apiService.delete('/files/documents/delete-all');
          
          // 清空文件列表和文件夹相关状态
          this.files = [];
          this.folders = [];
          this.folderIdMap = {};
          this.currentFolder = null;
          this.currentFiles = [];
          
          // 重新加载文件列表和文件夹列表以确保同步
          await Promise.all([this.loadFiles(), this.loadFolders()]);
          
          notifyUtils.showSuccess('所有文件已成功删除');
          
          return {
            success: true,
            message: response.data?.message || '所有文件、文件夹和向量数据库已清空',
            deleted_count: response.data?.deleted_count || 0
          };
        }, '删除所有文件失败');
        
        return result;
      } catch (error) {
        return {
          success: false,
          error: error.message || '未知错误'
        };
      }
    },
    
    // 创建文件夹/知识库
    async createFolder(knowledgeBaseName) {
      try {
        const result = await apiUtils.wrapApiCall(this, async () => {
          let response;
          
          try {
            // 优先尝试使用Tauri的文件系统API
            const { invoke } = await import('@tauri-apps/api');
            response = await invoke('create_knowledge_base', {
              name: knowledgeBaseName
            });
          } catch (importError) {
            // 如果导入失败，回退到使用Python API
            console.warn('无法使用Tauri invoke，回退到Python API:', importError);
            response = await apiService.post('/files/folders', {
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
          
          notifyUtils.showSuccess(`成功创建知识库: ${knowledgeBaseName}`);
          
          return {
            success: true,
            folder: response
          };
        }, '创建文件夹失败');
        
        return result;
      } catch (error) {
        return {
          success: false,
          error: error.message || '未知错误'
        };
      }
    },
    
    // 删除文件夹
    async deleteFolder(folder) {
      if (!folder || !folder.id) return;
      
      try {
        const result = await apiUtils.wrapApiCall(this, async () => {
          // 调用后端API删除文件夹
          await apiService.delete(`/files/folders?folder_id=${folder.id}`);
          
          // 重新加载文件夹列表和文件列表以确保同步
          await Promise.all([this.loadFolders(), this.loadFiles()]);
          
          notifyUtils.showSuccess(`成功删除文件夹: ${folder.name}`);
          
          // 如果删除的是当前文件夹，则重置当前文件夹和文件列表
          if (this.currentFolder === folder) {
            this.currentFolder = null;
            this.currentFiles = [];
          }
          
          return { success: true };
        }, '删除文件夹失败');
        
        return result;
      } catch (error) {
        return { success: false, error: error.message };
      }
    },
    
    // 获取文件详情
    async getFileDetails(fileId) {
      try {
        const fileDetails = await apiUtils.wrapApiCall(this, async () => {
          // 首先根据fileId查找文件
          const file = this.files.find(f => f.id === fileId);
          if (!file) {
            throw new Error(`文件不存在: ${fileId}`);
          }
          
          // 调用后端API获取文件详情
          const response = await apiService.get(`/files/documents/${fileId}`);
          // 确保正确处理响应格式
          const fileDetails = response.success && response.details ? response.details : null;
          
          return {
            ...file,
            ...fileDetails,
            id: file.id
          };
        }, '获取文件详情失败');
        
        return fileDetails;
      } catch (error) {
        return null;
      }
    }
  },
});
