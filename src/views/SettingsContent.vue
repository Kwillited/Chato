<template>
  <!-- 设置内容区域 -->
  <div id="settingsMainContent" class="flex-1 flex flex-col overflow-hidden">
    <!-- 基本设置 -->
    <!-- 标题栏 - 使用全局panel-header样式 -->
    <div class="panel-header">
      <div class="flex items-center gap-6">
        <h2 class="text-lg font-bold text-dark" id="currentSettingTitle">基本设置</h2>
      </div>
    </div>
    <!-- 基本设置部分 -->
    <div class="settings-section active h-full overflow-y-auto p-6 scrollbar-hidden" id="general-section">
      <GeneralSettings />
    </div>

    <!-- 模型配置设置部分 -->
    <div class="settings-section hidden h-full overflow-y-auto p-6 scrollbar-hidden" id="models-section">
      <ModelsSettings />
    </div>

    <!-- 通知设置部分 -->
    <div class="settings-section hidden h-full overflow-y-auto p-6 scrollbar-hidden" id="notifications-section">
      <NotificationsSettings />
    </div>

    <!-- 关于页面部分 -->
    <div class="settings-section hidden h-full overflow-y-auto p-6 scrollbar-hidden" id="about-section">
      <AboutSettings />
    </div>

    <!-- RAG配置部分 -->
    <div class="settings-section hidden h-full overflow-y-auto p-6 scrollbar-hidden" id="rag-section">
      <RAGSettings />
    </div>

    <!-- MCP服务设置部分 -->
    <div class="settings-section hidden h-full overflow-y-auto p-6 scrollbar-hidden" id="mcp-section">
      <McpSettings />
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import { useSettingsStore } from '../store/settingsStore.js';
import GeneralSettings from '../components/settings/GeneralSettings.vue';
import ModelsSettings from '../components/settings/ModelsSettings.vue';
import NotificationsSettings from '../components/settings/NotificationsSettings.vue';
import AboutSettings from '../components/settings/AboutSettings.vue';
import RAGSettings from '../components/settings/RAGSettings.vue';
import McpSettings from '../components/settings/McpSettings.vue';

// 初始化store
const settingsStore = useSettingsStore();



// 更新设置部分显示
const updateSettingsSection = () => {
  const activeSection = settingsStore.activeSection || 'general';

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

  // 更新设置标题
  const titleElement = document.getElementById('currentSettingTitle');
  if (titleElement) {
    const sectionTitles = {
      general: '基本设置',
      models: '模型配置',
      notifications: '通知设置',
      about: '关于页面',
      rag: '知识库配置',
      mcp: 'MCP服务设置',
    };
    titleElement.textContent = sectionTitles[activeSection] || '设置';
  }
};

// 监听activeSection变化
watch(
  () => settingsStore.activeSection,
  () => {
    updateSettingsSection();
  }
);

// 组件挂载时初始化
onMounted(() => {
  updateSettingsSection();
});
</script>
