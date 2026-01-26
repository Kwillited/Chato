import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const host = process.env.TAURI_DEV_HOST;

// https://vite.dev/config/
export default defineConfig(async () => ({
  plugins: [vue()],

  // 为 Tauri 开发量身定制的 Vite 选项，仅在 tauri dev 或 tauri build 时应用
  // 1. 防止 Vite 掩盖 Rust 错误
  clearScreen: false,
  // 2. Tauri 期望使用一个固定端口，若该端口不可用则运行失败
  server: {
    //端口配置
    port: 18450,
    strictPort: true,
    host: host || false,
    //热载配置
    hmr: host
      ? {
          protocol: "ws",
          host,
          port: 18451,
        }
      : undefined,
    watch: {
      // 3. 告知 Vite 忽略对 src-tauri 目录的监听
      ignored: ["**/src-tauri/**"],
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
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  
  // 构建配置
  build: {
    // 代码分割配置
    rollupOptions: {
      // 外部化Tauri API模块，这些模块只在运行时可用
      external: [
        '@tauri-apps/api',
        '@tauri-apps/api/invoke',
        '@tauri-apps/api/core',
        '@tauri-apps/api/tauri'
      ],
      output: {
        // 手动代码分割配置
        manualChunks: (id) => {
          // 第三方库单独分割
          if (id.includes('node_modules')) {
            if (id.includes('pinia')) {
              return 'pinia';
            } else if (id.includes('katex')) {
              return 'katex';
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
          if (id.includes('src/store/chatStore')) return 'chat';
          if (id.includes('src/store/ragStore')) return 'rag';
          if (id.includes('src/store/settingsStore')) return 'settings';
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
}));
