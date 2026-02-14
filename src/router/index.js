import { createRouter, createWebHistory } from 'vue-router';

// 导入视图组件（使用懒加载）
const HomeContent = () => import('../views/HomeContent.vue');
const ChatContent = () => import('../views/ChatContent.vue');
const SettingsContent = () => import('../views/SettingsContent.vue');
const FileMangerContent = () => import('../views/FileMangerContent.vue');
const McpMangerContent = () => import('../views/McpMangerContent.vue');
const ContextVisualizationContent = () => import('../components/library/ContextVisualization/ContextVisualizationContent.vue');

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeContent,
    meta: { activeContent: 'home' }
  },
  {
    path: '/chat/:uuid',
    name: 'Chat',
    component: ChatContent,
    meta: { activeContent: 'chat' },
    props: true
  },
  {
    path: '/setting',
    name: 'Setting',
    component: SettingsContent,
    meta: { activeContent: 'settings' }
  },
  {
    path: '/file',
    name: 'FileManager',
    component: FileMangerContent,
    meta: { activeContent: 'fileManager' }
  },
  {
    path: '/mcp',
    name: 'McpManagement',
    component: McpMangerContent,
    meta: { activeContent: 'mcpManagement' }
  },
  {
    path: '/context',
    name: 'ContextVisualization',
    component: ContextVisualizationContent,
    meta: { activeContent: 'contextVisualization' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 移除路由守卫，改为在App.vue中处理路由变化

export default router;