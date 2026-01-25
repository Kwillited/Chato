"""MCP工具相关API路由"""
from fastapi import APIRouter, Body, Depends

# 导入设置服务类，直接使用SettingService处理MCP设置
from app.services.settings.setting_service import SettingService
from app.utils.decorators import handle_exception
from app.dependencies import get_setting_service
from app.models.pydantic_models import MCPSettings

# 创建MCP API路由（前缀统一为 /api/mcp）
router = APIRouter(prefix='/api/mcp')

# 获取MCP设置
@router.get('')
@handle_exception
def get_mcp_settings(setting_service: SettingService = Depends(get_setting_service)):
    return setting_service.get_mcp_settings()

# 保存MCP设置
@router.post('')
@handle_exception
def save_mcp_settings(mcp_settings: MCPSettings = Body(...), setting_service: SettingService = Depends(get_setting_service)):
    settings = setting_service.save_mcp_settings(mcp_settings.model_dump())
    return {
        'message': 'MCP设置已保存',
        'settings': settings
    }

