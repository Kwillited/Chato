"""系统设置相关API路由"""
from fastapi import APIRouter, Body, Depends

# 导入相关服务类
from app.services.settings.setting_service import SettingService
from app.utils.error_handler import handle_api_errors as handle_exception
from app.dependencies import get_setting_service
from app.models.schemas.pydantic_models import (
    SystemSettings, PatchSystemSettings, SettingResponse
)

# 创建设置API路由（前缀统一为 /api/settings）
router = APIRouter(prefix='/api/settings')

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
    # 直接传递所有字段，服务层会处理None值的过滤
    settings = setting_service.save_system_setting(data.model_dump())
    return SettingResponse(
        message='系统设置已保存',
        settings=settings
    )

