<template>
  <button
    :class="[
      'flex items-center justify-center transition-all duration-300 font-medium',
      'bg-transparent text-neutral border border-transparent hover:bg-gray-100 hover:text-primary dark:text-gray-300 dark:hover:bg-transparent dark:hover:text-[#64B5F6]',
      buttonSizeClass,
      buttonShapeClass,
      {
        'opacity-50 cursor-not-allowed': disabled
      },
      $attrs.class
    ]"
    :disabled="disabled"
    @click="handleClick"
    v-bind="$attrs"
  >
    <i v-if="icon" :class="[
      'fa-solid',
      icon.startsWith('fa-') ? icon : 'fa-' + icon,
      'w-full h-full flex items-center justify-center',
      { 'mr-2': content }
    ]"></i>
    <span v-if="content">{{ content }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue';

// 定义组件属性
const props = defineProps({
  // 按钮大小：xs, sm, md, lg, icon
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'icon'].includes(value)
  },
  // 按钮形状：rounded, full, square
  shape: {
    type: String,
    default: 'full',
    validator: (value) => ['rounded', 'full', 'square'].includes(value)
  },
  // 按钮图标
  icon: {
    type: String,
    default: ''
  },
  // 按钮文本内容
  content: {
    type: String,
    default: ''
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  }
});

// 定义组件事件
const emit = defineEmits(['click']);

// 定义组件名称和属性继承选项
defineOptions({
  name: 'BaseButton',
  inheritAttrs: false // 阻止Vue自动将$attrs传递给组件根元素
});

// 尺寸样式类
const buttonSizeClass = computed(() => {
  const sizes = {
    xs: ['text-[10px] px-1 py-0.5 w-6 h-6', 'i:text-[10px]'],
    sm: ['text-xs px-2 py-1 w-7 h-7', 'i:text-xs'],
    md: ['text-sm px-3 py-1.5 w-8 h-8', 'i:text-sm'],
    lg: ['text-base px-4 py-2 w-9 h-9', 'i:text-base'],
    icon: ['text-sm p-1.5 w-8 h-8', 'i:text-sm']
  };
  return sizes[props.size] || sizes.md;
});

// 形状样式类
const buttonShapeClass = computed(() => {
  const shapes = {
    rounded: 'rounded-lg',
    full: 'rounded-full',
    square: 'rounded-sm'
  };
  return shapes[props.shape] || shapes.rounded;
});

// 处理点击事件
const handleClick = (event) => {
  if (!props.disabled) {
    emit('click', event);
  }
};
</script>

<style scoped>
/* 按钮基础样式已通过Tailwind CSS类实现 */
</style>