"""MCP工具相关业务逻辑服务"""
from typing import Dict, List, Optional, Any
import os
import json
from app.services.settings.setting_service import SettingService
from app.services.base_service import BaseService
from app.services.mcp.mcp_client_manager import MCPClientManager


class MCPService(BaseService):
    """MCP服务类，封装所有MCP相关的业务逻辑"""

    def __init__(self, setting_service: SettingService, mcp_client_manager=None):
        """初始化MCP服务
        
        Args:
            setting_service: 设置服务实例，用于依赖注入
            mcp_client_manager: MCP客户端管理器实例，用于依赖注入
        """
        self.setting_service = setting_service
        self.mcp_client_manager = mcp_client_manager or MCPClientManager()

    def _get_default_config(self) -> Dict:
        """获取默认 MCP 配置"""
        # 自动检测应用根目录
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        
        return {
            "filesystem": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", base_path]
            },
            "freesearch": {
                "transport": "stdio",
                "command": "npx",
                "args": ["freesearch-mcpserver@latest"]
            }
        }

    def get_default_config(self) -> Dict:
        """获取默认 MCP 配置
        
        Returns:
            Dict: 默认配置
        """
        return self._get_default_config()

    async def initialize_mcp(self, mcp_config: Optional[Dict] = None) -> bool:
        """初始化 MCP 服务
        
        Args:
            mcp_config: MCP 配置，如果为 None 则从配置文件读取
            
        Returns:
            bool: 是否初始化成功
        """
        if mcp_config is None:
            mcp_config = self.get_mcp_config()
        
        return await self.mcp_client_manager.initialize(mcp_config)

    def get_mcp_tools(self):
        """获取MCP工具列表"""
        tools = self.mcp_client_manager.get_tools()
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
    
    async def get_mcp_tools_by_server(self, server_name: str):
        """根据服务器名称获取MCP工具列表"""
        tools = await self.mcp_client_manager.get_tools_by_server(server_name)
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
        # 从配置文件中获取服务器列表
        
        try:
            config = self.get_mcp_config()
            
            servers = []
            for i, (server_name, server_config) in enumerate(config.items()):
                server_info = {
                    "id": i + 1,
                    "name": server_name,
                    "description": f"{server_name.capitalize()} MCP Server",
                    "type": server_name
                }
                servers.append(server_info)
            return servers
        except Exception as e:
            self.logger.error(f"获取MCP服务器列表失败: {e}")
            # 出错时使用默认配置
            default_config = self._get_default_config()
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
    
    def get_mcp_config(self):
        """获取MCP配置文件"""
        # 计算配置文件路径: H:\ChaTo\backend\config\mcp_config.json
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'mcp_config.json')
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config
            else:
                # 返回默认配置
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"获取MCP配置失败: {str(e)}")
            raise Exception(f"获取MCP配置失败: {str(e)}")
    
    def save_mcp_config(self, config):
        """保存MCP配置文件"""
        # 计算配置文件路径: H:\ChaTo\backend\config\mcp_config.json
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'mcp_config.json')
        
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            # 保存配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"MCP配置已保存到文件: {config_path}")
            
            return {
                'message': 'MCP配置已保存',
                'path': config_path
            }
        except Exception as e:
            self.logger.error(f"保存MCP配置失败: {str(e)}")
            raise Exception(f"保存MCP配置失败: {str(e)}")
