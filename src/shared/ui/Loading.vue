<template>
  <div class="loading-container" :class="containerClass">
    <!-- 旋转动画 -->
    <div v-if="type === 'spin'" class="loading-spin-container">
      <div 
        class="animate-spin rounded-full"
        :style="spinStyle"
      ></div>
    </div>
    
    <!-- 打字动画 -->
    <div v-else-if="type === 'typing'" class="loading-typing-container">
      <div 
        v-for="i in 3" 
        :key="i" 
        class="loading-typing-dot animate-bounce rounded-full"
        :style="{
          animationDelay: `${i * 150}ms`,
          width: computedDotSize,
          height: computedDotSize,
          backgroundColor: color
        }"
      ></div>
    </div>
    
    <!-- 文本内容 -->
    <div v-if="text" class="loading-text" :style="{ color: textColor }">
      {{ text }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

defineOptions({
  name: 'BaseLoading'
});

const props = defineProps({
  // 动画类型：spin（旋转）、typing（打字）
  type: {
    type: String,
    default: 'spin',
    validator: (value) => ['spin', 'typing'].includes(value)
  },
  // 颜色
  color: {
    type: String,
    default: 'var(--loading-primary-color)'
  },
  // 大小：small（小）、medium（中）、large（大）
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 自定义大小（覆盖size属性）
  customSize: {
    type: String,
    default: ''
  },
  // 文本内容
  text: {
    type: String,
    default: ''
  },
  // 文本颜色
  textColor: {
    type: String,
    default: 'var(--loading-text-color)'
  },
  // 容器类名
  containerClass: {
    type: String,
    default: ''
  },
  // 圆点大小（仅打字动画，覆盖size属性）
  dotSize: {
    type: String,
    default: ''
  }
});

// 计算旋转动画样式
const spinStyle = computed(() => {
  // 大小映射
  const sizeMap = {
    small: 'var(--loading-spin-small)',
    medium: 'var(--loading-spin-medium)',
    large: 'var(--loading-spin-large)'
  };
  
  // 边框宽度映射
  const borderWidthMap = {
    small: '2px',
    medium: '2px',
    large: '3px'
  };
  
  const size = props.customSize || sizeMap[props.size];
  const borderWidth = borderWidthMap[props.size];
  
  return {
    width: size,
    height: size,
    borderTopColor: props.color,
    borderRightColor: 'transparent',
    borderBottomColor: 'transparent',
    borderLeftColor: 'transparent',
    borderWidth: borderWidth,
    borderStyle: 'solid'
  };
});

// 计算打字动画圆点大小
const computedDotSize = computed(() => {
  if (props.dotSize) {
    return props.dotSize;
  }
  
  const dotSizeMap = {
    small: 'var(--loading-typing-dot-small)',
    medium: 'var(--loading-typing-dot-medium)',
    large: 'var(--loading-typing-dot-large)'
  };
  
  return dotSizeMap[props.size];
});
</script>

<style scoped>
/* 容器样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--loading-container-gap);
}

/* 旋转动画容器 */
.loading-spin-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 打字动画容器 */
.loading-typing-container {
  display: flex;
  gap: 0.25rem;
  align-items: center;
  justify-content: center;
}
</style>