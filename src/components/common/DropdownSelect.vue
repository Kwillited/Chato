<template>
  <div class="relative inline-block flex items-center justify-center">
    <Tooltip :content="tooltip">
      <button
        :class="[
          'flex items-center justify-center gap-2 text-sm px-3 rounded-lg border border-transparent dark:border-gray-600 transition-all duration-300 ease-in-out',
          buttonSizeClass,
          buttonColorClass,
          {
            'btn-secondary hover:bg-gray-100 dark:hover:bg-dark-600 hover:text-primary cursor-pointer': !disabled,
            'cursor-default opacity-70': disabled
          }
        ]"
        @click="toggleDropdown"
        :disabled="disabled"
      >
        <i v-if="currentOption?.icon" :class="['fa-solid', currentOption.icon, 'mr-2 text-sm']"></i>
        <span>{{ currentOption?.displayName || placeholder }}</span>
        <i v-if="!disabled" class="fa-solid fa-chevron-down text-xs text-neutral"></i>
      </button>
    </Tooltip>
    <div
      ref="dropdownRef"
      :class="[
        'absolute left-1/2 transform -translate-x-1/2 bottom-full w-48 bg-white dark:bg-gray-700 z-50 shadow-lg rounded-lg border border-gray-200 dark:border-gray-600 animate-fade-in',
        margin,
        { 'hidden': !showDropdown }
      ]"
      style="z-index: var(--z-dropdown)"
    >
      <div class="py-1">
        <button
          v-for="option in options"
          :key="option.value"
          class="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-dark-600 transition-colors border-l-2 border-transparent"
          :class="{ 'border-l-3 border-gray-800 dark:border-gray-200 font-medium': option.value === modelValue }"
          @click="selectOption(option.value)"
        >
          <i v-if="option.icon" :class="['fa-solid', option.icon, 'mr-2 text-sm']"></i>
          {{ option.displayName }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { Tooltip } from '../library/index.js';

const props = defineProps({
  // 选项列表
  options: {
    type: Array,
    default: () => []
  },
  // 模型值（双向绑定）
  modelValue: {
    type: String,
    default: ''
  },
  // 占位符
  placeholder: {
    type: String,
    default: '请选择'
  },
  // 提示文本
  tooltip: {
    type: String,
    default: ''
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 按钮大小
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 按钮颜色
  color: {
    type: String,
    default: 'default', // default, primary, secondary
    validator: (value) => ['default', 'primary', 'secondary'].includes(value)
  },
  // 下拉菜单边距
  margin: {
    type: String,
    default: 'mb-2' // 默认边距
  }
});

const emit = defineEmits(['update:modelValue', 'change']);

// 下拉菜单显示状态
const showDropdown = ref(false);
// 下拉菜单引用
const dropdownRef = ref(null);

// 计算当前选中的选项
const currentOption = computed(() => {
  return props.options.find(option => option.value === props.modelValue) || null;
});

// 计算按钮大小类
const buttonSizeClass = computed(() => {
  switch (props.size) {
    case 'small':
      return 'h-6';
    case 'large':
      return 'h-10';
    default: // medium
      return 'h-8';
  }
});

// 计算按钮颜色类
const buttonColorClass = computed(() => {
  switch (props.color) {
    case 'primary':
      return 'text-white bg-primary hover:bg-primary/90';
    case 'secondary':
      return 'text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500';
    default: // default
      return 'text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700';
  }
});

// 切换下拉菜单显示状态
const toggleDropdown = () => {
  if (!props.disabled) {
    showDropdown.value = !showDropdown.value;
  }
};

// 选择选项
const selectOption = (value) => {
  emit('update:modelValue', value);
  emit('change', value);
  showDropdown.value = false;
};

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target) && !event.target.closest('button')) {
    showDropdown.value = false;
  }
};

// 生命周期钩子
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
/* 下拉菜单动画 */
.animate-fade-in {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, 5px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>