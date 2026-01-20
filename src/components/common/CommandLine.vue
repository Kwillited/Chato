<template>
  <div v-if="visible" class="command-line-overlay">
    <div class="command-line-container">
      <div class="command-line-header">
        <div class="command-line-title">Chato Command Line</div>
        <div class="command-line-controls">
          <button class="command-line-btn" @click="minimizeCommandLine">
            <i class="fa-solid fa-window-minimize"></i>
          </button>
          <button class="command-line-btn" @click="maximizeCommandLine">
            <i class="fa-solid fa-window-maximize"></i>
          </button>
          <button class="command-line-btn command-line-close" @click="handleClose">
            <i class="fa-solid fa-times"></i>
          </button>
        </div>
      </div>
      <div class="command-line-body">
        <div class="command-line-output" ref="outputContainer">
          <div v-for="(entry, index) in commandHistory" :key="index" class="command-entry">
            <div class="command-input">
            <span class="prompt">{{ currentPath }}{{ prompt }}</span>
            <span class="command-text">{{ entry.command }}</span>
          </div>
            <div v-if="entry.response" class="command-response">{{ entry.response }}</div>
          </div>
          <div class="command-input active">
            <span class="prompt">{{ currentPath }}{{ prompt }}</span>
            <input 
              v-model="currentCommand" 
              ref="commandInput" 
              @keydown.enter="executeCommand" 
              @keydown.up="navigateHistory(-1)" 
              @keydown.down="navigateHistory(1)"
              class="command-input-field"
              placeholder="输入命令..."
              autocomplete="off"
              spellcheck="false"
            />
            <span class="cursor" :class="{ blinking: showCursor }"></span>
          </div>
        </div>
      </div>
      <div class="command-line-footer">
        <div class="command-line-help">
          <span>可用命令: </span>
          <span class="command-help-item">help</span>
          <span class="command-help-item">clear</span>
          <span class="command-help-item">exit</span>
          <span class="command-help-item">list-models</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, watch } from 'vue';
import { invoke } from '@tauri-apps/api/core';
import { showNotification } from '../../services/notificationUtils.js';

// 定义组件属性
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
});

// 定义组件事件
const emit = defineEmits(['close']);

// 定义组件名称
defineOptions({
  name: 'CommandLine'
});

// 组件状态
const outputContainer = ref(null);
const commandInput = ref(null);
const currentCommand = ref('');
const commandHistory = ref([]);
const historyIndex = ref(-1);
const historyBuffer = ref('');
const showCursor = ref(true);
const prompt = ref('> ');
const isMaximized = ref(false);
const currentPath = ref('');

// 光标闪烁效果
let cursorInterval;

// 命令执行函数
const executeCommand = async () => {
  const command = currentCommand.value.trim();
  if (!command) return;

  // 添加到历史记录
  commandHistory.value.push({ command, response: null });
  
  // 保存到历史缓冲区
  const historyBufferCopy = [...historyBuffer.value];
  historyBufferCopy.push(command);
  historyBuffer.value = historyBufferCopy;
  
  // 清空当前命令
  const executedCommand = command;
  currentCommand.value = '';
  historyIndex.value = -1;

  // 滚动到底部
  await nextTick();
  if (outputContainer.value) {
    outputContainer.value.scrollTop = outputContainer.value.scrollHeight;
  }

  // 执行命令并获取响应
  let response = '';
  try {
    response = await handleCommand(executedCommand);
  } catch (error) {
    response = `错误: ${error.message}`;
  }

  // 更新响应
  const lastEntry = commandHistory.value[commandHistory.value.length - 1];
  lastEntry.response = response;

  // 再次滚动到底部
  await nextTick();
  if (outputContainer.value) {
    outputContainer.value.scrollTop = outputContainer.value.scrollHeight;
  }
};

// 获取当前工作路径
const getCurrentPath = async () => {
  try {
    const path = await invoke('execute_command', { command: 'cd' });
    // 清理路径输出，Windows系统的cd命令输出格式为"当前目录为: X:\path"
    if (path.includes('当前目录为:')) {
      currentPath.value = path.split('当前目录为:')[1].trim();
    } else {
      currentPath.value = path.trim();
    }
  } catch {
    currentPath.value = 'C:'; // 默认路径
  }
};

