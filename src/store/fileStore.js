import { defineStore } from 'pinia';
import { apiService } from '../services/apiService';
import { showNotification } from '../utils/notificationUtils.js';
import eventBus from '../services/eventBus.js';

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
      this.error = message;
    },
    
    // 清除错误
    clearError() {
      this.error = null;
    },
    
    // 加载文件列表
    async loadFiles() {
      this.loading = true;
      this.clearError();
      
      try {
        const response = await apiService.rag.getDocuments();
        if (response.success) {
          this.files = response.documents || [];
          this.folderIdMap = response.folder_id_map || {};
        } else {
          this.setError('加载文件列表失败');
        }
      } catch (error) {
        console.error('加载文件列表失败:', error);
        this.setError(`加载文件列表失败: ${error.message || '未知错误'}`);
      } finally {
        this.loading = false;
      }
    },
    
    // 加载文件夹列表
    async loadFolders() {
      this.loading = true;
      this.clearError();
      
      try {
        const response = await apiService.rag.getFolders();
        if (response.success) {
          this.folders = response.folders || [];
        } else {
          this.setError('加载文件夹列表失败');
        }
      } catch (error) {
        console.error('加载文件夹列表失败:', error);
        this.setError(`加载文件夹列表失败: ${error.message || '未知错误'}`);
      } finally {
        this.loading = false;
      }
    },
    
    // 加载文件夹中的文件
    async loadFilesInFolder(folder) {
      this.loading = true;
      this.clearError();
      
      try {
        // 直接使用folder_id调用API端点
        const response = await apiService.get(`/api/files/folders/by-id/${encodeURIComponent(folder.id)}/files`);
        
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
      } catch (error) {
        console.error('加载文件夹中的文件失败:', error);
        this.setError(`加载文件夹中的文件失败: ${error.message || '未知错误'}`);
        return [];
      } finally {
        this.loading = false;
      }
    },
    
    // 上传文件
    async uploadFile(file, folderId = '') {
      this.loading = true;
      this.clearError();
      this.fileUploadProgress = 0;
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        if (folderId) {
          formData.append('folder_id', folderId);
        }
        
        const response = await apiService.rag.uploadFile(file, folderId);
        
        if (response.success) {
          showNotification(`文件上传成功: ${file.name}`, 'success');
          
          // 重新加载文件列表和文件夹列表以确保同步
          await Promise.all([this.loadFiles(), this.loadFolders()]);
          
          return { success: true };
        } else {
          throw new Error(response.message || '文件上传失败');
        }
      } catch (error) {
        console.error('上传文件失败:', error);
        this.setError(`上传文件失败: ${error.message || '未知错误'}`);
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
        this.fileUploadProgress = null;
      }
    },
    
    // 批量上传文件
    async batchUploadFiles(files, folderId = '') {
      this.loading = true;
      this.clearError();
      
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
          showNotification(`成功上传 ${successCount} 个文件`, 'success');
        }
        if (failCount > 0) {
          showNotification(`上传失败 ${failCount} 个文件`, 'error');
        }
        
        return { successCount, failCount, uploadResults };
      } catch (error) {
        console.error('批量上传文件失败:', error);
        this.setError(`批量上传文件失败: ${error.message || '未知错误'}`);
        return { successCount: 0, failCount: files.length, uploadResults: [] };
      } finally {
        this.loading = false;
      }
    },
    
    // 删除文件
    async deleteDocument(filename, foldername = '') {
      this.loading = true;
      this.clearError();
      
      try {
        const response = await apiService.rag.deleteDocument(filename, foldername);
        
        if (response.success) {
          showNotification(`文件删除成功: ${filename}`, 'success');
          
          // 重新加载文件列表和文件夹列表以确保同步
          await Promise.all([this.loadFiles(), this.loadFolders()]);
          
          return { success: true };
        } else {
          throw new Error(response.message || '文件删除失败');
        }
      } catch (error) {
        console.error('删除文件失败:', error);
        this.setError(`删除文件失败: ${error.message || '未知错误'}`);
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
      }
    },
    
    // 删除所有文档
    async deleteAllDocuments() {
      this.loading = true;
      this.clearError();
      
      try {
        // 调用后端API删除所有文件
        const response = await apiService.delete('/api/files/documents/delete-all');
        
        // 清空文件列表和文件夹相关状态
        this.files = [];
        this.folders = [];
        this.folderIdMap = {};
        this.currentFolder = null;
        this.currentFiles = [];
        
        // 重新加载文件列表和文件夹列表以确保同步
        await Promise.all([this.loadFiles(), this.loadFolders()]);
        
        showNotification('所有文件已成功删除', 'success');
        
        return {
          success: true,
          message: response.data?.message || '所有文件、文件夹和向量数据库已清空',
          deleted_count: response.data?.deleted_count || 0
        };
      } catch (error) {
        console.error('删除所有文件失败:', error);
        this.setError(`删除所有文件失败: ${error.message || '未知错误'}`);
        return {
          success: false,
          error: error.message || '未知错误'
        };
      } finally {
        this.loading = false;
      }
    },
    
    // 创建文件夹/知识库
    async createFolder(knowledgeBaseName) {
      this.loading = true;
      this.clearError();
      
      try {
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
          response = await apiService.post('/api/files/folders', {
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
        
        showNotification(`成功创建知识库: ${knowledgeBaseName}`, 'success');
        
        return {
          success: true,
          folder: response
        };
      } catch (error) {
        console.error('创建文件夹失败:', error);
        this.setError(`创建文件夹失败: ${error.message || '未知错误'}`);
        return {
          success: false,
          error: error.message || '未知错误'
        };
      } finally {
        this.loading = false;
      }
    },
    
    // 删除文件夹
    async deleteFolder(folder) {
      if (!folder || !folder.id) return;
      
      this.loading = true;
      this.clearError();
      
      try {
        // 调用后端API删除文件夹
        await apiService.delete(`/api/files/folders?folder_id=${folder.id}`);
        
        // 重新加载文件夹列表和文件列表以确保同步
        await Promise.all([this.loadFolders(), this.loadFiles()]);
        
        showNotification(`成功删除文件夹: ${folder.name}`, 'success');
        
        // 如果删除的是当前文件夹，则重置当前文件夹和文件列表
        if (this.currentFolder === folder) {
          this.currentFolder = null;
          this.currentFiles = [];
        }
        
        return { success: true };
      } catch (error) {
        console.error('删除文件夹失败:', error);
        this.setError(`删除文件夹失败: ${error.message || '未知错误'}`);
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
      }
    },
    
    // 获取文件详情
    async getFileDetails(fileId) {
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
        const response = await apiService.get(`/api/files/documents/${fileId}`);
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
    }
  },
});
