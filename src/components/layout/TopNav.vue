<template>
  <!-- Tauri 自定义菜单栏 -->
  <CustomMenuBar />
  
  <!-- 应用顶部导航栏 - 仅在非设置页面显示 -->
  <HeaderNav v-if="settingsStore.activeContent !== 'settings'" />
</template>

<script setup>
import CustomMenuBar from './CustomMenuBar.vue';
import HeaderNav from './HeaderNav.vue';
import { useSettingsStore } from '../../store/settingsStore.js';

// 初始化stores
const settingsStore = useSettingsStore();
</script>

<style scoped>
/* TopNav 组件作为容器，不包含具体样式 */
</style>