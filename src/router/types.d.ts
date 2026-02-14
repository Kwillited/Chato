// 路由路径类型
export interface RoutePaths {
  HOME: string;
  CHAT: string;
  SETTING: string;
  FILE: string;
  RAG: string;
  MCP: string;
  CONTEXT: string;
}

// 路由名称类型
export interface RouteNames {
  HOME: string;
  CHAT: string;
  SETTING: string;
  FILE_MANAGER: string;
  RAG_MANAGEMENT: string;
  MCP_MANAGEMENT: string;
  CONTEXT_VISUALIZATION: string;
}

// 激活内容类型
export interface ActiveContentTypes {
  HOME: string;
  CHAT: string;
  SETTINGS: string;
  FILE_MANAGER: string;
  RAG_MANAGEMENT: string;
  MCP_MANAGEMENT: string;
  CONTEXT_VISUALIZATION: string;
}

// 路由元数据类型
export interface RouteMeta {
  activeContent: string;
}

// 路由配置类型
export interface RouteConfig {
  path: string;
  name: string;
  component?: any;
  meta: RouteMeta;
  props?: boolean;
}

// 路由元数据配置类型
export interface RouteMetaConfig {
  HOME: RouteMeta;
  CHAT: RouteMeta;
  SETTING: RouteMeta;
  FILE: RouteMeta;
  RAG: RouteMeta;
  MCP: RouteMeta;
  CONTEXT: RouteMeta;
}

// 路由配置数组类型
export type RouteConfigArray = RouteConfig[];

// 导航方法类型
export interface NavigationMethods {
  navigateToHome: () => void;
  navigateToChat: (chatId: string) => void;
  navigateToSettings: () => void;
  navigateToFileManager: () => void;
  navigateToRagManagement: () => void;
  navigateToMcpManagement: () => void;
  navigateToContextVisualization: () => void;
  createAndNavigateToNewChat: (model?: string) => Promise<any>;
  handleRouteChange: (newRoute: any, router: any) => Promise<void>;
  handleStateDrivenRouting: (newChatId: string | null, currentPath: string, router: any) => void;
}
