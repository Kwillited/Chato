"""MCP 客户端管理器 - 管理 MCP 客户端生命周期"""
from typing import Dict, List, Optional, Any
import json
from app.services.base_service import BaseService
from app.core.instance_manager import InstanceManager


class MCPClientManager(BaseService):
    """MCP 客户端管理器类 - 负责 MCP 客户端的生命周期管理"""
    
    _instance = None
    _tools_cache = {}  # 缓存不同配置的工具列表
    
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
        self._initialized = True
        self.log_info("MCP 客户端管理器初始化")
    
    def _generate_cache_key(self, mcp_config: Dict) -> str:
        """生成缓存键"""
        return json.dumps(mcp_config, sort_keys=True)
    
    def is_available(self, mcp_config: Dict = None) -> bool:
        """检查 MCP 是否可用"""
        if mcp_config:
            cache_key = self._generate_cache_key(mcp_config)
            return InstanceManager.get_cache_size('mcp').get('mcp', 0) > 0 and cache_key in self._tools_cache
        return InstanceManager.get_cache_size('mcp').get('mcp', 0) > 0
    
    async def initialize(self, mcp_config: Dict) -> bool:
        """初始化 MCP 客户端
        
        Args:
            mcp_config: MCP 配置
            
        Returns:
            bool: 是否初始化成功
        """
        cache_key = self._generate_cache_key(mcp_config)
        
        # 检查缓存中是否已有对应配置的客户端
        if cache_key in self._tools_cache:
            self.log_info(f"MCP 客户端已存在于缓存中: {cache_key[:50]}...")
            return True
        
        self.log_info(f"开始初始化 MCP 客户端: {cache_key[:50]}...")
        
        try:
            # 使用统一实例管理器获取实例
            def create_client():
                # 动态导入 MCP 客户端
                from langchain_mcp_adapters.client import MultiServerMCPClient
                return MultiServerMCPClient(mcp_config)
            
            mcp_client = InstanceManager.get_instance('mcp', cache_key, create_client)
            self.log_info("MCP 客户端初始化成功")
            
            # 获取工具
            self.log_info("正在获取 MCP 工具...")
            tools = await mcp_client.get_tools()
            self.log_info(f"成功获取 {len(tools)} 个 MCP 工具")
            
            # 缓存工具
            self._tools_cache[cache_key] = tools
            
            self.log_info(f"MCP 客户端已缓存: {cache_key[:50]}...")
            return True
        except Exception as e:
            self.log_error(f"初始化 MCP 客户端失败: {str(e)}")
            return False
    
    def get_tools(self, mcp_config: Dict = None) -> List[Any]:
        """获取 MCP 工具列表
        
        Args:
            mcp_config: MCP 配置，如果为 None，则返回第一个客户端的工具
            
        Returns:
            List[Any]: 工具列表
        """
        if mcp_config:
            cache_key = self._generate_cache_key(mcp_config)
            return self._tools_cache.get(cache_key, [])
        return next(iter(self._tools_cache.values()), [])
    
    async def get_tools_by_server(self, server_name: str, mcp_config: Dict = None) -> List[Any]:
        """根据服务器名称获取 MCP 工具列表
        
        Args:
            server_name: 服务器名称
            mcp_config: MCP 配置，如果为 None，则使用第一个客户端
            
        Returns:
            List[Any]: 工具列表
        """
        if mcp_config:
            cache_key = self._generate_cache_key(mcp_config)
            # 从统一实例管理器获取客户端
            def create_client():
                from langchain_mcp_adapters.client import MultiServerMCPClient
                return MultiServerMCPClient(mcp_config)
            mcp_client = InstanceManager.get_instance('mcp', cache_key, create_client)
        else:
            # 这里简化处理，实际应该从缓存中获取第一个客户端
            # 由于统一实例管理器的实现，这里需要根据具体情况调整
            return []
        
        if not mcp_client:
            return []
        return await mcp_client.get_tools(server_name=server_name)
    
    def clear_cache(self):
        """清空 MCP 客户端缓存"""
        InstanceManager.clear_cache('mcp')
        self._tools_cache.clear()
        self.log_info("MCP 客户端缓存已清空")
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return InstanceManager.get_cache_size('mcp').get('mcp', 0)
