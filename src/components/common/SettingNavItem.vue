<template>
  <button
    class="settings-nav-item w-full text-left p-3 rounded-lg transition-all duration-300"
    :class="{ active: isActive }"
    @click="handleClick"
  >
    <i :class="iconClass + ' mr-2'"></i> {{ label }}
  </button>
</template>

<script setup>
import { computed } from 'vue';

// 定义props
const props = defineProps({
  // 导航项的ID/标识
  id: {
    type: String,
    required: true
  },
  // 当前激活的section ID
  activeSection: {
    type: String,
    required: true
  },
  // 导航项显示的文本
  label: {
    type: String,
    required: true
  },
  // 图标类名
  iconClass: {
    type: String,
    required: true
  }
});

// 定义emits
const emit = defineEmits(['click']);

// 计算当前项是否为激活状态
const isActive = computed(() => {
  return props.id === props.activeSection;
});

// 处理点击事件
const handleClick = () => {
  emit('click', props.id);
};
</script>

<style scoped>
/* 基本样式已通过内联class实现 */
/* 组件特有的样式可以在这里定义 */
.settings-nav-item {
  transition: all 0.2s ease;
  border-radius: 8px;
  color: #64748b;
  border: 1px solid transparent;
  cursor: pointer;
  position: relative;
}

/* 图标样式 */
.settings-nav-item i {
  color: #64748b;
}

/* 暗色模式适配 */
.dark .settings-nav-item {
  color: #94a3b8;
  border-color: #334155;
}

.dark .settings-nav-item i {
  color: #94a3b8;
}

/* 悬停状态 */
.settings-nav-item:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.dark .settings-nav-item:hover {
  background-color: #334155;
  border-color: #475569;
}

/* 激活状态 */
.settings-nav-item.active {
  background-color: #f5f3ff;
  border-left: 4px solid #4f46e5;
  font-weight: 500;
  color: #4f46e5;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.1);
}

.settings-nav-item.active i {
  color: #4f46e5;
}

.dark .settings-nav-item.active {
  background-color: #4f46e515;
  border-left: 4px solid #818cf8;
  color: #818cf8;
  box-shadow: 0 2px 8px rgba(129, 140, 248, 0.2);
}

.dark .settings-nav-item.active i {
  color: #818cf8;
}
</style>