import { createApp } from 'vue';
import App from './App.vue';
import pinia from './store/pinia.js';
import router from './router/index.js';

// 导入Markdown插件
import MarkdownPlugin from './plugins/markdown/index.js';

// 导入代码块样式
import './assets/styles/codeBlock.css';

// 等待DOM完全加载后再初始化Vue应用
document.addEventListener('DOMContentLoaded', () => {
  try {
    // 创建Vue应用并使用Pinia和路由
    const app = createApp(App);
    app.use(pinia);
    app.use(router);
    // 注册Markdown插件
    app.use(MarkdownPlugin);
    app.mount('#app');

    console.log('Vue应用已成功挂载到#app元素，并配置了Pinia状态管理');
  } catch (error) {
    console.error('Vue应用挂载失败:', error);
  }
});