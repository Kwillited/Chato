<template>
  <!-- 导航栏 - 固定在顶部，包含左侧设置按钮和右侧菜单按钮 -->
  <div class="absolute top-0 left-0 right-0 h-8 bg-dark/80 backdrop-blur-md z-30 border border-blue-400/30 border-b-0 flex items-center justify-between px-3 hover-nav rounded-t-[12px]">
    <button 
      id="settings-button" 
      class="p-1 rounded-full hover:bg-blue-400/20 transition-colors duration-300 text-blue-300" 
      @click="onSettingsClick"
      title="打开设置面板"
    >
      <i class="fa-solid fa-gear text-xs"></i>
    </button>
    <button 
      id="menu-button" 
      class="p-1 rounded-full hover:bg-blue-400/20 transition-colors duration-300 text-blue-300" 
      @click="onMenuClick"
      title="{{ selectedNode ? '关闭节点信息' : '查看第一个节点信息' }}"
    >
      <i class="fa-solid fa-bars text-xs"></i>
    </button>
  </div>
</template>

<script setup>
// 定义组件的props
const _props = defineProps({
  selectedNode: {
    type: Object,
    default: null
  }
});

// 定义组件的emits
const emit = defineEmits(['settingsClick', 'menuClick']);

// 处理设置按钮点击事件
const onSettingsClick = () => {
  emit('settingsClick');
};

// 处理菜单按钮点击事件
const onMenuClick = () => {
  emit('menuClick');
};
</script>

<style scoped>
/* 导航栏默认隐藏，悬停显示 */
.hover-nav {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.hover-nav:hover {
  opacity: 1;
}
</style>