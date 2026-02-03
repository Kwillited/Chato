"""MCP 适配器工具类"""
from typing import Dict, List, Optional, Any
import json
import os
from app.core.logging_config import logger


try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    MCP_AVAILABLE = True
except ImportError:
    MultiServerMCPClient = None
    MCP_AVAILABLE = False


class MCPAdapter:
    """MCP 适配器工具类"""
    
    def __init__(self):
        """初始化 MCP 适配器"""
        self.mcp_client = None
        self.tools = []
        self.weather_tool_name = None
        self.filesystem_tool_name = None
        logger.info("MCPAdapter 初始化完成")
    
    def is_available(self) -> bool:
        """检查 MCP 是否可用"""
        return MCP_AVAILABLE and self.mcp_client is not None
    
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
            "weather": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@h1deya/mcp-server-weather"]
            },
            "freesearch": {
                "transport": "stdio",
                "command": "npx",
                "args": ["freesearch-mcpserver@latest"]
            }
        }
    
    async def initialize(self, mcp_config: Optional[Dict] = None) -> bool:
        """初始化 MCP 客户端"""
        logger.info("=== 开始初始化 MCP 适配器 ===")
        
        if not MCP_AVAILABLE:
            logger.error("MultiServerMCPClient 导入失败，MCP 功能不可用")
            return False
        
        # 读取配置文件
        if mcp_config is None:
            # 计算配置文件路径: H:\ChaTo\backend\config\mcp_config.json
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'mcp_config.json')
            if os.path.exists(config_path):
                logger.info(f"从配置文件读取 MCP 配置: {config_path}")
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        mcp_config = json.load(f)
                except Exception as e:
                    logger.error(f"读取配置文件失败: {str(e)}")
                    # 使用默认配置作为 fallback
                    logger.info("使用默认 MCP 配置")
                    mcp_config = self._get_default_config()
            else:
                logger.info("配置文件不存在，使用默认 MCP 配置")
                mcp_config = self._get_default_config()
        
        try:
            # 初始化 MCP 客户端
            logger.info("正在初始化 MCP 客户端...")
            self.mcp_client = MultiServerMCPClient(mcp_config)
            logger.info("MCP 客户端初始化成功")
            
            # 获取工具
            logger.info("正在获取 MCP 工具...")
            self.tools = await self.mcp_client.get_tools()
            logger.info(f"成功获取 {len(self.tools)} 个 MCP 工具")
            
            # 检测工具
            self._detect_tools()
            
            return True
        except Exception as e:
            logger.error(f"初始化 MCP 客户端失败: {str(e)}")
            return False
    
    def _detect_tools(self):
        """检测可用工具"""
        logger.info("=== 开始检测 MCP 工具 ===")
        
        file_tools = []
        weather_tools = []
        all_tool_names = []
        
        for i, tool in enumerate(self.tools):
            try:
                tool_name = getattr(tool, 'name', str(tool))
                all_tool_names.append(tool_name)
                
                # 检测天气工具
                weather_keywords = ['weather', 'forecast', 'temp', 'climate', 'temperature']
                tool_desc = getattr(tool, 'description', '')
                if any(keyword in tool_name.lower() for keyword in weather_keywords) or any(keyword in tool_desc.lower() for keyword in weather_keywords):
                    weather_tools.append(tool_name)
                
                # 检测文件系统工具
                fs_keywords = ['file', 'fs', 'directory', 'read', 'list', 'folder', 'path', 'ls', 'dir']
                if any(keyword in tool_name.lower() for keyword in fs_keywords) or any(keyword in tool_desc.lower() for keyword in fs_keywords):
                    file_tools.append(tool_name)
            except Exception as e:
                logger.error(f"解析工具 {i+1} 信息失败: {str(e)}")
                pass
        
        # 输出简化的工具列表
        logger.info(f"检测到 {len(all_tool_names)} 个工具: {', '.join(all_tool_names)}")
        
        # 选择最合适的工具
        if weather_tools:
            forecast_tools = [t for t in weather_tools if 'forecast' in t.lower()]
            self.weather_tool_name = forecast_tools[0] if forecast_tools else weather_tools[0]
        
        if file_tools:
            list_tools = [t for t in file_tools if 'list' in t.lower() or 'dir' in t.lower() or 'ls' in t.lower()]
            if list_tools:
                self.filesystem_tool_name = list_tools[0]
            else:
                self.filesystem_tool_name = file_tools[0]
        
        logger.info(f"检测完成：天气工具={self.weather_tool_name}, 文件系统工具={self.filesystem_tool_name}")
    
    def get_tools(self) -> List[Any]:
        """获取 MCP 工具列表"""
        return self.tools
    
    def get_tool_info(self) -> Dict[str, Optional[str]]:
        """获取工具信息"""
        return {
            "weather_tool": self.weather_tool_name,
            "filesystem_tool": self.filesystem_tool_name
        }


# 创建全局 MCP 适配器实例
mcp_adapter = MCPAdapter()