"""MCP 客户端管理器 - 管理 MCP 客户端生命周期"""
from typing import Dict, List, Any
import json
from app.services.base_service import BaseService
from app.core.instance_manager import InstanceManager


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
        self._initialized = True
        self.log_info("MCP 客户端管理器初始化")
    
    def _generate_cache_key(self, mcp_config: Dict, server_name: str = None) -> str:
        """生成缓存键
        
        Args:
            mcp_config: MCP配置
            server_name: 服务器名称，如果提供则只包含该服务器的配置
            
        Returns:
            缓存键
        """
        if server_name and server_name in mcp_config:
            # 只包含指定服务器的配置
            single_server_config = {server_name: mcp_config[server_name]}
            return json.dumps(single_server_config, sort_keys=True)
        # 包含所有服务器的配置
        return json.dumps(mcp_config, sort_keys=True)
    
    def is_available(self, mcp_config: Dict = None) -> bool:
        """检查 MCP 是否可用"""
        if mcp_config:
            cache_key = self._generate_cache_key(mcp_config)
            # 检查 InstanceManager 中是否有对应的客户端实例
            return InstanceManager.get_cache_size('mcp').get('mcp', 0) > 0
        return InstanceManager.get_cache_size('mcp').get('mcp', 0) > 0
    
    def initialize_client(self, mcp_config: Dict) -> bool:
        """初始化 MCP 客户端配置（仅注册配置，不建立连接）
        
        Args:
            mcp_config: MCP 配置
            
        Returns:
            bool: 是否初始化成功
        """
        cache_key = self._generate_cache_key(mcp_config)
        
        self.log_info(f"开始初始化 MCP 客户端配置: {cache_key[:50]}...")
        
        try:
            # 使用统一实例管理器获取实例
            def create_client():
                # 动态导入 MCP 客户端
                from langchain_mcp_adapters.client import MultiServerMCPClient
                return MultiServerMCPClient(mcp_config)
            
            mcp_client = InstanceManager.get_instance('mcp', cache_key, create_client)
            self.log_info("MCP 客户端配置初始化成功（仅注册配置，未建立连接）")
            return True
        except Exception as e:
            self.log_error(f"初始化 MCP 客户端配置失败: {str(e)}")
            return False
    
    async def initialize(self, mcp_config: Dict) -> bool:
        """初始化 MCP 客户端
        
        Args:
            mcp_config: MCP 配置
            
        Returns:
            bool: 是否初始化成功
        """
        cache_key = self._generate_cache_key(mcp_config)
        tools_cache_key = f"TOOLS:ALL:{cache_key}"
        
        # 检查缓存中是否已有工具
        try:
            from app.core.instance_manager import InstanceManager as IM
            if tools_cache_key in IM._caches.get('mcp', {}):
                self.log_info("从缓存加载 MCP 工具")
                return True
        except Exception:
            pass
        
        # 先初始化客户端配置
        if not self.initialize_client(mcp_config):
            return False
        
        # 获取工具（这会触发实际连接）
        self.log_info("正在获取 MCP 工具...（首次调用将建立连接）")
        
        try:
            # 从统一实例管理器获取客户端
            def create_client():
                # 动态导入 MCP 客户端
                from langchain_mcp_adapters.client import MultiServerMCPClient
                return MultiServerMCPClient(mcp_config)
            
            mcp_client = InstanceManager.get_instance('mcp', cache_key, create_client)
            
            # 获取所有服务器的工具
            tools = await mcp_client.get_tools()
            self.log_info(f"成功获取 {len(tools)} 个 MCP 工具（已建立连接）")
            
            # 缓存工具
            InstanceManager.get_instance('mcp', tools_cache_key, lambda: tools)
            self.log_info("MCP 工具已缓存")
            return True
        except Exception as e:
            self.log_error(f"获取 MCP 工具失败: {str(e)}")
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
            tools_cache_key = f"TOOLS:ALL:{cache_key}"
            try:
                tools = InstanceManager.get_instance('mcp', tools_cache_key, lambda: [])
                return tools if tools != None else []
            except Exception:
                return []
        # 处理默认情况，这里简化处理
        return []
    
    async def get_tools_by_server(self, server_name: str, mcp_config: Dict = None) -> List[Any]:
        """根据服务器名称获取 MCP 工具列表
        
        Args:
            server_name: 服务器名称
            mcp_config: MCP 配置，如果为 None，则使用第一个客户端
            
        Returns:
            List[Any]: 工具列表
        """
        if mcp_config:
            # 为单个服务器生成独立的缓存键
            cache_key = self._generate_cache_key(mcp_config, server_name)
            # 工具缓存键使用更明显的前缀，避免与客户端实例混淆
            tools_cache_key = f"TOOLS:{server_name}:{cache_key}"
            
            # 检查缓存中是否已有该服务器的工具
            # 直接访问缓存，避免创建默认值
            try:
                from app.core.instance_manager import InstanceManager as IM
                if tools_cache_key in IM._caches.get('mcp', {}):
                    tools = IM._caches['mcp'][tools_cache_key]
                    self.log_info(f"从缓存加载 {server_name} 服务器的工具")
                    return tools
            except Exception:
                pass
            
            # 为单个服务器创建配置
            single_server_config = {server_name: mcp_config[server_name]}
            
            # 从统一实例管理器获取客户端（使用单个服务器配置）
            def create_client():
                from langchain_mcp_adapters.client import MultiServerMCPClient
                return MultiServerMCPClient(single_server_config)
            mcp_client = InstanceManager.get_instance('mcp', cache_key, create_client)
            
            # 获取指定服务器的工具（这会触发实际连接）
            self.log_info(f"正在获取 {server_name} 服务器的工具...（首次调用将建立连接）")
            tools = await mcp_client.get_tools(server_name=server_name)
            self.log_info(f"成功获取 {server_name} 服务器的 {len(tools)} 个工具（已建立连接）")
            
            # 缓存工具
            InstanceManager.get_instance('mcp', tools_cache_key, lambda: tools)
            self.log_info(f"{server_name} 服务器工具已缓存")
            return tools
        else:
            # 这里简化处理，实际应该从缓存中获取第一个客户端
            # 由于统一实例管理器的实现，这里需要根据具体情况调整
            return []
    
    def clear_cache(self):
        """清空 MCP 客户端缓存"""
        InstanceManager.clear_cache('mcp')
        self._tools_cache.clear()
        self.log_info("MCP 客户端缓存已清空")
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return InstanceManager.get_cache_size('mcp').get('mcp', 0)
