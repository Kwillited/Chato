<template>
  <UserBubbleEditStyle 
    v-if="isEditing" 
    :message="message"
    @cancel="cancelEdit"
    @save="saveEdit"
  />
  <div v-else class="flex justify-end max-w-[85%]">
    <div class="relative group flex flex-col items-end">
      <!-- 文件列表 - 放在消息气泡上方 -->
      <div v-if="messageValue.files && messageValue.files.length > 0" class="flex flex-wrap gap-2 mb-2">
        <div 
          v-for="(file, index) in messageValue.files" 
          :key="index"
          class="flex flex-col items-start p-2 bg-white/80 dark:bg-dark-600 rounded-lg text-xs group transition-colors duration-300 ease-in-out max-w-[150px] shadow-md cursor-pointer hover:bg-white dark:hover:bg-dark-500"
          @click="previewFile(file)"
        >
          <div class="flex items-center gap-1 w-full">
            <i :class="['fa', getFileIcon(file.name), 'text-gray-500']"></i>
            <span class="truncate font-medium text-gray-800 dark:text-white">{{ file.name }}</span>
          </div>
          <div class="flex items-center gap-2 mt-1 w-full text-gray-400 text-[10px]">
            <span>{{ getFileExtension(file.name) }}</span>
            <span>{{ formatFileSize(file.size) }}</span>
          </div>
        </div>
      </div>
      
      <!-- 消息内容气泡 -->
      <div 
        v-if="messageContent || messageValue.error || messageValue.isTyping"
        :class="[
          'bg-gray-200 dark:bg-dark-500 text-gray-800 rounded-2xl rounded-tr-none px-5 py-3 shadow-lg overflow-hidden',
          'w-fit',
          'max-w-full'
        ]"
      >
        <div v-if="messageContent" class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="formattedContent" :key="updateKey"></div>
        
        <div v-if="messageValue.error" class="chat-error mt-2">
          <i class="fa-solid fa-circle-exclamation text-red-500 mr-1"></i>
          <span>{{ messageValue.error }}</span>
        </div>
        
        <Loading 
          v-if="messageValue.isTyping" 
          type="typing" 
          size="small" 
          color="var(--text-color-secondary, #9ca3af)" 
          containerClass="mt-2"
          v-memo="[messageValue.isTyping]"
        />
      </div>
      
      <div class="text-sm text-gray-500 dark:text-gray-400 mt-3 ml-3 flex items-center justify-end w-full max-w-[85%]">
        <div class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <Tooltip v-if="!messageValue.isTyping" content="编辑消息">
            <button class="edit-btn text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-full transition-all duration-200" @click="startEditMessage">
              <i class="fa-solid fa-pen"></i>
            </button>
          </Tooltip>
          <Tooltip content="复制消息内容">
            <button class="copy-btn text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-full transition-all duration-200" @click="copyMessageContent">
              <i class="fa-solid fa-copy"></i>
            </button>
          </Tooltip>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 文件预览模态框 -->
  <div v-if="showPreviewModal" class="fixed inset-0 flex items-center justify-center z-50" @click="closePreviewModal">
    <div class="bg-white dark:bg-gray-800 dark:text-white rounded-xl shadow-2xl dark:shadow-2xl border-2 border-gray-200 dark:border-gray-600 p-6 w-full max-w-3xl mx-4 transform transition-all duration-300 scale-100" @click.stop>
      <!-- 预览模态框标题 -->
      <div class="mb-4 flex justify-between items-center">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-white">{{ previewFileData.name }}</h3>
        <button 
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
          @click="closePreviewModal"
        >
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      
      <!-- 预览模态框内容 -->
      <div class="mb-6 max-h-[70vh] overflow-y-auto">
        <div v-if="previewLoading" class="flex justify-center items-center py-10">
          <Loading type="spin" size="medium" color="var(--text-color-secondary, #9ca3af)" />
        </div>
        <div v-else-if="previewError" class="text-red-500 text-center py-10">
          <i class="fa-solid fa-circle-exclamation text-4xl mb-2"></i>
          <p>{{ previewError }}</p>
        </div>
        <!-- 文本内容预览 -->
        <div v-else-if="previewFileContent" class="text-sm text-gray-800 dark:text-gray-300 whitespace-pre-wrap">
          {{ previewFileContent }}
        </div>
        <!-- 图片预览 -->
        <div v-else-if="previewImageUrl" class="flex justify-center items-center py-4">
          <img :src="previewImageUrl" alt="预览图片" class="max-w-full max-h-[60vh] object-contain" />
        </div>
        <!-- PDF预览 -->
        <div v-else-if="previewPdfUrl" class="flex flex-col items-center justify-center py-10">
          <i class="fa-solid fa-file-pdf text-6xl text-red-500 mb-4"></i>
          <h4 class="text-lg font-medium mb-2">{{ previewFileData.name }}</h4>
          <p class="text-gray-500 mb-4">PDF文件预览</p>
          <button 
            class="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-md transition-colors"
            @click="downloadFile(previewFileData)"
          >
            <i class="fa-solid fa-download mr-1"></i>
            下载PDF
          </button>
        </div>
        <!-- 不支持的文件类型 -->
        <div v-else class="text-gray-500 text-center py-10">
          <i class="fa-solid fa-file-circle-question text-4xl mb-2"></i>
          <p>不支持的文件类型或无法预览</p>
        </div>
      </div>
      
      <!-- 预览模态框按钮 -->
      <div class="flex justify-end gap-3">
        <button 
          class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 text-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          @click="downloadFile(previewFileData)"
        >
          <i class="fa-solid fa-download mr-1"></i>
          下载
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Tooltip, Loading } from '../../index.js'
import { useChatBubble } from '../../../../composables/useChatBubble.js'
import { getFileIcon, getFileExtension, formatFileSize } from '../../../../utils/file.js'
import UserBubbleEditStyle from './UserBubbleEditStyle.vue'

