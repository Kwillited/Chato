<template>
  <!-- 通用侧边栏基础组件 -->
  <div :class="sidebarContainerClass">
    <!-- 插槽：侧边栏内容区域 -->
    <slot name="content">
      <div class="p-4">
        <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-white">{{ defaultTitle }}</h3>
        <div class="text-gray-600 dark:text-gray-400">
          <p>{{ defaultContent }}</p>
        </div>
      </div>
    </slot>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// 定义组件属性
const props = defineProps({
  // 侧边栏类型：left 或 right
  type: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'right'].includes(value)
  },
  // 默认标题
  defaultTitle: {
    type: String,
    default: '侧边栏'
  },
  // 默认内容
  defaultContent: {
    type: String,
    default: '侧边栏内容区域'
  },
  // 是否显示滚动条
  showScrollbar: {
    type: Boolean,
    default: true
  }
});

// 计算侧边栏容器类
const sidebarContainerClass = computed(() => {
  const baseClasses = ['transition-all', 'duration-300', 'overflow-y-auto', 'height-full', 'bg-inherit'];
  
  // 左右侧边栏的边框位置不同
  if (props.type === 'left') {
    baseClasses.push('border-r', 'border-gray-100', 'dark:border-dark-700');
  } else {
    baseClasses.push('border-l', 'border-gray-100', 'dark:border-dark-700');
  }
  
  return baseClasses;
});
</script>

<style scoped>
/* 滚动条样式 - 从原组件中提取的通用样式 */
.sidebar-container::-webkit-scrollbar {
  width: 6px;
}

.sidebar-container::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.sidebar-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

.dark .sidebar-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
}

.dark .sidebar-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 高度100% */
.height-full {
  height: 100%;
}

/* 背景继承 */
.bg-inherit {
  background-color: inherit;
}
</style>