// 命令处理函数
const handleCommand = async (command) => {
  const [cmd, ...args] = command.split(' ');
  
  // 检查是否是cd命令，如果是则特殊处理
  if (cmd.toLowerCase() === 'cd') {
    try {
      const newPath = args.join(' ');
      await invoke('execute_command', { command: `cd ${newPath}` });
      // 更新当前路径
      await getCurrentPath();
      return `已切换到: ${currentPath.value}`;
    } catch (error) {
      return `切换目录失败: ${error.message}`;
    }
  }
  
  switch (cmd.toLowerCase()) {
    case 'help':
      return `
可用命令列表:
  help              - 显示此帮助信息
  clear             - 清除命令行历史
  exit              - 关闭命令行窗口
  list-models       - 列出可用的模型
  echo [text]       - 显示文本
  version           - 显示Chato版本信息
          `;
          
    case 'clear':
      commandHistory.value = [];
      return '命令历史已清除';
          
    case 'exit':
      handleClose();
      return '正在关闭命令行...';
          
    case 'list-models':
      // 这里可以从modelSettingStore获取模型列表
      return '可用模型: OpenAI GPT-4, Claude 3, Gemini, 本地模型';
          
    case 'echo':
      return args.join(' ');
          
    case 'version':
      return 'Chato v0.1.0 - AI助手应用';
          
    default:
      try {
        // 尝试通过Tauri调用系统命令
        const result = await invoke('execute_command', { command: command });
        return result;
      } catch {
        return `未知命令: ${cmd}`;
      }
  }
};

// 历史导航
const navigateHistory = (direction) => {
  if (historyBuffer.value.length === 0) return;
  
  // 保存当前输入（如果是新命令）
  if (historyIndex.value === -1) {
    historyBuffer.value.push(currentCommand.value);
  }
  
  // 更新索引
  historyIndex.value += direction;
  
  // 边界检查
  if (historyIndex.value < 0) {
    historyIndex.value = historyBuffer.value.length - 1;
  } else if (historyIndex.value >= historyBuffer.value.length) {
    historyIndex.value = 0;
  }
  
  // 设置当前命令
  currentCommand.value = historyBuffer.value[historyIndex.value];
};

// 关闭命令行
const handleClose = () => {
  emit('close');
};

// 最小化命令行
const minimizeCommandLine = () => {
  // 这里可以实现最小化逻辑
  showNotification('最小化功能待实现', 'info');
};

// 最大化命令行
const maximizeCommandLine = async () => {
  if (isMaximized.value) {
    // 恢复原始大小
    isMaximized.value = false;
    // 这里可以添加恢复原始大小的逻辑
  } else {
    // 最大化
    isMaximized.value = true;
    // 这里可以添加最大化的逻辑
  }
};

// 监听可见性变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    nextTick(() => {
      if (commandInput.value) {
        commandInput.value.focus();
      }
    });
  }
});

// 生命周期
onMounted(async () => {
  cursorInterval = setInterval(() => {
    showCursor.value = !showCursor.value;
  }, 500);
  // 获取初始路径
  await getCurrentPath();
});

onUnmounted(() => {
  if (cursorInterval) {
    clearInterval(cursorInterval);
  }
});
</script>

<style scoped>
.command-line-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.command-line-container {
  width: 800px;
  max-width: 90vw;
  height: 400px;
  max-height: 80vh;
  background-color: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
}

.command-line-header {
  background-color: #2d2d2d;
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #3e3e3e;
}

.command-line-title {
  color: #cccccc;
  font-size: 14px;
  font-weight: 500;
}

.command-line-controls {
  display: flex;
  gap: 8px;
}

.command-line-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  color: #cccccc;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.command-line-btn:hover {
  background-color: #404040;
}

.command-line-close:hover {
  background-color: #ff5252;
  color: white;
}

.command-line-body {
  flex: 1;
  overflow: hidden;
  background-color: #1e1e1e;
}

.command-line-output {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
  color: #d4d4d4;
  font-size: 14px;
  line-height: 1.5;
}

.command-entry {
  margin-bottom: 8px;
}

.command-input {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.command-input.active {
  position: relative;
}

.prompt {
  color: #569cd6;
  font-weight: 600;
  margin-right: 4px;
}

.command-text {
  color: #d4d4d4;
}

.command-input-field {
  flex: 1;
  background: none;
  border: none;
  color: #d4d4d4;
  font-family: inherit;
  font-size: inherit;
  outline: none;
  padding: 0;
}

.command-response {
  color: #9cdcfe;
  margin-left: 20px;
  white-space: pre-wrap;
  word-break: break-word;
}

.cursor {
  width: 8px;
  height: 16px;
  background-color: #d4d4d4;
  margin-left: 2px;
  display: inline-block;
}

.cursor.blinking {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.command-line-footer {
  background-color: #2d2d2d;
  padding: 8px 16px;
  border-top: 1px solid #3e3e3e;
  font-size: 12px;
  color: #858585;
}

.command-line-help {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.command-help-item {
  background-color: #3e3e3e;
  padding: 2px 6px;
  border-radius: 3px;
  color: #cccccc;
  font-size: 11px;
}

/* 滚动条样式 */
.command-line-output::-webkit-scrollbar {
  width: 10px;
}

.command-line-output::-webkit-scrollbar-track {
  background: #1e1e1e;
}

.command-line-output::-webkit-scrollbar-thumb {
  background: #404040;
  border-radius: 5px;
}

.command-line-output::-webkit-scrollbar-thumb:hover {
  background: #505050;
}
</style>