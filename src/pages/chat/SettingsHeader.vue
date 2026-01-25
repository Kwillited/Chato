<template>
  <!-- 设置页面头部导航栏 -->
  <div class="w-full flex items-center justify-between gap-2">
    <!-- 左侧返回按钮 -->
    <div class="flex items-center gap-2">
      <Button 
        icon="arrow-left"
        tooltip="返回"
        variant="secondary"
        size="md"
        shape="full"
        @click="$emit('back')"
      />
    </div>
    
    <!-- 标题区域 -->
    <h1 class="font-bold text-sm sm:text-base tracking-tight text-gray-900 dark:text-white">{{ title }}</h1>
    
    <!-- 右侧空白区域（用于平衡布局） -->
    <div class="w-16"></div>
  </div>
</template>

<script setup>
import Button from '../../shared/ui/Button.vue';

// 定义组件属性
const props = defineProps({
  // 页面标题
  title: {
    type: String,
    default: '设置与配置'
  },
  // 当前激活的标签
  activeTab: {
    type: String,
    default: 'basic'
  },
  // 标签列表
  tabs: {
    type: Array,
    default: () => [
      { label: '基本设置', value: 'basic' },
      { label: '模型配置', value: 'models' },
      { label: '知识库配置', value: 'knowledge' },
      { label: 'MCP工具', value: 'mcp' },
      { label: '通知设置', value: 'notifications' },
      { label: '关于', value: 'about' }
    ]
  }
});

// 定义组件事件
const emit = defineEmits(['back', 'tab-change']);
</script>

<style scoped>
/* 设置页面特定样式可以在这里添加 */
</style>