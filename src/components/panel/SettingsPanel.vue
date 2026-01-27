<template>
  <div id="settingsPanel" class="h-full flex flex-col">
    <div class="overflow-y-auto h-full scrollbar-thin">
      <div class="p-2 space-y-1">
        <SettingNavItem 
          id="general" 
          :activeSection="uiStore.activeSection"
          label="基本设置" 
          iconClass="fa-regular fa-user"
          @click="handleSectionClick"
        />
        <SettingNavItem 
          id="models" 
          :activeSection="uiStore.activeSection"
          label="模型配置" 
          iconClass="fa-solid fa-gears"
          @click="handleSectionClick"
        />
        <SettingNavItem 
          id="rag" 
          :activeSection="uiStore.activeSection"
          label="知识库配置" 
          iconClass="fa-solid fa-book-open"
          @click="handleSectionClick"
        />
        <SettingNavItem 
          id="mcp" 
          :activeSection="uiStore.activeSection"
          label="MCP服务" 
          iconClass="fa-solid fa-server"
          @click="handleSectionClick"
        />
        <SettingNavItem 
          id="notifications" 
          :activeSection="uiStore.activeSection"
          label="通知设置" 
          iconClass="fa-regular fa-bell"
          @click="handleSectionClick"
        />
        <SettingNavItem 
          id="about" 
          :activeSection="uiStore.activeSection"
          label="关于" 
          iconClass="fa-solid fa-circle-info"
          @click="handleSectionClick"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUiStore } from '../../store/uiStore.js';
import SettingNavItem from '../common/SettingNavItem.vue';


const uiStore = useUiStore();

// 组件挂载时，确保store中至少有一个选中的section
onMounted(() => {
  if (!uiStore.activeSection) {
    uiStore.setActiveSection('general');
  }
});

// 使用PanelHeader组件的默认返回行为
// 注：返回功能已在PanelHeader组件中实现

// 处理设置项点击事件
const handleSectionClick = (section) => {
  // section参数会从SettingNavItem组件的click事件中传递过来
  uiStore.setActiveSection(section);
};
</script>

<style scoped>
/* 组件特定样式 - 遵循项目整体风格 */

/* 面板标题深色模式 */
.dark .panel-header h2 {
  color: #e2e8f0;
}


</style>
