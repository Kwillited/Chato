"""系统设置相关API路由"""
from fastapi import APIRouter, Body, Depends

# 导入相关服务类
from app.services.settings.setting_service import SettingService
from app.utils.decorators import handle_exception
from app.dependencies import get_setting_service
from app.models.pydantic_models import (
    NotificationSettings, MCPSettings, BasicSettings, SystemSettings, SettingResponse
)

# 创建设置API路由（前缀统一为 /api/settings）
router = APIRouter(prefix='/api/settings')

# 获取通知设置
@router.get('/notification', response_model=NotificationSettings)
@handle_exception
def get_notification_settings(setting_service: SettingService = Depends(get_setting_service)):
    """获取通知设置"""
    return setting_service.get_notification_settings()

# 保存通知设置
@router.post('/notification', response_model=SettingResponse)
@handle_exception
def save_notification_settings(data: NotificationSettings = Body(...), setting_service: SettingService = Depends(get_setting_service)):
    """保存通知设置"""
    settings = setting_service.save_notification_settings(data.dict())
    return SettingResponse(
        message='通知设置已保存',
        settings=settings
    )

# 获取MCP设置
@router.get('/mcp', response_model=MCPSettings)
@handle_exception
def get_mcp_settings(setting_service: SettingService = Depends(get_setting_service)):
    """获取MCP设置"""
    return setting_service.get_mcp_settings()

# 保存MCP设置
@router.post('/mcp', response_model=SettingResponse)
@handle_exception
def save_mcp_settings(data: MCPSettings = Body(...), setting_service: SettingService = Depends(get_setting_service)):
    """保存MCP设置"""
    settings = setting_service.save_mcp_settings(data.dict())
    return SettingResponse(
        message='MCP设置已保存',
        settings=settings
    )

# 获取基本设置
@router.get('/basic', response_model=BasicSettings)
@handle_exception
def get_basic_settings(setting_service: SettingService = Depends(get_setting_service)):
    """获取基本设置"""
    return setting_service.get_basic_settings()

# 保存基本设置
@router.post('/basic', response_model=SettingResponse)
@handle_exception
def save_basic_settings(data: BasicSettings = Body(...), setting_service: SettingService = Depends(get_setting_service)):
    """保存基本设置"""
    settings = setting_service.save_basic_settings(data.dict())
    return SettingResponse(
        message='基本设置已保存',
        settings=settings
    )

# 获取系统设置
@router.get('/system', response_model=SystemSettings)
@handle_exception
def get_system_settings(setting_service: SettingService = Depends(get_setting_service)):
    """获取系统设置"""
    return setting_service.get_system_setting()

# 保存系统设置
@router.post('/system', response_model=SettingResponse)
@handle_exception
def save_system_settings(data: SystemSettings = Body(...), setting_service: SettingService = Depends(get_setting_service)):
    """保存系统设置"""
    settings = setting_service.save_system_setting(data.dict())
    return SettingResponse(
        message='系统设置已保存',
        settings=settings
    )

