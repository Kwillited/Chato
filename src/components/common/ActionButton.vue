<template>
  <Tooltip :content="title">
    <button
      class="btn-secondary flex items-center justify-center transition-all duration-300"
      :class="['w-8 h-8 p-1.5 rounded-full text-neutral dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-700', $attrs.class]"
      @click="handleClick"
      v-bind="$attrs"
    >
      <i :class="['fa-solid', icon.startsWith('fa-') ? icon : 'fa-' + icon]"></i>
    </button>
  </Tooltip>
</template>

<script setup>
import { Tooltip } from '../library/index.js';

// 定义组件属性
defineProps({
  icon: {
    type: String,
    required: true,
    validator: (value) => {
      // 基本的Font Awesome图标验证
      return typeof value === 'string' && value.length > 0;
    }
  },
  title: {
    type: String,
    required: true
  }
});

// 定义组件事件
const emit = defineEmits(['click']);

// 定义组件名称和属性继承选项
// 使用defineOptions API注册组件名称，替代旧的export default语法
// 注意：defineOptions必须在defineProps和defineEmits之后调用
defineOptions({
  name: 'ActionButton',
  inheritAttrs: false // 阻止Vue自动将$attrs传递给组件根元素
});

// 处理点击事件并传递事件对象
const handleClick = (event) => {
  emit('click', event);
};
</script>

<style scoped>
/* 样式已内联在模板中 */
</style>