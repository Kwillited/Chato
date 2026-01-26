import { ref, computed } from 'vue';
import { useFileStore } from '../../../app/store/fileStore.js';
import logger from '../../../shared/utils/logger.js';

/**
 * 聊天文件上传管理组合函数，封装聊天过程中的文件上传逻辑
 * @returns {Object} 包含文件上传相关的状态和方法
 */
export function useChatFileUpload() {
  const fileStore = useFileStore();
  
  // 响应式状态
  const uploadedFiles = ref([]);
  const isUploading = ref(false);
  const uploadProgress = ref(0);
  const error = ref(null);
  
  // 计算属性
  const hasUploadedFiles = computed(() => uploadedFiles.value.length > 0);
  
  /**
   * 添加文件到上传列表
   * @param {FileList|Array} files - 要上传的文件列表
   */
  const addFiles = (files) => {
    try {
      error.value = null;
      const fileArray = Array.from(files);
      
      // 转换为上传文件对象格式
      const newUploadFiles = fileArray.map(file => ({
        id: generateTempFileId(),
        name: file.name,
        size: file.size,
        type: file.type,
        file: file,
        status: 'pending'
      }));
      
      uploadedFiles.value = [...uploadedFiles.value, ...newUploadFiles];
      return newUploadFiles;
    } catch (err) {
      error.value = `添加文件失败: ${err.message}`;
      logger.error('添加文件失败:', err);
      return [];
    }
  };
  
  /**
   * 从上传列表中移除文件
   * @param {string} fileId - 要移除的文件ID
   */
  const removeFile = (fileId) => {
    uploadedFiles.value = uploadedFiles.value.filter(file => file.id !== fileId);
  };
  
  /**
   * 清空上传列表
   */
  const clearUploadedFiles = () => {
    uploadedFiles.value = [];
    uploadProgress.value = 0;
    error.value = null;
  };
  
  /**
   * 开始上传文件
   */
  const startUpload = async () => {
    if (uploadedFiles.value.length === 0) return;
    
    try {
      isUploading.value = true;
      uploadProgress.value = 0;
      error.value = null;
      
      // 更新文件状态为上传中
      uploadedFiles.value.forEach(file => {
        file.status = 'uploading';
      });
      
      // TODO: 实现文件上传逻辑
      // 这里可以调用fileStore的上传方法，或者直接调用API
      
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        uploadProgress.value += 10;
        if (uploadProgress.value >= 100) {
          clearInterval(progressInterval);
          uploadProgress.value = 100;
          
          // 更新文件状态为已上传
          uploadedFiles.value.forEach(file => {
            file.status = 'uploaded';
          });
          
          isUploading.value = false;
        }
      }, 500);
      
    } catch (err) {
      error.value = `文件上传失败: ${err.message}`;
      isUploading.value = false;
      logger.error('文件上传失败:', err);
      
      // 更新文件状态为上传失败
      uploadedFiles.value.forEach(file => {
        file.status = 'error';
      });
    }
  };
  
  /**
   * 取消上传
   */
  const cancelUpload = () => {
    isUploading.value = false;
    uploadProgress.value = 0;
    error.value = '上传已取消';
    
    // 更新文件状态为已取消
    uploadedFiles.value.forEach(file => {
      file.status = 'cancelled';
    });
  };
  
  /**
   * 生成临时文件ID
   * @returns {string} 临时文件ID
   */
  const generateTempFileId = () => {
    return `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };
  
  return {
    // 状态
    uploadedFiles,
    isUploading,
    uploadProgress,
    error,
    
    // 计算属性
    hasUploadedFiles,
    
    // 方法
    addFiles,
    removeFile,
    clearUploadedFiles,
    startUpload,
    cancelUpload
  };
}

