<template>
  <div class="relative flex items-center justify-center" ref="tooltipWrapper">
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import tooltipManager from '../../utils/tooltipManager';

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  placement: {
    type: String,
    default: 'bottom',
    validator: (value) => {
      return ['top', 'bottom', 'left', 'right'].includes(value);
    }
  }
});

// 解构 props
const { content, placement } = props;

// 阻止Vue自动将$attrs传递给组件根元素
defineOptions({
  name: 'BaseTooltip',
  inheritAttrs: false
});

const tooltipWrapper = ref(null);

// 计算tooltip位置
const calculatePosition = () => {
  if (!tooltipWrapper.value || !content) return null;
  
  try {
    const wrapperRect = tooltipWrapper.value.getBoundingClientRect();
    
    // 创建临时元素用于测量尺寸
    const tempElement = document.createElement('div');
    tempElement.className = 'absolute left-[-9999px] top-[-9999px] opacity-0 visibility-hidden pointer-events-none whitespace-nowrap bg-black/80 text-white px-2 py-1 rounded text-xs custom-tooltip';
    tempElement.textContent = content;
    document.body.appendChild(tempElement);
    
    // 获取临时元素的尺寸
    const tooltipRect = tempElement.getBoundingClientRect();
    
    // 移除临时元素
    document.body.removeChild(tempElement);
    
    // 计算位置，添加防护措施确保数值有效
    const position = {};
    
    // 根据placement计算位置，直接计算准确位置，不使用transform居中
    switch (placement) {
      case 'top':
        position.top = Math.max(0, wrapperRect.top - tooltipRect.height - 8);
        position.left = Math.max(0, wrapperRect.left + wrapperRect.width / 2 - tooltipRect.width / 2);
        break;
      case 'bottom':
        position.top = Math.max(0, wrapperRect.bottom + 8);
        position.left = Math.max(0, wrapperRect.left + wrapperRect.width / 2 - tooltipRect.width / 2);
        break;
      case 'left':
        position.top = Math.max(0, wrapperRect.top + wrapperRect.height / 2 - tooltipRect.height / 2);
        position.left = Math.max(0, wrapperRect.left - tooltipRect.width - 8);
        break;
      case 'right':
        position.top = Math.max(0, wrapperRect.top + wrapperRect.height / 2 - tooltipRect.height / 2);
        position.left = Math.max(0, wrapperRect.right + 8);
        break;
      default:
        break;
    }
    
    return position;
  } catch (error) {
    console.error('Tooltip position calculation error:', error);
    return null;
  }
};

// 显示tooltip
const showTooltip = () => {
  if (!content) return;
  const position = calculatePosition();
  if (position) {
    tooltipManager.show({
      content,
      position,
      placement
    });
  }
};

// 隐藏tooltip
const hideTooltip = () => {
  tooltipManager.hide();
};

// 监听窗口大小变化，重新计算位置
const handleResize = () => {
  // 窗口大小变化时，隐藏tooltip
  tooltipManager.hide();
};

// 添加防抖处理，避免频繁计算位置
let resizeTimeout;
const debouncedHandleResize = () => {
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
  resizeTimeout = setTimeout(handleResize, 100);
};

onMounted(() => {
  const wrapper = tooltipWrapper.value;
  if (wrapper) {
    // 使用pointerover和pointerout事件，提供更好的跨设备支持
    // 添加passive: true优化性能
    wrapper.addEventListener('pointerover', showTooltip, { passive: true });
    wrapper.addEventListener('pointerout', hideTooltip, { passive: true });
    window.addEventListener('resize', debouncedHandleResize);
  }
});

onUnmounted(() => {
  const wrapper = tooltipWrapper.value;
  if (wrapper) {
    wrapper.removeEventListener('pointerover', showTooltip);
    wrapper.removeEventListener('pointerout', hideTooltip);
    window.removeEventListener('resize', debouncedHandleResize);
    if (resizeTimeout) {
      clearTimeout(resizeTimeout);
    }
  }
});
</script>

