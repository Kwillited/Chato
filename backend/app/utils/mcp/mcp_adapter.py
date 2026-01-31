"""MCP 适配器工具类"""
from typing import Dict, List, Optional, Any
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
    
    async def initialize(self, mcp_config: Optional[Dict] = None) -> bool:
        """初始化 MCP 客户端"""
        logger.info("=== 开始初始化 MCP 适配器 ===")
        
        if not MCP_AVAILABLE:
            logger.error("MultiServerMCPClient 导入失败，MCP 功能不可用")
            return False
        
        # 默认 MCP 配置
        if mcp_config is None:
            logger.info("使用默认 MCP 配置")
            mcp_config = {
                "filesystem": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem"]
                },
                "weather": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["-y", "@h1deya/mcp-server-weather"]
                }
            }
        
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
        
        for i, tool in enumerate(self.tools):
            try:
                tool_name = getattr(tool, 'name', str(tool))
                tool_desc = getattr(tool, 'description', '')
                logger.info(f"工具 {i+1} 详细信息: 名称={tool_name}, 描述={tool_desc}")
                
                # 检测天气工具
                weather_keywords = ['weather', 'forecast', 'temp', 'climate', 'temperature']
                if any(keyword in tool_name.lower() for keyword in weather_keywords) or any(keyword in tool_desc.lower() for keyword in weather_keywords):
                    weather_tools.append(tool_name)
                    logger.info(f"识别为天气工具: {tool_name}")
                
                # 检测文件系统工具
                fs_keywords = ['file', 'fs', 'directory', 'read', 'list', 'folder', 'path', 'ls', 'dir']
                if any(keyword in tool_name.lower() for keyword in fs_keywords) or any(keyword in tool_desc.lower() for keyword in fs_keywords):
                    file_tools.append(tool_name)
                    logger.info(f"识别为文件系统工具: {tool_name}")
            except Exception as e:
                logger.error(f"解析工具 {i+1} 信息失败: {str(e)}")
                pass
        
        # 选择最合适的工具
        if weather_tools:
            forecast_tools = [t for t in weather_tools if 'forecast' in t.lower()]
            self.weather_tool_name = forecast_tools[0] if forecast_tools else weather_tools[0]
            logger.info(f"选择天气工具: {self.weather_tool_name}")
        
        if file_tools:
            list_tools = [t for t in file_tools if 'list' in t.lower() or 'dir' in t.lower() or 'ls' in t.lower()]
            if list_tools:
                self.filesystem_tool_name = list_tools[0]
                logger.info(f"选择文件系统工具（用于列出目录）: {self.filesystem_tool_name}")
            else:
                self.filesystem_tool_name = file_tools[0]
                logger.info(f"选择文件系统工具: {self.filesystem_tool_name}")
        
        logger.info(f"检测到的工具：天气工具={self.weather_tool_name}, 文件系统工具={self.filesystem_tool_name}")
    
    def get_tools(self) -> List[Any]:
        """获取 MCP 工具列表"""
        return self.tools
    
    def get_tool_usage_guide(self) -> str:
        """获取工具使用指导"""
        guide = ""
        
        if self.weather_tool_name:
            guide += f"""

当用户询问天气相关问题时，请使用天气工具：{self.weather_tool_name}
重要提示：
1. 确认用户提到的城市名称
2. 使用默认坐标：
   - 北京：latitude=39.9042, longitude=116.4074
   - 上海：latitude=31.2304, longitude=121.4737
   - 广州：latitude=23.1291, longitude=113.2644
   - 深圳：latitude=22.5431, longitude=114.0579
3. 工具执行后，用自然语言总结结果"""
        
        if self.filesystem_tool_name:
            guide += f"""

当用户需要文件操作时，请使用文件系统工具：{self.filesystem_tool_name}
重要提示：
1. 检测关键词：查看目录、列出文件、当前目录、文件夹内容等
2. 工具执行后，用自然语言总结结果"""
        else:
            guide += """

注意：当前环境中没有可用的文件系统工具，无法执行文件操作相关任务。"""
        
        # 简化的工具使用决策流程
        guide += f"""

工具使用流程：
1. 分析用户问题核心需求
2. 天气相关问题 → 使用天气工具
3. 文件操作需求 → 使用文件系统工具
4. 严格按规则选择工具，不要混淆使用场景
5. 工具执行后，必须总结结果给用户"""
        
        return guide
    
    def get_tool_info(self) -> Dict[str, Optional[str]]:
        """获取工具信息"""
        return {
            "weather_tool": self.weather_tool_name,
            "filesystem_tool": self.filesystem_tool_name
        }


# 创建全局 MCP 适配器实例
mcp_adapter = MCPAdapter()