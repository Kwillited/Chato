"""MCP 数据服务 - 管理 MCP 相关的内存数据"""
from typing import Dict, List, Optional, Any
from app.services.base_service import BaseService


class MCPDataService(BaseService):
    """MCP 数据服务类"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(MCPDataService, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        """初始化 MCP 数据服务"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        super().__init__()
        # 存储 MCP 工具信息
        self._tools_cache: List[Any] = []
        # 存储 MCP 服务器信息
        self._servers_cache: List[Dict[str, Any]] = []
        # 存储 MCP 配置
        self._config_cache: Optional[Dict[str, Any]] = None
        # 脏标记
        self._dirty = False
        
        self._initialized = True
        self.log_info("MCP 数据服务初始化")
    
    def set_tools(self, tools: List[Any]) -> None:
        """设置 MCP 工具列表
        
        Args:
            tools: 工具列表
        """
        self._tools_cache = tools
        self._dirty = True
        self.log_debug(f"更新 MCP 工具缓存: {len(tools)} 个工具")
    
    def get_tools(self) -> List[Any]:
        """获取 MCP 工具列表
        
        Returns:
            List[Any]: 工具列表
        """
        return self._tools_cache
    
    def set_servers(self, servers: List[Dict[str, Any]]) -> None:
        """设置 MCP 服务器列表
        
        Args:
            servers: 服务器列表
        """
        self._servers_cache = servers
        self._dirty = True
        self.log_debug(f"更新 MCP 服务器缓存: {len(servers)} 个服务器")
    
    def get_servers(self) -> List[Dict[str, Any]]:
        """获取 MCP 服务器列表
        
        Returns:
            List[Dict[str, Any]]: 服务器列表
        """
        return self._servers_cache
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """设置 MCP 配置
        
        Args:
            config: MCP 配置
        """
        self._config_cache = config
        self._dirty = True
        self.log_debug("更新 MCP 配置缓存")
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """获取 MCP 配置
        
        Returns:
            Optional[Dict[str, Any]]: MCP 配置
        """
        return self._config_cache
    
    def is_dirty(self) -> bool:
        """检查是否有脏数据
        
        Returns:
            bool: 是否有脏数据
        """
        return self._dirty
    
    def clear_dirty(self) -> None:
        """清除脏标记"""
        self._dirty = False
        self.log_debug("清除 MCP 数据服务脏标记")
    
    def clear_cache(self) -> None:
        """清除所有缓存"""
        self._tools_cache = []
        self._servers_cache = []
        self._config_cache = None
        self._dirty = False
        self.log_info("清除 MCP 数据服务缓存")
