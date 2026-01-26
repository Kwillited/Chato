import { createApp } from 'vue';
import App from './app/App.vue';
import pinia from './app/store/pinia.js';
import router from './app/router/index.js';
import logger from './shared/utils/logger.js'; // 引入日志工具

// 等待DOM完全加载后再初始化Vue应用
document.addEventListener('DOMContentLoaded', () => {
  try {
    // 创建Vue应用并使用Pinia和Router
    const app = createApp(App);
    app.use(pinia);
    app.use(router);
    app.mount('#app');

    logger.info('Vue应用已成功挂载到#app元素，并配置了Pinia状态管理和Vue Router');
  } catch (error) {
    logger.error('Vue应用挂载失败:', error);
  }
});