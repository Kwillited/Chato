<template>
  <div class="relative flex items-center justify-center" ref="tooltipWrapper">
    <slot></slot>
    <!-- 预渲染的隐藏tooltip，用于获取准确的尺寸 -->
    <div
      v-if="content"
      class="absolute left-[-9999px] top-[-9999px] opacity-0 visibility-hidden pointer-events-none whitespace-nowrap bg-black/80 text-white px-2 py-1 rounded text-xs custom-tooltip tooltip-measure"
    >
      {{ content }}
    </div>
    <!-- 实际显示的tooltip，使用Teleport挂载到body -->
    <Teleport to="body">
      <div
        v-if="show && content"
        class="fixed z-50 bg-black/80 text-white px-2 py-1 rounded text-xs shadow-lg custom-tooltip"
        :style="tooltipStyle"
      >
        {{ content }}
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import logger from '../../utils/logger.js';

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

// 阻止Vue自动将$attrs传递给组件根元素
defineOptions({
  name: 'BaseTooltip',
  inheritAttrs: false
});

const show = ref(false);
const tooltipWrapper = ref(null);
const tooltipStyle = ref({});

// 计算tooltip位置
const calculatePosition = () => {
  if (!tooltipWrapper.value) return;
  
  try {
    const wrapperRect = tooltipWrapper.value.getBoundingClientRect();
    
    // 优先使用预渲染的测量元素获取尺寸，确保准确性
    let tooltipElement = tooltipWrapper.value.querySelector('.custom-tooltip.tooltip-measure');
    let tooltipRect;
    
    if (tooltipElement) {
      // 使用预渲染元素获取尺寸
      tooltipRect = tooltipElement.getBoundingClientRect();
    } else {
      // 备用方案：使用实际显示的tooltip元素
      tooltipElement = tooltipWrapper.value.querySelector('.custom-tooltip:not(.tooltip-measure)');
      if (!tooltipElement) return;
      tooltipRect = tooltipElement.getBoundingClientRect();
    }
    
    // 计算位置，添加防护措施确保数值有效
    const style = {
      position: 'fixed',
      zIndex: '9999', // 确保层级最高
      pointerEvents: 'none',
      // 初始位置设置，避免闪烁
      visibility: 'hidden'
    };
    
    // 根据placement计算位置，直接计算准确位置，不使用transform居中
    switch (props.placement) {
      case 'top':
        style.top = `${Math.max(0, wrapperRect.top - tooltipRect.height - 8)}px`;
        style.left = `${Math.max(0, wrapperRect.left + wrapperRect.width / 2 - tooltipRect.width / 2)}px`;
        // 初始transform用于动画，后续由CSS动画控制
        style.transform = 'translateY(0)';
        break;
      case 'bottom':
        style.top = `${Math.max(0, wrapperRect.bottom + 8)}px`;
        style.left = `${Math.max(0, wrapperRect.left + wrapperRect.width / 2 - tooltipRect.width / 2)}px`;
        style.transform = 'translateY(0)';
        break;
      case 'left':
        style.top = `${Math.max(0, wrapperRect.top + wrapperRect.height / 2 - tooltipRect.height / 2)}px`;
        style.left = `${Math.max(0, wrapperRect.left - tooltipRect.width - 8)}px`;
        style.transform = 'translateX(0)';
        break;
      case 'right':
        style.top = `${Math.max(0, wrapperRect.top + wrapperRect.height / 2 - tooltipRect.height / 2)}px`;
        style.left = `${Math.max(0, wrapperRect.right + 8)}px`;
        style.transform = 'translateX(0)';
        break;
      default:
        break;
    }
    
    // 移除visibility控制，直接应用样式
    style.visibility = 'visible';
    tooltipStyle.value = style;
  } catch (error) {
    logger.error('Tooltip position calculation error:', error);
  }
};

// 显示tooltip
const showTooltip = () => {
  // 先计算位置，再显示tooltip，确保首次显示就在正确位置
  nextTick(() => {
    calculatePosition();
    show.value = true;
  });
};

// 隐藏tooltip
const hideTooltip = () => {
  show.value = false;
};

// 监听窗口大小变化，重新计算位置
const handleResize = () => {
  if (show.value) {
    calculatePosition();
  }
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

