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
        self.weather_tool_name = None
        self.filesystem_tool_name = None
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
            
            # 检测工具
            self._detect_tools()
            
            self._initialized = True
            self.log_info("MCP 客户端管理器初始化成功")
            return True
        except Exception as e:
            self.log_error(f"初始化 MCP 客户端失败: {str(e)}")
            self.log_error("MCP 客户端管理器初始化失败")
            return False
    
    def _detect_tools(self):
        """检测可用工具"""
        self.log_info("=== 开始检测 MCP 工具 ===")
        
        all_tool_names = []
        
        for i, tool in enumerate(self.tools):
            try:
                tool_name = getattr(tool, 'name', str(tool))
                all_tool_names.append(tool_name)
            except Exception as e:
                self.log_error(f"解析工具 {i+1} 信息失败: {str(e)}")
                pass
        
        # 输出工具列表
        self.log_info(f"检测到 {len(all_tool_names)} 个工具: {', '.join(all_tool_names)}")
        self.log_info("=== 工具检测完成 ===")
    
    def get_tools(self) -> List[Any]:
        """获取 MCP 工具列表
        
        Returns:
            List[Any]: 工具列表
        """
        return self.tools
    
    def get_tool_info(self) -> Dict[str, Optional[str]]:
        """获取工具信息
        
        Returns:
            Dict[str, Optional[str]]: 工具信息
        """
        return {
            "weather_tool": self.weather_tool_name,
            "filesystem_tool": self.filesystem_tool_name
        }
