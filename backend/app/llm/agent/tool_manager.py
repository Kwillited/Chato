import json
from typing import Dict, Any, List, Optional
from langchain_core.messages import ToolMessage
from app.core.logger import logger
from app.core.service_container import service_container


class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        """初始化工具管理器"""
        self.tools_map = {}
    
    async def initialize(self, mcp_config: Optional[Dict] = None):
        """
        初始化工具管理器
        
        Args:
            mcp_config: MCP 配置
        """
        if self.tools_map:
            return
        
        # 通过服务容器获取 MCPService 实例
        mcp_service = service_container.get_service('mcp_service')
        # 只初始化客户端配置，不获取工具
        mcp_service.initialize_mcp_client(mcp_config)
        # 工具将在实际需要时获取
        self.tools_map = {}
    
    def get_tools(self) -> List[Any]:
        """
        获取工具列表
        
        Returns:
            List[Any]: 工具列表
        """
        if not self.tools_map:
            # 首次调用时获取工具
            try:
                mcp_service = service_container.get_service('mcp_service')
                # 只初始化 MCP 客户端配置（不建立连接）
                mcp_service.initialize_mcp_client()
                # 工具将在实际需要时通过 get_tools_by_server 获取
            except Exception as e:
                logger.error(f"初始化 MCP 失败: {e}")
        return list(self.tools_map.values())
    
    def get_tool_by_name(self, tool_name: str) -> Optional[Any]:
        """
        根据名称获取工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具实例，如果不存在则返回 None
        """
        return self.tools_map.get(tool_name)
    
    async def run_tool(self, tool_call: Dict[str, Any], tool_index: int = 0) -> ToolMessage:
        """
        运行单个工具
        
        Args:
            tool_call: 工具调用信息
            tool_index: 工具索引
        
        Returns:
            工具执行结果消息
        """
        t_name, t_args, t_id = tool_call['name'], tool_call['args'], tool_call['id']
        
        try:
            if t_name in self.tools_map:
                result = await self.tools_map[t_name].ainvoke(t_args)
                res_str = self._format_tool_result(result)
            else:
                res_str = f"错误: 未找到工具 {t_name}"
        except Exception as e:
            logger.error(f"工具执行失败: {t_name}, 错误: {str(e)}")
            res_str = f"执行出错: {str(e)}"
        
        tool_message = ToolMessage(content=res_str, tool_call_id=t_id)
        # 为 ToolMessage 添加工具索引
        tool_message.tool_index = tool_index
        return tool_message
    
    def _format_tool_result(self, result: Any) -> str:
        """
        格式化工具执行结果
        
        Args:
            result: 工具执行结果
        
        Returns:
            格式化后的结果字符串
        """
        if isinstance(result, str):
            return result
        try:
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"结果格式化失败: {str(e)}")
            return str(result)
    
    def clear_cache(self):
        """清空工具缓存"""
        self.tools_map = {}
