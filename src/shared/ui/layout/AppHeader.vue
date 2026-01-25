<template>
  <!-- 通用应用头部导航栏容器 -->
  <header class="w-full px-4 sm:px-6 h-10 flex items-center justify-between gap-2 sticky top-0 bg-[#F8FAFC] dark:bg-dark-primary backdrop-blur-md z-30 border-b border-gray-100 dark:border-dark-700 transition-all duration-300">
    <!-- 动态渲染不同的头部组件内容 -->
    <component 
      :is="componentMap[headerType]" 
      v-bind="headerProps" 
      v-on="headerEvents"
    />
  </header>
</template>

<script setup>
import { defineAsyncComponent, computed } from 'vue';

// 定义组件属性
const props = defineProps({
  // 要渲染的头部组件名称
  headerType: {
    type: String,
    default: 'chat-header'
  },
  // 头部组件的 props
  headerProps: {
    type: Object,
    default: () => {}
  },
  // 头部组件的事件
  headerEvents: {
    type: Object,
    default: () => {}
  }
});

// 动态导入头部组件
const ChatHeader = defineAsyncComponent(() => import('../../../modules/conversation/components/headers/ChatHeader.vue'));
const SettingsHeader = defineAsyncComponent(() => import('../../../pages/chat/SettingsHeader.vue'));

// 组件映射表：将字符串类型映射到实际组件
const componentMap = {
  'chat-header': ChatHeader,
  'settings-header': SettingsHeader
};
</script>

<style scoped>
/* 通用头部样式 */
header {
  transition: all 0.3s ease;
}

/* 确保按钮和内容的交互效果一致 */
button {
  transition: all 0.2s ease;
}

button:active {
  transform: scale(0.98);
}
</style>