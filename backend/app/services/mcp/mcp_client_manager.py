"""MCP 客户端管理器 - 管理 MCP 客户端生命周期"""
from typing import Dict, List, Optional, Any
from app.services.base_service import BaseService
from langchain_mcp_adapters.client import MultiServerMCPClient


class MCPClientManager(BaseService):
    """MCP 客户端管理器类 - 负责 MCP 客户端的生命周期管理"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(MCPClientManager, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        """初始化 MCP 客户端管理器"""
        if hasattr(self, '_initialized'):
            return
        
        super().__init__()
        self.mcp_client = None
        self.tools = []
        self._initialized = False
        self.log_info("MCP 客户端管理器初始化")
    
    def is_available(self) -> bool:
        """检查 MCP 是否可用"""
        return self.mcp_client is not None
    
    async def initialize(self, mcp_config: Dict) -> bool:
        """初始化 MCP 客户端
        
        Args:
            mcp_config: MCP 配置
            
        Returns:
            bool: 是否初始化成功
        """
        if self._initialized:
            self.log_info("MCP 客户端管理器已初始化")
            return True
        
        self.log_info("开始初始化 MCP 客户端管理器")
        
        try:
            # 初始化 MCP 客户端
            self.log_info("正在初始化 MCP 客户端...")
            self.mcp_client = MultiServerMCPClient(mcp_config)
            self.log_info("MCP 客户端初始化成功")
            
            # 获取工具
            self.log_info("正在获取 MCP 工具...")
            self.tools = await self.mcp_client.get_tools()
            self.log_info(f"成功获取 {len(self.tools)} 个 MCP 工具")
            
            self._initialized = True
            self.log_info("MCP 客户端管理器初始化成功")
            return True
        except Exception as e:
            self.log_error(f"初始化 MCP 客户端失败: {str(e)}")
            self.log_error("MCP 客户端管理器初始化失败")
            return False
    
    def get_tools(self) -> List[Any]:
        """获取 MCP 工具列表
        
        Returns:
            List[Any]: 工具列表
        """
        return self.tools
    
    async def get_tools_by_server(self, server_name: str) -> List[Any]:
        """根据服务器名称获取 MCP 工具列表
        
        Args:
            server_name: 服务器名称
            
        Returns:
            List[Any]: 工具列表
        """
        if not self.mcp_client:
            return []
        return await self.mcp_client.get_tools(server_name=server_name)
