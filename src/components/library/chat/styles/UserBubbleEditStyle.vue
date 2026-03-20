<template>
  <div class="flex justify-end w-full">
    <div class="relative flex flex-col items-end w-full">
      <!-- 文件列表 - 放在消息气泡上方 -->
      <div v-if="messageValue.files && messageValue.files.length > 0" class="flex flex-wrap gap-2 mb-2">
        <div 
          v-for="(file, index) in messageValue.files" 
          :key="index"
          class="flex flex-col items-start p-2 bg-white/80 dark:bg-dark-600 rounded-lg text-xs transition-colors duration-300 ease-in-out max-w-[150px] shadow-md"
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
      
      <!-- 编辑框气泡 -->
      <div 
        :class="[
          'bg-transparent text-gray-800 rounded-2xl rounded-tr-none px-5 py-3 overflow-hidden border-2 border-gray-800 dark:border-gray-300 relative',
          'w-full flex-1'
        ]"
      >
        <textarea
          v-model="editContent"
          class="w-full h-full bg-transparent resize-none outline-none text-gray-800 dark:text-gray-100 leading-relaxed min-h-[80px] pb-12"
          placeholder="编辑消息..."
          @input="handleInput"
        ></textarea>
        <!-- 操作按钮 -->
        <div class="absolute bottom-2 right-2 flex items-center space-x-2">
          <Tooltip content="取消编辑">
            <button class="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-full transition-all duration-200" @click="cancelEdit">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </Tooltip>
          <Tooltip content="保存编辑">
            <button class="text-gray-400 hover:text-primary dark:text-gray-500 dark:hover:text-[#64B5F6] p-2 rounded-full transition-all duration-200" @click="saveEdit">
              <i class="fa-solid fa-check"></i>
            </button>
          </Tooltip>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Tooltip } from '../../index.js'
import { getFileIcon, getFileExtension, formatFileSize } from '../../../../utils/file.js'

const props = defineProps({
  message: {
    type: [Object, Function],
    required: true,
    default: () => ({})
  }
})

const emit = defineEmits(['cancel', 'save'])

const messageValue = props.message
const editContent = ref(props.message.content || '')

const handleInput = () => {
}

const cancelEdit = () => {
  emit('cancel')
}

const saveEdit = () => {
  emit('save', {
    id: messageValue.id,
    content: editContent.value
  })
}
</script>

<style scoped>
textarea {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
}
</style>
