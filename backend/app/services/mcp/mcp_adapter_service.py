"""MCP 适配器服务 - 管理 MCP 客户端生命周期"""
from typing import Dict, List, Optional, Any
from app.services.base_service import BaseService
from app.utils.mcp.mcp_adapter import MCPAdapter


class MCPAdapterService(BaseService):
    """MCP 适配器服务类"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(MCPAdapterService, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        """初始化 MCP 适配器服务"""
        if hasattr(self, '_initialized'):
            return
        
        super().__init__()
        self.mcp_adapter = MCPAdapter()
        self._initialized = False
        self.log_info("MCP 适配器服务初始化")
    
    async def initialize(self, mcp_config: Optional[Dict] = None) -> bool:
        """初始化 MCP 适配器
        
        Args:
            mcp_config: MCP 配置
            
        Returns:
            bool: 是否初始化成功
        """
        if self._initialized:
            self.log_info("MCP 适配器服务已初始化")
            return True
        
        self.log_info("开始初始化 MCP 适配器服务")
        result = await self.mcp_adapter.initialize(mcp_config)
        self._initialized = result
        
        if result:
            self.log_info("MCP 适配器服务初始化成功")
        else:
            self.log_error("MCP 适配器服务初始化失败")
        
        return result
    
    def get_tools(self) -> List[Any]:
        """获取 MCP 工具列表
        
        Returns:
            List[Any]: 工具列表
        """
        return self.mcp_adapter.get_tools()
    
    def get_tool_info(self) -> Dict[str, Optional[str]]:
        """获取工具信息
        
        Returns:
            Dict[str, Optional[str]]: 工具信息
        """
        return self.mcp_adapter.get_tool_info()
    
    def is_available(self) -> bool:
        """检查 MCP 是否可用
        
        Returns:
            bool: 是否可用
        """
        return self.mcp_adapter.is_available()
    
    def get_default_config(self) -> Dict:
        """获取默认 MCP 配置
        
        Returns:
            Dict: 默认配置
        """
        return self.mcp_adapter._get_default_config()
