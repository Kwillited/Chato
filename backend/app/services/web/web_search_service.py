"""网络搜索服务 - 负责处理联网搜索相关操作"""
from app.services.base_service import BaseService


class WebSearchService(BaseService):
    """网络搜索服务类，封装所有联网搜索相关的操作"""
    
    def __init__(self):
        """初始化网络搜索服务"""
        super().__init__()
    
    async def perform_web_search(self, query, max_results=3):
        """执行网络搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            搜索结果
        """
        try:
            from app.core.service_container import service_container
            from app.services.mcp.mcp_service import MCPService
            # 获取 MCP 服务实例
            mcp_service = service_container.get_service('mcp_service')
            
            # 获取 MCP 配置
            mcp_config = mcp_service.get_mcp_config()
            
            # 直接获取 open-websearch 服务器的工具（不需要先初始化完整配置）
            tools = await mcp_service.mcp_client_manager.get_tools_by_server('open-websearch', mcp_config)
            
            # 查找搜索工具
            search_tool = None
            for tool in tools:
                try:
                    tool_name = getattr(tool, 'name', '').lower()
                    if 'search' in tool_name:
                        search_tool = tool
                        break
                except Exception:
                    pass
            
            if search_tool:
                # 执行搜索
                search_params = {
                    "query": query,
                    "max_results": max_results
                }
                # 调用搜索工具（使用异步调用）
                search_result = await search_tool.arun(search_params)
                return search_result
            return None
        except Exception as e:
            self.log_error(f"网络搜索失败: {str(e)}")
            return None
