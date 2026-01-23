<template>
  <!-- Tauri 自定义菜单栏 -->
  <CustomMenuBar />
  
  <!-- 应用顶部导航栏 -->
  <HeaderNav />
</template>

<script setup>
import CustomMenuBar from './CustomMenuBar.vue';
import HeaderNav from './HeaderNav.vue';
</script>

<style scoped>
/* TopNav 组件作为容器，不包含具体样式 */
</style>