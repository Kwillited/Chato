// 路由路径常量
export const ROUTES = {
  HOME: '/',
  CHAT: '/chat/:uuid',
  SETTING: '/setting',
  FILE: '/file',
  RAG: '/rag',
  MCP: '/mcp',
  CONTEXT: '/context'
};

// 路由名称常量
export const ROUTE_NAMES = {
  HOME: 'Home',
  CHAT: 'Chat',
  SETTING: 'Setting',
  FILE_MANAGER: 'FileManager',
  RAG_MANAGEMENT: 'RagManagement',
  MCP_MANAGEMENT: 'McpManagement',
  CONTEXT_VISUALIZATION: 'ContextVisualization'
};

// 激活内容类型常量
export const ACTIVE_CONTENT = {
  HOME: 'home',
  CHAT: 'chat',
  SETTINGS: 'settings',
  FILE_MANAGER: 'fileManager',
  RAG_MANAGEMENT: 'ragManagement',
  MCP_MANAGEMENT: 'mcpManagement',
  CONTEXT_VISUALIZATION: 'contextVisualization'
};

// 路由元数据常量
export const ROUTE_META = {
  HOME: { activeContent: ACTIVE_CONTENT.HOME },
  CHAT: { activeContent: ACTIVE_CONTENT.CHAT },
  SETTING: { activeContent: ACTIVE_CONTENT.SETTINGS },
  FILE: { activeContent: ACTIVE_CONTENT.FILE_MANAGER },
  RAG: { activeContent: ACTIVE_CONTENT.RAG_MANAGEMENT },
  MCP: { activeContent: ACTIVE_CONTENT.MCP_MANAGEMENT },
  CONTEXT: { activeContent: ACTIVE_CONTENT.CONTEXT_VISUALIZATION }
};

// 路由配置常量（用于生成路由数组）
export const ROUTE_CONFIGS = [
  {
    path: ROUTES.HOME,
    name: ROUTE_NAMES.HOME,
    meta: ROUTE_META.HOME
  },
  {
    path: ROUTES.CHAT,
    name: ROUTE_NAMES.CHAT,
    meta: ROUTE_META.CHAT,
    props: true
  },
  {
    path: ROUTES.SETTING,
    name: ROUTE_NAMES.SETTING,
    meta: ROUTE_META.SETTING
  },
  {
    path: ROUTES.FILE,
    name: ROUTE_NAMES.FILE_MANAGER,
    meta: ROUTE_META.FILE
  },
  {
    path: ROUTES.RAG,
    name: ROUTE_NAMES.RAG_MANAGEMENT,
    meta: ROUTE_META.RAG
  },
  {
    path: ROUTES.MCP,
    name: ROUTE_NAMES.MCP_MANAGEMENT,
    meta: ROUTE_META.MCP
  },
  {
    path: ROUTES.CONTEXT,
    name: ROUTE_NAMES.CONTEXT_VISUALIZATION,
    meta: ROUTE_META.CONTEXT
  }
];
