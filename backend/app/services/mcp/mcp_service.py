"""MCP工具相关业务逻辑服务"""
from app.services.settings.setting_service import SettingService
from app.services.base_service import BaseService
from app.utils.logging_utils import LoggingUtils
from app.utils.mcp.mcp_adapter import mcp_adapter


class MCPService(BaseService):
    """MCP服务类，封装所有MCP相关的业务逻辑"""

    def __init__(self, setting_service=None):
        """初始化MCP服务
        
        Args:
            setting_service: 设置服务实例，用于依赖注入
        """
        self.setting_service = setting_service or SettingService()

    def get_mcp_settings(self):
        """获取MCP设置"""
        return self.setting_service.get_mcp_settings()

    def save_mcp_settings(self, data):
        """保存MCP设置"""
        return self.setting_service.save_mcp_settings(data)

    def get_notification_settings(self):
        """获取通知设置"""
        return self.setting_service.get_notification_settings()

    def save_notification_settings(self, data):
        """保存通知设置"""
        return self.setting_service.save_notification_settings(data)

    def get_mcp_tools(self):
        """获取MCP工具列表"""
        tools = mcp_adapter.get_tools()
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