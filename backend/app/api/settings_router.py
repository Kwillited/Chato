"""系统设置相关API路由"""
from fastapi import APIRouter, Body, Depends

# 导入相关服务类
from app.services.settings.setting_service import SettingService
from app.utils.error_handler import handle_api_errors as handle_exception
from app.dependencies import get_setting_service
from app.models.schemas.pydantic_models import (
    BasicSettings, SystemSettings, PatchSystemSettings, SettingResponse
)

# 创建设置API路由（前缀统一为 /api/settings）
router = APIRouter(prefix='/api/settings')

# 获取基本设置
@router.get('/basic', response_model=BasicSettings)
@handle_exception()
def get_basic_settings(setting_service: SettingService = Depends(get_setting_service)):
    """获取基本设置"""
    return setting_service.get_basic_settings()

# 保存基本设置
@router.post('/basic', response_model=SettingResponse)
@handle_exception()
def save_basic_settings(data: BasicSettings = Body(...), setting_service: SettingService = Depends(get_setting_service)):
    """保存基本设置"""
    settings = setting_service.save_basic_settings(data.dict())
    return SettingResponse(
        message='基本设置已保存',
        settings=settings
    )

# 获取系统设置
@router.get('/system', response_model=SystemSettings)
@handle_exception()
def get_system_settings(setting_service: SettingService = Depends(get_setting_service)):
    """获取系统设置"""
    return setting_service.get_system_setting()

# 保存系统设置
@router.patch('/system', response_model=SettingResponse)
@handle_exception()
def save_system_settings(data: PatchSystemSettings = Body(...), setting_service: SettingService = Depends(get_setting_service)):
    """保存系统设置"""
    # 只包含请求体中提供的非None字段
    settings_data = {k: v for k, v in data.model_dump().items() if v is not None}
    settings = setting_service.save_system_setting(settings_data)
    return SettingResponse(
        message='系统设置已保存',
        settings=settings
    )