const props = defineProps({
  message: {
    type: [Object, Function],
    required: true,
    default: () => ({})
  }
})

const emit = defineEmits(['editMessage', 'saveEditMessage', 'cancelEditMessage'])

const isEditing = ref(false)

// 使用公共聊天气泡逻辑
const { 
  messageValue, 
  messageContent, 
  formattedContent, 
  updateKey, 
  copyMessageContent,
  copyCodeToClipboard
} = useChatBubble(props)

// 编辑消息（用户消息）
const startEditMessage = () => {
  isEditing.value = true
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  emit('cancelEditMessage', {
    id: messageValue.value.id
  })
}

// 保存编辑
const saveEdit = (data) => {
  isEditing.value = false
  emit('saveEditMessage', data)
}

// 文件预览相关状态
const showPreviewModal = ref(false);
const previewFileData = ref(null);
const previewFileContent = ref('');
const previewImageUrl = ref('');
const previewPdfUrl = ref('');
const previewLoading = ref(false);
const previewError = ref('');

// 预览文件
const previewFile = async (file) => {
  // 重置所有预览状态
  previewFileData.value = file;
  previewFileContent.value = '';
  previewImageUrl.value = '';
  previewPdfUrl.value = '';
  previewLoading.value = true;
  previewError.value = '';
  showPreviewModal.value = true;
  
  try {
    // 文件类型处理配置
    const textExtensions = ['txt', 'md', 'csv', 'js', 'ts', 'json', 'html', 'css', 'py', 'java', 'cpp', 'c', 'xml', 'yaml', 'yml', 'sh', 'bash'];
    const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'];
    const pdfExtensions = ['pdf'];
    
    const fileName = file.name || '';
    const fileExtension = fileName.split('.').pop().toLowerCase();
    
    // 文本文件处理
    if (textExtensions.includes(fileExtension)) {
      if (file.content) {
        // 处理带有base64 content字段的文件对象（来自后端）
        try {
          // 先解码base64，得到二进制数据
          const binaryString = atob(file.content);
          // 将二进制数据转换为UTF-8编码的字符串
          const bytes = new Uint8Array(binaryString.length);
          for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
          }
          const decodedContent = new TextDecoder('utf-8').decode(bytes);
          previewFileContent.value = decodedContent;
        } catch (decodeError) {
          console.error('解码文件内容失败:', decodeError);
          previewError.value = '解码文件内容失败: ' + decodeError.message;
        }
      } else if (file instanceof File) {
        // 处理浏览器原生File对象（来自前端上传）
        try {
          const fileContent = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
              resolve(e.target.result);
            };
            reader.onerror = (_e) => {
              reject(new Error('读取文件失败'));
            };
            reader.readAsText(file);
          });
          previewFileContent.value = fileContent;
        } catch (readError) {
          console.error('读取文件内容失败:', readError);
          previewError.value = '读取文件内容失败: ' + readError.message;
        }
      } else if (file.url) {
        // 处理带有URL的文件（可能是从其他地方获取的文件）
        previewError.value = 'URL类型文件预览功能正在开发中';
      } else {
        // 对于没有内容的文本文件，显示提示
        previewError.value = '文件内容为空或无法获取';
      }
    }
    // 图片文件处理
    else if (imageExtensions.includes(fileExtension)) {
      if (file.content) {
        // 处理带有base64 content字段的图片文件
        previewImageUrl.value = `data:image/${fileExtension};base64,${file.content}`;
      } else if (file instanceof File) {
        // 处理浏览器原生File对象的图片
        try {
          const imageUrl = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
              resolve(e.target.result);
            };
            reader.onerror = (_e) => {
              reject(new Error('读取图片失败'));
            };
            reader.readAsDataURL(file);
          });
          previewImageUrl.value = imageUrl;
        } catch (readError) {
          console.error('读取图片失败:', readError);
          previewError.value = '读取图片失败: ' + readError.message;
        }
      } else if (file.url) {
        // 处理带有URL的图片
        previewImageUrl.value = file.url;
      } else {
        previewError.value = '图片文件内容为空或无法获取';
      }
    }
    // PDF文件处理
    else if (pdfExtensions.includes(fileExtension)) {
      if (file.content) {
        // 处理带有base64 content字段的PDF文件
        previewPdfUrl.value = `data:application/pdf;base64,${file.content}`;
      } else if (file instanceof File) {
        // 处理浏览器原生File对象的PDF
        try {
          const pdfUrl = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
              resolve(e.target.result);
            };
            reader.onerror = (_e) => {
              reject(new Error('读取PDF失败'));
            };
            reader.readAsDataURL(file);
          });
          previewPdfUrl.value = pdfUrl;
        } catch (readError) {
          console.error('读取PDF失败:', readError);
          previewError.value = '读取PDF失败: ' + readError.message;
        }
      } else if (file.url) {
        // 处理带有URL的PDF
        previewPdfUrl.value = file.url;
      } else {
        previewError.value = 'PDF文件内容为空或无法获取';
      }
    }
    // 其他文件类型处理
    else {
      // 对于不支持的文件类型，显示提示
      console.error('不支持的文件类型:', fileExtension);
      previewError.value = `不支持的文件类型: ${fileExtension}`;
    }
  } catch (error) {
    console.error('预览文件失败:', error);
    previewError.value = '预览文件失败: ' + error.message;
  } finally {
    previewLoading.value = false;
  }
};

// 关闭预览模态框
const closePreviewModal = () => {
  showPreviewModal.value = false;
  previewFileData.value = null;
  previewFileContent.value = '';
  previewImageUrl.value = '';
  previewPdfUrl.value = '';
  previewError.value = '';
};

// 下载文件
const downloadFile = (file) => {
  // 创建下载链接
  if (file.url) {
    const link = document.createElement('a');
    link.href = file.url;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } else {
    // 如果没有URL，提示用户
    console.error('文件没有下载链接');
    previewError.value = '文件没有下载链接';
  }
};
</script>

<style scoped>
/* 确保操作按钮组的容器是相对定位，以便提示框可以绝对定位 */
.edit-btn, .copy-btn {
  position: relative;
}

/* 错误提示样式 */
.chat-error {
  color: #ef4444;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}
</style>