import { createRouter, createWebHistory } from 'vue-router';
import { ROUTE_CONFIGS } from './constants.js';

// 导入视图组件（使用懒加载）
const HomeContent = () => import('../views/HomeContent.vue');
// ChatContent组件直接加载，避免首次跳转延迟
import ChatContent from '../views/ChatContent.vue';
const SettingsContent = () => import('../views/SettingsContent.vue');
const FileMangerContent = () => import('../views/FileMangerContent.vue');
const McpMangerContent = () => import('../views/McpMangerContent.vue');
const ContextVisualizationContent = () => import('../components/library/ContextVisualization/ContextVisualizationContent.vue');

// 组件映射
const componentMap = {
  Home: HomeContent,
  Chat: ChatContent,
  Setting: SettingsContent,
  FileManager: FileMangerContent,
  RagManagement: FileMangerContent,
  McpManagement: McpMangerContent,
  ContextVisualization: ContextVisualizationContent
};

// 生成路由配置
const routes = ROUTE_CONFIGS.map(config => ({
  ...config,
  component: componentMap[config.name]
}));

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 移除路由守卫，改为在App.vue中处理路由变化

export default router;