# 开发指南

## 1. 环境准备

### 1.1 系统要求

- Windows 10/11 (64位)
- macOS 11+ (Intel/Apple Silicon)
- Linux (64位)

### 1.2 软件依赖

| 软件 | 版本要求 | 用途 |
|------|----------|------|
| Node.js | v16+ | 前端开发环境 |
| npm | v7+ | Node.js 包管理器 |
| Rust | v1.89+ | Tauri 开发环境 |
| Cargo | v1.89+ | Rust 包管理器 |
| Python | v3.9+ | 后端开发环境 |
| pip | 最新版 | Python 包管理器 |

### 1.3 安装步骤

#### 1.3.1 安装 Node.js

从 [Node.js 官网](https://nodejs.org/) 下载并安装适合您系统的 Node.js 版本。

#### 1.3.2 安装 Rust

使用 Rustup 安装 Rust：

```bash
# Windows
download and run rustup-init.exe from https://rustup.rs/

# macOS/Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

#### 1.3.3 安装 Tauri 开发依赖

根据您的操作系统安装 Tauri 开发依赖：

- **Windows**：安装 Visual Studio 2022 Build Tools
- **macOS**：安装 Xcode Command Line Tools
- **Linux**：安装 GTK、WebKitGTK 和其他依赖

详细信息请参考 [Tauri 官方文档](https://tauri.app/v1/guides/getting-started/prerequisites/)

## 2. 项目初始化

### 2.1 克隆仓库

```bash
git clone <repository-url>
cd Chato
```

### 2.2 安装依赖

```bash
# 安装前端依赖
npm install

# 安装后端 Python 依赖
pip install -r src-tauri/python/requirements.txt
```

### 2.3 配置开发环境

1. 复制 `.env.example` 文件为 `.env`（如果存在）
2. 根据需要修改配置项

## 3. 开发流程

### 3.1 启动开发服务器

```bash
# 启动前端开发服务器
npm run dev

# 启动 Tauri 开发模式（推荐）
npm run tauri dev
```

### 3.2 代码风格

#### 3.2.1 前端代码风格

- 使用 ESLint 进行代码检查
- 遵循 Vue 3 最佳实践
- 使用 Composition API
- 组件命名使用 PascalCase
- 文件名使用 kebab-case

#### 3.2.2 后端代码风格

- 使用 PEP 8 编码规范
- 函数和变量名使用 snake_case
- 类名使用 PascalCase
- 模块名使用小写字母

### 3.3 提交代码

1. 确保所有代码通过 ESLint 检查：
   ```bash
   npm run lint
   ```

2. 提交代码遵循 Conventional Commits 规范：
   ```
   <type>[optional scope]: <description>
   
   [optional body]
   
   [optional footer(s)]
   ```

   常见类型：
   - feat: 新功能
   - fix: 修复 bug
   - docs: 文档变更
   - style: 代码风格调整
   - refactor: 代码重构
   - test: 测试相关
   - chore: 构建或工具变更

## 4. 前端开发

### 4.1 组件开发

#### 4.1.1 组件结构

每个组件应该包含：
- 模板（HTML）
- 脚本（JavaScript/TypeScript）
- 样式（CSS）

#### 4.1.2 组件创建流程

1. 在 `src/components/` 目录下创建组件文件夹
2. 创建 `.vue` 文件
3. 使用 Composition API 编写组件
4. 导出组件
5. 在需要的地方导入并使用

#### 4.1.3 组件示例

```vue
<template>
  <div class="my-component">
    <h2>{{ title }}</h2>
    <button @click="handleClick">{{ buttonText }}</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  buttonText: {
    type: String,
    default: 'Click Me'
  }
})

// Emits
const emit = defineEmits(['click'])

// Methods
const handleClick = () => {
  emit('click')
}
</script>

<style scoped>
.my-component {
  padding: 1rem;
  background-color: #f5f5f5;
  border-radius: 0.5rem;
}
</style>
```

### 4.2 组合函数开发

#### 4.2.1 组合函数结构

组合函数应该：
- 封装可复用的逻辑
- 返回响应式状态和方法
- 遵循单一职责原则

#### 4.2.2 组合函数示例

```javascript
import { ref, computed } from 'vue'

export function useCounter(initialValue = 0) {
  const count = ref(initialValue)
  
  const doubleCount = computed(() => count.value * 2)
  
  const increment = () => {
    count.value++
  }
  
  const decrement = () => {
    count.value--
  }
  
  const reset = () => {
    count.value = initialValue
  }
  
  return {
    count,
    doubleCount,
    increment,
    decrement,
    reset
  }
}
```

### 4.3 状态管理

使用 Pinia 进行状态管理：

1. 在 `src/store/` 目录下创建 store 文件
2. 定义 state、getters、actions
3. 导出 store

## 5. 后端开发

### 5.1 API 开发

使用 FastAPI 开发 API 接口：

1. 在 `src-tauri/python/app/api/` 目录下创建路由文件
2. 定义 API 端点
3. 实现业务逻辑
4. 添加请求和响应模型
5. 处理错误情况

### 5.2 服务层开发

1. 在 `src-tauri/python/app/services/` 目录下创建服务文件
2. 实现业务逻辑
3. 调用数据访问层
4. 返回处理结果

### 5.3 数据访问层开发

1. 在 `src-tauri/python/app/repositories/` 目录下创建仓库文件
2. 实现数据 CRUD 操作
3. 使用数据库连接池
4. 处理事务

## 6. 测试

### 6.1 前端测试

- 使用 Vitest 进行单元测试
- 使用 Cypress 进行端到端测试

### 6.2 后端测试

- 使用 pytest 进行单元测试
- 测试 API 端点
- 测试业务逻辑

### 6.3 运行测试

```bash
# 前端测试
npm run test

# 后端测试
cd src-tauri/python
pytest
```

## 7. 构建与部署

### 7.1 构建生产版本

```bash
# 构建前端
npm run build

# 构建 Tauri 应用
npm run tauri build
```

### 7.2 部署

构建完成后，可在 `src-tauri/target/release/` 目录下找到可执行文件。

## 8. 调试

### 8.1 前端调试

- 使用浏览器开发者工具
- 查看控制台日志
- 使用 Vue DevTools

### 8.2 后端调试

- 使用 Python 调试器
- 查看日志文件
- 使用 FastAPI 自动生成的文档（/docs）

### 8.3 前后端通信调试

- 查看网络请求
- 使用 Tauri 开发工具
- 检查 IPC 通信

## 9. 常见问题

### 9.1 依赖安装失败

- 检查 Node.js 和 Python 版本
- 清理缓存后重试
- 检查网络连接

### 9.2 开发服务器启动失败

- 检查端口是否被占用
- 检查配置文件
- 查看错误日志

### 9.3 前后端通信问题

- 检查 Tauri 配置
- 检查 API 端点
- 查看控制台错误

## 10. 贡献指南

1. Fork 仓库
2. 创建特性分支
3. 提交代码
4. 创建 Pull Request
5. 等待代码审查
6. 合并到主分支

## 11. 开发工具推荐

- **IDE**：VS Code + Volar + Rust Analyzer
- **浏览器**：Chrome + Vue DevTools
- **调试工具**：Postman（API 测试）
- **终端**：Windows Terminal / iTerm2

## 12. 学习资源

- [Vue 3 官方文档](https://vuejs.org/)
- [Tauri 官方文档](https://tauri.app/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Rust 官方文档](https://www.rust-lang.org/learn)
- [Composition API 指南](https://vuejs.org/guide/extras/composition-api-faq.html)
