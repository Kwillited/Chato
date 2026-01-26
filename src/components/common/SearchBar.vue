<template>
  <div class="search-container px-4 py-3 transition-all duration-300">
    <div class="relative">
      <input
        type="text"
        v-model="localSearchQuery"
        :placeholder="placeholder"
        class="w-full px-3 py-0.5 pl-8 rounded-[15px] bg-gray-50 border border-gray-200 text-sm text-slate-700 dark:text-white placeholder-gray-400 dark:placeholder-slate-300 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-300"
        @input="handleInput"
        @focus="$emit('focus')"
        @blur="$emit('blur')"
      />
      <i class="fa-solid fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-slate-300 text-sm"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

// 定义props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '搜索对话...'
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
/* 搜索框样式已通过内联class实现 */
/* 如需添加额外样式，可以在此处定义 */
</style>