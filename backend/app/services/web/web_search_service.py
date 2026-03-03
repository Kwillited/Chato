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
            from app.utils.mcp.mcp_adapter import mcp_adapter
            # 初始化MCP适配器
            await mcp_adapter.initialize()
            if mcp_adapter.is_available():
                # 获取工具列表
                tools = mcp_adapter.get_tools()
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
