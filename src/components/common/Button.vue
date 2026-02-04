<template>
  <Tooltip v-if="tooltip" :content="tooltip">
    <button
      :class="[
        baseClasses,
        variantClasses,
        sizeClasses,
        shapeClasses,
        $attrs.class
      ]"
      :disabled="disabled"
      @click="handleClick"
      v-bind="$attrs"
    >
      <!-- 图标 -->
      <i v-if="icon" :class="[
        'fa-solid',
        icon.startsWith('fa-') ? icon : 'fa-' + icon,
        { 'mr-2': content }
      ]"></i>
      <!-- 文本内容 -->
      <span v-if="content">{{ content }}</span>
    </button>
  </Tooltip>
  <button
    v-else
    :class="[
      baseClasses,
      variantClasses,
      sizeClasses,
      shapeClasses,
      $attrs.class
    ]"
    :disabled="disabled"
    @click="handleClick"
    v-bind="$attrs"
  >
    <!-- 图标 -->
    <i v-if="icon" :class="[
      'fa-solid',
      icon.startsWith('fa-') ? icon : 'fa-' + icon,
      { 'mr-2': content }
    ]"></i>
    <!-- 文本内容 -->
    <span v-if="content">{{ content }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue';
import { Tooltip } from '../library/index.js';

// 定义组件属性
const props = defineProps({
  // 按钮类型：primary, secondary, dark
  variant: {
    type: String,
    default: 'secondary',
    validator: (value) => ['primary', 'secondary', 'dark'].includes(value)
  },
  // 按钮大小：sm, md, lg, icon
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'icon'].includes(value)
  },
  // 按钮形状：rounded, full, square
  shape: {
    type: String,
    default: 'rounded',
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
  // 按钮提示文本（显示为tooltip）
  tooltip: {
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

// 基础样式类
const baseClasses = computed(() => {
  return [
    'flex items-center justify-center transition-all duration-300',
    'font-medium',
    {
      'opacity-50 cursor-not-allowed': props.disabled,

    }
  ];
});

// 变体样式类
const variantClasses = computed(() => {
  const variants = {
    primary: [
      'bg-primary text-white border border-primary',
      'hover:bg-primary/90 hover:border-primary/90',
      'dark:bg-primary dark:text-white dark:border-primary',
      'dark:hover:bg-primary/90 dark:hover:border-primary/90'
    ],
    secondary: [
      'bg-transparent text-neutral border border-transparent',
      'hover:bg-gray-100 dark:hover:bg-dark-700',
      'dark:text-gray-300'
    ],
    dark: [
      'bg-gray-800 text-white border border-gray-800',
      'hover:bg-gray-700 hover:border-gray-700',
      'dark:bg-gray-700 dark:text-white dark:border-gray-700',
      'dark:hover:bg-gray-600 dark:hover:border-gray-600'
    ]
  };
  return variants[props.variant] || variants.secondary;
});

// 尺寸样式类
const sizeClasses = computed(() => {
  const sizes = {
    sm: [
      'text-xs px-2 py-1',
      'i:text-xs'
    ],
    md: [
      'text-sm px-3 py-1.5',
      'i:text-sm'
    ],
    lg: [
      'text-base px-4 py-2',
      'i:text-base'
    ],
    icon: [
      'text-sm p-1.5',
      'w-8 h-8',
      'i:text-sm'
    ]
  };
  return sizes[props.size] || sizes.md;
});

// 形状样式类
const shapeClasses = computed(() => {
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