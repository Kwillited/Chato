import { createRouter, createWebHistory } from 'vue-router';
import AppLayout from '../../shared/ui/layout/AppLayout.vue';
import ChatContent from '../../pages/chat/ChatContent.vue';
import SettingsPage from '../../pages/chat/SettingsPage.vue';
import Home from '../../pages/chat/home.vue';

const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: Home
      },
      {
        path: 'chat',
        name: 'Chat',
        component: ChatContent
      },
      {
        path: 'settings',
        name: 'Settings',
        component: SettingsPage
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;