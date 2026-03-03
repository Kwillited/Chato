"""MCP工具相关API路由"""
from fastapi import APIRouter, Depends, Body
from typing import List, Dict, Any
from app.services.mcp.mcp_service import MCPService
from app.dependencies import get_mcp_service
from app.utils.error_handler import handle_api_errors

# 创建MCP API路由（前缀统一为 /api/mcp）
router = APIRouter(prefix='/api/mcp')

# 获取MCP工具列表
@router.get('/tools', response_model=List[Dict[str, Any]])
@handle_api_errors()
def get_mcp_tools(mcp_service: MCPService = Depends(get_mcp_service)):
    """获取MCP工具列表"""
    return mcp_service.get_mcp_tools()

# 获取MCP服务器列表
@router.get('/servers', response_model=List[Dict[str, Any]])
@handle_api_errors()
def get_mcp_servers(mcp_service: MCPService = Depends(get_mcp_service)):
    """获取MCP服务器列表"""
    return mcp_service.get_mcp_servers()

# 获取MCP配置文件
@router.get('/config', response_model=Dict[str, Any])
@handle_api_errors()
def get_mcp_config(mcp_service: MCPService = Depends(get_mcp_service)):
    """获取MCP配置文件"""
    return mcp_service.get_mcp_config()

# 保存MCP配置文件
@router.post('/config', response_model=Dict[str, str])
@handle_api_errors()
def save_mcp_config(config: dict = Body(...), mcp_service: MCPService = Depends(get_mcp_service)):
    """保存MCP配置文件"""
    return mcp_service.save_mcp_config(config)
