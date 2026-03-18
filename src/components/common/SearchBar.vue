<template>
  <div
    :class="[
      'search-container',
      $attrs.class
    ]"
    v-bind="$attrs"
  >
    <div class="search-input-wrapper">
      <input
        type="text"
        v-model="localSearchQuery"
        :placeholder="placeholder"
        class="search-input"
        :style="{ 'border-radius': rounded }"
        @input="handleInput"
        @focus="$emit('focus')"
        @blur="$emit('blur')"
      />
      <i class="search-icon fa-solid fa-search"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

defineOptions({ name: 'SearchBar', inheritAttrs: false });

// 定义props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '搜索对话...'
  },
  rounded: {
    type: String,
    default: '15px'
  }
});

// 定义emits
const emit = defineEmits(['update:modelValue', 'input', 'focus', 'blur']);

// 本地搜索查询状态
const localSearchQuery = ref(props.modelValue);

// 监听外部modelValue变化
watch(() => props.modelValue, (newValue) => {
  // 避免不必要的更新
  if (localSearchQuery.value !== newValue) {
    localSearchQuery.value = newValue;
  }
});

// 处理输入变化
const handleInput = (event) => {
  // 确保同步本地状态和模型值
  localSearchQuery.value = event.target.value;
  emit('update:modelValue', localSearchQuery.value);
  emit('input', localSearchQuery.value);
};
</script>

<style scoped>
/* 搜索框容器 */
.search-container {
  width: 100%;
  transition: all 0.3s ease;
}

/* 搜索输入包装器 */
.search-input-wrapper {
  position: relative;
  width: 100%;
}

/* 搜索输入框 */
.search-input {
  width: 100%;
  padding: 0.125rem 0.75rem 0.125rem 2rem;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  font-size: 0.875rem;
  color: #374151;
  transition: all 0.3s ease;
}

/* 搜索图标 */
.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.875rem;
  color: #9ca3af;
  pointer-events: none;
}

/* 输入框焦点状态 */
.search-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
  border-color: #3b82f6;
}
</style>

<style>
/* 暗色模式支持 */
.dark .search-input {
  background-color: #1f2937;
  border-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.dark .search-input::placeholder {
  color: #9ca3af;
}

.dark .search-icon {
  color: #9ca3af;
}

.dark .search-input:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}
</style>