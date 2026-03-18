<template>
  <div 
    class="relative inline-flex bg-gray-100 dark:bg-gray-800 p-0.5 shadow-sm" 
    :class="containerClass"
    :style="containerStyle"
  >
    <button
      v-for="(tab, index) in tabs"
      :key="tab.id || index"
      class="relative flex-1 py-1.5 text-sm font-medium transition-all duration-200 z-10 text-center"
      :class="[
        tabClass,
        {
          'text-white font-medium': activeTab === (tab.id || index),
          'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white': activeTab !== (tab.id || index)
        }
      ]"
      :style="buttonStyle"
      @click="handleTabClick(tab.id || index)"
    >
      {{ tab.name }}
    </button>
    <!-- 滑动块 -->
    <span
      class="absolute top-0.5 bottom-0.5 bg-gray-800 dark:bg-gray-700 transition-all duration-300 ease-in-out"
      :style="sliderStyle"
    ></span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  tabs: {
    type: Array,
    required: true,
    default: () => []
  },
  activeTab: {
    type: [String, Number],
    required: true
  },
  containerClass: {
    type: String,
    default: ''
  },
  tabClass: {
    type: String,
    default: ''
  },
  borderRadius: {
    type: String,
    default: '9999px' // 默认圆角
  },
  buttonRadius: {
    type: String,
    default: '' // 默认为空，使用borderRadius
  }
});

const emit = defineEmits(['tabChange']);

const handleTabClick = (tabId) => {
  emit('tabChange', tabId);
};

const containerStyle = computed(() => {
  return {
    borderRadius: props.borderRadius
  };
});

const buttonStyle = computed(() => {
  return {
    borderRadius: props.buttonRadius || props.borderRadius
  };
});

const sliderStyle = computed(() => {
  const tabIndex = props.tabs.findIndex(tab => (tab.id || props.tabs.indexOf(tab)) === props.activeTab);
  const tabCount = props.tabs.length;
  const widthPercent = 100 / tabCount;
  const leftPercent = tabIndex * widthPercent;
  
  return {
    left: `${leftPercent}%`,
    width: `${widthPercent}%`,
    borderRadius: props.borderRadius
  };
});
</script>

<style scoped>
/* 可以添加额外的组件样式 */
</style>