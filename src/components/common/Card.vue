<template>
  <div
    :class="[
      'card-wrapper',
      hoverClasses,
      showComet ? 'has-comet' : 'standard-border',
      $attrs.class
    ]"
    v-bind="$attrs"
  >
    <!-- 1. 彗星流光层：仅在 showComet 为 true 时渲染 -->
    <div v-if="showComet" class="comet-container">
      <div class="comet-rotate-layer">
        <div class="comet-glow"></div>
        <div class="comet-tail"></div>
      </div>
    </div>

    <!-- 2. 内容遮罩层：背景色设为 Tailwind 700 (#374151) -->
    <div class="card-content">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  hoverable: { type: Boolean, default: true },
  comet: { type: Boolean, default: false },
  darkComet: { type: Boolean, default: false }
});

defineOptions({ name: 'Card', inheritAttrs: false });

// 检测当前是否处于暗色模式
const isDarkMode = ref(false);

// 检测函数
const checkDarkMode = () => {
  isDarkMode.value = document.documentElement.classList.contains('dark');
};

// 监听暗色模式变化
onMounted(() => {
  checkDarkMode();
  // 监听系统主题变化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  mediaQuery.addEventListener('change', checkDarkMode);
  // 监听 document.documentElement 的 classList 变化
  const observer = new MutationObserver(checkDarkMode);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
});

// 计算是否显示彗星效果：当手动设置了 comet 为 true，或者处于暗色模式且设置了 darkComet 为 true 时
const showComet = computed(() => props.comet || (isDarkMode.value && props.darkComet));

const hoverClasses = computed(() => (props.hoverable ? 'hoverable' : ''));
</script>

<style scoped>
/* 基础容器 */
.card-wrapper {
  position: relative;
  border-radius: 20px;
  overflow: visible; /* 允许下拉菜单显示 */
  display: flex;
  flex-direction: column;
  min-height: 0; /* 重要：允许flex子项缩小到内容以下 */
  transition: all 0.3s ease;
  /* 默认保持你原来的背景色逻辑 */
  background-color: white; 
}

/* 彗星流光容器：强制居中正方形旋转 */
.comet-container {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-base);
  pointer-events: none;
  overflow: hidden; /* 限制流光效果在卡片边界内 */
  border-radius: 20px; /* 与卡片容器相同的圆角 */
}

.comet-rotate-layer {
  /* 关键：无论卡片多长，旋转层始终是正方形，保证轨迹圆滑 */
  width: 400%; /* 足够大以覆盖长对角线 */
  aspect-ratio: 1 / 1; 
  position: absolute;
  animation: spin-border 4s linear infinite;
}

@keyframes spin-border {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 彗星样式 */
.comet-tail {
  position: absolute;
  inset: 0;
  background: conic-gradient(
    from 0deg, 
    transparent 65%, 
    rgba(6, 182, 212, 0.9) 95%, 
    #fff 100%
  );
}

.comet-glow {
  position: absolute;
  inset: 0;
  background: conic-gradient(
    from 0deg, 
    transparent 75%, 
    rgba(6, 182, 212, 0.5) 95%, 
    rgba(255, 255, 255, 0.7) 100%
  );
  filter: blur(15px);
}

/* 内容层（遮罩层） */
.card-content {
  position: relative;
  z-index: var(--z-card);
  flex: 1;
  margin: 2px; /* 边框厚度 */
  border-radius: 18px;
  background: inherit; /* 自动跟随父级背景 */
  display: flex;
  flex-direction: column;
  min-height: 0; /* 重要：允许flex子项缩小到内容以下 */
}

/* --- 状态样式 --- */

/* 1. 开启彗星时的背景：强制使用 Tailwind 700 */
.has-comet {
  background-color: #374151 !important; /* Tailwind gray-700 */
  border: none;
}
.has-comet .card-content {
  background-color: #374151 !important; 
  color: white;
}

/* 2. 标准模式样式 */
.standard-border {
  border: 1px solid #e2e8f0;
}
.standard-border .card-content { 
  margin: 0; 
  border-radius: 19px;
}

</style>

<style>
/* 暗色模式支持 */
.dark .card-wrapper {
  background-color: #374151; /* gray-700 */
  border-color: rgba(255, 255, 255, 0.1);
}

/* Enter 按钮暗色模式支持 */
.dark button.text-black.bg-white {
  background-color: #374151;
  color: white;
  border-color: #4b5563;
}

.dark button.text-black.bg-white:hover {
  background-color: #4b5563;
  border-color: #6b7280;
}
</style>