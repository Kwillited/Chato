import { createRouter, createWebHistory } from 'vue-router';
import App from '../App.vue'; // 你的主应用组件

const routes = [
  {
    path: '/',
    name: 'Home',
    component: App
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;