<template>
  <Header
    :title="title"
    :showBackButton="showBackButton && !hideDefaultActions"
    :backButtonId="backButtonId"
  >
    <slot name="actions"></slot>
  </Header>
</template>

<script setup>
import Header from './Header.vue';

// 定义props
defineProps({
  title: {
    type: String,
    required: true
  },
  showBackButton: {
    type: Boolean,
    default: true
  },
  backButtonId: {
    type: String,
    default: 'backToChatBtn'
  },
  hideDefaultActions: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
</style>