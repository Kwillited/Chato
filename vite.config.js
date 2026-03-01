import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

  server: {
    //端口配置
    port: 18450,
    strictPort: true,
    //热载配置
    hmr: {
      protocol: "ws",
      port: 18451,
    },
    // API代理配置
    proxy: {
      // 为图标请求添加特殊处理，保留完整路径
      '/api/models/icons': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      // 其他API请求移除/api前缀
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  },
  
  // 构建配置
  build: {
    // 修改构建目录为 build
    outDir: 'web_dist',
    // 代码分割配置
    rollupOptions: {
      output: {
        // 手动代码分割配置
        manualChunks: (id) => {
          // 第三方库单独分割
          if (id.includes('node_modules')) {
            if (id.includes('pinia')) {
              return 'pinia';

            } else if (id.includes('highlight')) {
              return 'highlight';
            } else if (id.includes('marked')) {
              return 'marked';
            } else if (id.includes('vue')) {
              return 'vue';
            }
            return 'vendor';
          }
          // 按功能模块分割
          if (id.includes('src/components/chat')) return 'chat';
          if (id.includes('src/components/rag')) return 'rag';
          if (id.includes('src/components/settings')) return 'settings';
        }
      }
    },
    // 增加chunk大小警告阈值
    chunkSizeWarningLimit: 1000
  },
  
  // 资源处理配置
  assetsInclude: [
    '**/*.woff',
    '**/*.woff2',
    '**/*.ttf',
    '**/*.eot'
  ]
});
