<template>
  <div class="relative flex justify-center">
    <button
      v-if="isVisible"
      class="absolute bottom-full mb-3 bg-primary text-white w-8 h-8 rounded-full shadow-lg flex items-center justify-center hover:bg-primary/80 transition-all duration-300 z-10"
      @click="handleScrollToBottom"
    >
      <i class="fa-solid fa-chevron-down"></i>
    </button>
  </div>
</template>

<script setup>


// 定义props
defineProps({
  isVisible: {
    type: Boolean,
    default: false
  }
});

// 定义事件
const emit = defineEmits(['scrollToBottom']);

// 处理滚动到底部按钮点击事件
const handleScrollToBottom = () => {
  emit('scrollToBottom');
};
</script>