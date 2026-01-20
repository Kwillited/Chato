"""MCP工具相关API路由"""
from fastapi import APIRouter, Body, Depends

# 导入MCP服务类
from app.services.mcp.mcp_service import MCPService
from app.utils.decorators import handle_exception
from app.dependencies import get_mcp_service
from app.models.pydantic_models import MCPSettings

# 创建MCP API路由（前缀统一为 /api/mcp）
router = APIRouter(prefix='/api/mcp')

# 获取MCP设置
@router.get('')
@handle_exception
def get_mcp_settings(mcp_service: MCPService = Depends(get_mcp_service)):
    return mcp_service.get_mcp_settings()

# 保存MCP设置
@router.post('')
@handle_exception
def save_mcp_settings(mcp_settings: MCPSettings = Body(...), mcp_service: MCPService = Depends(get_mcp_service)):
    settings = mcp_service.save_mcp_settings(mcp_settings.model_dump())
    return {
        'message': 'MCP设置已保存',
        'settings': settings
    }

