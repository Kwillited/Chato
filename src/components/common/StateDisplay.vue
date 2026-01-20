<template>
  <div class="state-display" :class="containerClass">
    <!-- 加载状态 -->
    <div v-if="type === 'loading'" class="state-content flex flex-col items-center justify-center">
      <Loading 
        :type="loadingType" 
        :size="loadingSize" 
        :color="loadingColor"
        :text="message || defaultMessages.loading" 
        :container-class="loadingContainerClass"
      />
      <slot name="actions"></slot>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="type === 'empty'" class="state-content flex flex-col items-center justify-center">
      <i :class="['fa-solid', icon || defaultIcons.empty, iconClass]"></i>
      <h3 class="state-title text-lg font-medium mb-1">{{ title || defaultTitles.empty }}</h3>
      <p class="state-message text-neutral text-sm mb-4">{{ message || defaultMessages.empty }}</p>
      <slot name="actions"></slot>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="type === 'error'" class="state-content flex flex-col items-center justify-center">
      <i :class="['fa-solid', icon || defaultIcons.error, iconClass]"></i>
      <h3 class="state-title text-lg font-medium mb-1">{{ title || defaultTitles.error }}</h3>
      <p class="state-message text-neutral text-sm mb-4">{{ message || defaultMessages.error }}</p>
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
import Loading from './Loading.vue';

defineProps({
  // 状态类型：loading（加载）、empty（空）、error（错误）
  type: {
    type: String,
    required: true,
    validator: (value) => ['loading', 'empty', 'error'].includes(value)
  },
  // 标题
  title: {
    type: String,
    default: ''
  },
  // 消息内容
  message: {
    type: String,
    default: ''
  },
  // 图标类名
  icon: {
    type: String,
    default: ''
  },
  // 容器类名
  containerClass: {
    type: String,
    default: 'text-center py-6'
  },
  // 图标类名
  iconClass: {
    type: String,
    default: 'text-4xl text-gray-300 mb-3'
  },
  // 加载相关配置
  loadingType: {
    type: String,
    default: 'spin'
  },
  loadingSize: {
    type: String,
    default: 'large'
  },
  loadingColor: {
    type: String,
    default: ''
  },
  loadingContainerClass: {
    type: String,
    default: ''
  }
});

// 默认标题
const defaultTitles = {
  loading: '加载中',
  empty: '暂无数据',
  error: '操作失败'
};

// 默认消息
const defaultMessages = {
  loading: '加载中...',
  empty: '这里还没有任何内容',
  error: '发生了一些错误'
};

// 默认图标
const defaultIcons = {
  empty: 'fa-inbox',
  error: 'fa-exclamation-circle'
};
</script>

<style scoped>
.state-display {
  transition: all 0.3s ease;
}
</style>