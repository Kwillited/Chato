<template>
  <div id="topNav" class="z-50 absolute top-0 left-0 right-0 h-8 flex items-center px-4 bg-[#F8FAFC] dark:bg-dark-primary transition-all duration-300" data-tauri-drag-region="">
    <!-- 菜单栏项目 -->
    <div class="flex items-center gap-6" data-tauri-drag-region>
      <!-- Mac风格窗口控制按钮 -->
       <div class="flex gap-2.5 mr-4">
          <Tooltip content="关闭">
            <button class="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors duration-200 focus:outline-none focus:ring-0" @click="handleClose"></button>
          </Tooltip>
          <Tooltip content="最小化">
            <button class="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors duration-200 focus:outline-none focus:ring-0" @click="handleMinimize"></button>
          </Tooltip>
          <Tooltip content="最大化">
            <button class="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors duration-200 focus:outline-none focus:ring-0" @click="handleMaximize"></button>
          </Tooltip>
        </div>
      <!-- NeoVAI标题已删除 -->
    </div>

    <!-- 中间：占位，确保右侧元素靠右 -->
    <div class="flex-1"></div>
    

  </div>
  <!-- 命令行窗口组件 -->
  <CommandLine 
    :visible="showCommandLine" 
    @close="closeCommandLine"
  />
</template>

<script setup>
import { ref } from 'vue';
import { Window } from '@tauri-apps/api/window';
import CommandLine from '../../components/common/CommandLine.vue';

const appWindow = new Window('main');

// 命令行窗口状态
const showCommandLine = ref(false);

// 处理窗口控制按钮点击事件
const handleMinimize = () => {
  appWindow.minimize();
};

const handleMaximize = () => {
  appWindow.toggleMaximize();
};

const handleClose = () => {
  appWindow.close();
};

// 关闭命令行窗口
const closeCommandLine = () => {
  showCommandLine.value = false;
};
</script>

<style scoped>



</style>
