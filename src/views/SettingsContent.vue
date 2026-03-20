<template>
  <!-- 设置内容区域 -->
  <div id="settingsMainContent" class="flex-1 flex flex-col overflow-hidden">
    <!-- 基本设置 -->

    <!-- 基本设置部分 -->
    <div class="settings-section active h-full overflow-y-auto p-6 scrollbar-hidden" id="general-section">
      <GeneralSettings />
    </div>

    <!-- 模型配置设置部分 -->
    <div class="settings-section hidden h-full p-6 scrollbar-hidden" id="models-section">
      <ModelsSettings />
    </div>

    <!-- 关于页面部分 -->
    <div class="settings-section hidden h-full overflow-y-auto p-6 scrollbar-hidden" id="about-section">
      <AboutSettings />
    </div>

    <!-- RAG配置部分 -->
    <div class="settings-section hidden h-full overflow-y-auto p-6 scrollbar-hidden" id="rag-section">
      <RAGSettings />
    </div>


  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import { useUiStore } from '../store/uiStore.js';
import GeneralSettings from '../components/settings/GeneralSettings.vue';
import ModelsSettings from '../components/settings/ModelsSettings.vue';
import AboutSettings from '../components/settings/AboutSettings.vue';
import RAGSettings from '../components/settings/RAGSettings.vue';

// 初始化store
const uiStore = useUiStore();

// 更新设置部分显示
const updateSettingsSection = () => {
  const activeSection = uiStore.activeSection || 'general';

  // 隐藏所有设置部分
  document.querySelectorAll('.settings-section').forEach((section) => {
    section.classList.add('hidden');
    section.classList.remove('active');
  });

  // 显示当前活动的设置部分
  const activeSectionElement = document.getElementById(`${activeSection}-section`);
  if (activeSectionElement) {
    activeSectionElement.classList.remove('hidden');
    activeSectionElement.classList.add('active');
  }
};

// 监听activeSection变化
watch(
  () => uiStore.activeSection,
  () => {
    updateSettingsSection();
  }
);

// 组件挂载时初始化
onMounted(() => {
  updateSettingsSection();
});
</script>
