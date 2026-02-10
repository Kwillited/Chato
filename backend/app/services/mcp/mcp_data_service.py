"""MCP 数据服务 - 处理 MCP 相关的数据操作"""
from typing import Dict, List, Optional, Any
from app.services.base_service import BaseService
from app.repositories.mcp_repository import MCPRepository


class MCPDataService(BaseService):
    """MCP 数据服务类"""
    
    def __init__(self, mcp_repository: MCPRepository = None):
        """初始化 MCP 数据服务
        
        Args:
            mcp_repository: MCP 仓库实例，用于依赖注入
        """
        super().__init__()
        self.mcp_repo = mcp_repository or MCPRepository()
    
    def get_tools(self) -> List[Any]:
        """获取 MCP 工具列表
        
        Returns:
            List[Any]: 工具列表
        """
        try:
            tools = self.mcp_repo.get_all_tools()
            return [{
                'id': tool.id,
                'name': tool.name,
                'description': tool.description,
                'type': tool.type,
                'enabled': tool.enabled
            } for tool in tools]
        except Exception as e:
            self.logger.error(f"获取 MCP 工具列表失败: {e}")
            return []
    
    def get_servers(self) -> List[Dict[str, Any]]:
        """获取 MCP 服务器列表
        
        Returns:
            List[Dict[str, Any]]: 服务器列表
        """
        try:
            servers = self.mcp_repo.get_all_servers()
            return [{
                'id': server.id,
                'name': server.name,
                'description': server.description,
                'type': server.type,
                'enabled': server.enabled
            } for server in servers]
        except Exception as e:
            self.logger.error(f"获取 MCP 服务器列表失败: {e}")
            return []
