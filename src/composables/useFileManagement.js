import { ref, computed } from 'vue';
import { useFileStore } from '../store/fileStore.js';
import { useNotifications } from './useNotifications.js';
import logger from '../utils/logger.js';

/**
 * 文件管理组合函数，统一处理文件操作逻辑
 * @returns {Object} 包含文件管理功能的对象
 */
export function useFileManagement() {
  const fileStore = useFileStore();
  const { showSystemNotification } = useNotifications();

  // 响应式状态
  const selectedFolder = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  // 计算属性
  const files = computed(() => fileStore.files || []);
  const folders = computed(() => fileStore.folders || []);
  const currentFolder = computed(() => fileStore.currentFolder || null);
  const currentFiles = computed(() => fileStore.currentFiles || []);
  const fileUploadProgress = computed(() => fileStore.fileUploadProgress || null);

  /**
   * 加载文件列表
   * @returns {Promise<Array>} 文件列表
   */
  const loadFiles = async () => {
    try {
      isLoading.value = true;
      error.value = null;

      await fileStore.loadFiles();
      return files.value;
    } catch (err) {
      error.value = err.message || '加载文件列表失败';
      logger.error('加载文件列表失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 加载文件夹列表
   * @returns {Promise<Array>} 文件夹列表
   */
  const loadFolders = async () => {
    try {
      isLoading.value = true;
      error.value = null;

      await fileStore.loadFolders();
      return folders.value;
    } catch (err) {
      error.value = err.message || '加载文件夹列表失败';
      logger.error('加载文件夹列表失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 加载指定文件夹中的文件
   * @param {Object} folder - 文件夹对象
   * @returns {Promise<Array>} 文件列表
   */
  const loadFilesInFolder = async (folder) => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await fileStore.loadFilesInFolder(folder);
      selectedFolder.value = folder;
      return result;
    } catch (err) {
      error.value = err.message || '加载文件夹中的文件失败';
      logger.error('加载文件夹中的文件失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 上传文件
   * @param {File} file - 文件对象
   * @param {string} [folderId=''] - 文件夹ID
   * @returns {Promise<Object>} 上传结果
   */
  const uploadFile = async (file, folderId = '') => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await fileStore.uploadFile(file, folderId);
      showSystemNotification(`文件上传成功: ${file.name}`, 'success');
      return result;
    } catch (err) {
      error.value = err.message || '上传文件失败';
      logger.error('上传文件失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 批量上传文件
   * @param {Array<File>} files - 文件数组
   * @param {string} [folderId=''] - 文件夹ID
   * @returns {Promise<Object>} 批量上传结果
   */
  const batchUploadFiles = async (files, folderId = '') => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await fileStore.batchUploadFiles(files, folderId);
      if (result.successCount > 0) {
        showSystemNotification(`成功上传 ${result.successCount} 个文件`, 'success');
      }
      if (result.failCount > 0) {
        showSystemNotification(`上传失败 ${result.failCount} 个文件`, 'error');
      }
      return result;
    } catch (err) {
      error.value = err.message || '批量上传文件失败';
      logger.error('批量上传文件失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 删除文件
   * @param {string} filename - 文件名
   * @param {string} [foldername=''] - 文件夹名
   * @returns {Promise<Object>} 删除结果
   */
  const deleteFile = async (filename, foldername = '') => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await fileStore.deleteDocument(filename, foldername);
      showSystemNotification(`文件删除成功: ${filename}`, 'success');
      return result;
    } catch (err) {
      error.value = err.message || '删除文件失败';
      logger.error('删除文件失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 删除所有文件
   * @returns {Promise<Object>} 删除结果
   */
  const deleteAllFiles = async () => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await fileStore.deleteAllDocuments();
      showSystemNotification('所有文件已成功删除', 'success');
      return result;
    } catch (err) {
      error.value = err.message || '删除所有文件失败';
      logger.error('删除所有文件失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 创建文件夹
   * @param {string} folderName - 文件夹名
   * @returns {Promise<Object>} 创建结果
   */
  const createFolder = async (folderName) => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await fileStore.createFolder(folderName);
      showSystemNotification(`成功创建文件夹: ${folderName}`, 'success');
      return result;
    } catch (err) {
      error.value = err.message || '创建文件夹失败';
      logger.error('创建文件夹失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 删除文件夹
   * @param {Object} folder - 文件夹对象
   * @returns {Promise<Object>} 删除结果
   */
  const deleteFolder = async (folder) => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await fileStore.deleteFolder(folder);
      showSystemNotification(`成功删除文件夹: ${folder.name}`, 'success');
      return result;
    } catch (err) {
      error.value = err.message || '删除文件夹失败';
      logger.error('删除文件夹失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 获取文件详情
   * @param {string} fileId - 文件ID
   * @returns {Promise<Object>} 文件详情
   */
  const getFileDetails = async (fileId) => {
    try {
      isLoading.value = true;
      error.value = null;

      const result = await fileStore.getFileDetails(fileId);
      return result;
    } catch (err) {
      error.value = err.message || '获取文件详情失败';
      logger.error('获取文件详情失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 下载文件
   * @param {Object} file - 文件对象
   */
  const downloadFile = (file) => {
    try {
      isLoading.value = true;
      error.value = null;

      return fileStore.downloadFile(file);
    } catch (err) {
      error.value = err.message || '下载文件失败';
      logger.error('下载文件失败:', err);
      showSystemNotification(error.value, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    // 响应式状态
    selectedFolder,
    isLoading,
    error,
    
    // 计算属性
    files,
    folders,
    currentFolder,
    currentFiles,
    fileUploadProgress,
    
    // 方法
    loadFiles,
    loadFolders,
    loadFilesInFolder,
    uploadFile,
    batchUploadFiles,
    deleteFile,
    deleteAllFiles,
    createFolder,
    deleteFolder,
    getFileDetails,
    downloadFile
  };
}
