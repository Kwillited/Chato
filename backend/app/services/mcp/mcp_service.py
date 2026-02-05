"""MCP工具相关业务逻辑服务"""
from app.services.settings.setting_service import SettingService
from app.services.base_service import BaseService
from app.services.mcp.mcp_adapter_service import MCPAdapterService


class MCPService(BaseService):
    """MCP服务类，封装所有MCP相关的业务逻辑"""

    def __init__(self, setting_service=None, mcp_adapter_service=None):
        """初始化MCP服务
        
        Args:
            setting_service: 设置服务实例，用于依赖注入
            mcp_adapter_service: MCP适配器服务实例，用于依赖注入
        """
        self.setting_service = setting_service or SettingService()
        self.mcp_adapter_service = mcp_adapter_service or MCPAdapterService()

    def get_mcp_tools(self):
        """获取MCP工具列表"""
        tools = self.mcp_adapter_service.get_tools()
        # 转换工具格式，提取必要的信息
        tool_list = []
        for i, tool in enumerate(tools):
            try:
                tool_info = {
                    "id": i + 1,
                    "name": getattr(tool, 'name', f"Tool {i + 1}"),
                    "description": getattr(tool, 'description', "No description available"),
                    "type": "custom"
                }
                tool_list.append(tool_info)
            except Exception as e:
                self.logger.error(f"解析工具信息失败: {e}")
        return tool_list

    def get_mcp_servers(self):
        """获取MCP服务器列表"""
        # 从MCP配置中获取服务器列表
        # 获取默认配置中的服务器
        default_config = self.mcp_adapter_service.get_default_config()
        servers = []
        for i, (server_name, server_config) in enumerate(default_config.items()):
            server_info = {
                "id": i + 1,
                "name": server_name,
                "description": f"{server_name.capitalize()} MCP Server",
                "type": server_name
            }
            servers.append(server_info)
        return servers