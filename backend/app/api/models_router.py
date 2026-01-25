"""模型相关API路由"""
from fastapi import APIRouter, Body, Path, HTTPException, Response, Depends
from fastapi.responses import FileResponse
import os

# 导入模型服务层
from app.services.model.model_service import ModelService
from app.utils.decorators import handle_exception
from app.dependencies import get_model_service
from app.models.pydantic_models import BaseResponse

# 创建模型API路由（前缀统一为 /api/models）
router = APIRouter(prefix='/api/models')




# 获取所有模型供应商以及模型版本
@router.get('', response_model=BaseResponse[dict])
@handle_exception
def get_models(model_service: ModelService = Depends(get_model_service)):
    models = model_service.get_all_models()
    return BaseResponse(
        data={'models': models},
        message="模型列表获取成功"
    )

# 获取模型供应商图标
@router.get('/icons/{filename}')
@handle_exception
def get_model_icon(filename: str = Path(...), model_service: ModelService = Depends(get_model_service)):
    """
    提供模型供应商图标文件下载功能
    参数: filename - 图标文件名，如 'OpenAI.png'
    """
    success, icon_data, message = model_service.get_model_icon(filename)
    
    if success and icon_data:
        return Response(content=icon_data, media_type='image/png')
    else:
        raise HTTPException(status_code=404, detail=message)

# 配置特定模型（按名称）
@router.post('/{model_name}', response_model=BaseResponse[dict])
@handle_exception
def configure_model(model_name: str = Path(...), data: dict = Body(...), model_service: ModelService = Depends(get_model_service)):
    success, message, model = model_service.configure_model(model_name, data)
    
    if not success:
        # 根据错误类型返回不同的状态码
        if message == '模型不存在':
            raise HTTPException(status_code=404, detail=message)
        else:
            # 其他错误返回500状态码
            raise HTTPException(status_code=500, detail=message)
    
    return BaseResponse(
        data={'model': model},
        message=message
    )

# 删除特定模型配置（按名称）
@router.delete('/{model_name}', response_model=BaseResponse)
@handle_exception
def delete_model(model_name: str = Path(...), model_service: ModelService = Depends(get_model_service)):
    success, message = model_service.delete_model(model_name)
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return BaseResponse(
        message=message
    )

# 更新模型启用状态
@router.post('/{model_name}/enabled', response_model=BaseResponse[dict])
@handle_exception
def update_model_enabled(model_name: str = Path(...), data: dict = Body(...), model_service: ModelService = Depends(get_model_service)):
    enabled = data.get('enabled', True)
    success, message = model_service.update_model_enabled(model_name, enabled)
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return BaseResponse(
        data={'enabled': enabled},
        message=message
    )

# 删除特定模型的特定版本
@router.delete('/{model_name}/versions/{version_name}', response_model=BaseResponse[dict])
@handle_exception
def delete_version(model_name: str = Path(...), version_name: str = Path(...), model_service: ModelService = Depends(get_model_service)):
    success, message, model = model_service.delete_version(model_name, version_name)
    
    if not success:
        if message == '模型不存在':
            raise HTTPException(status_code=404, detail=message)
        elif message == '该模型没有版本信息' or message == '版本不存在':
            raise HTTPException(status_code=400, detail=message)
        else:
            raise HTTPException(status_code=400, detail=message)
    
    return BaseResponse(
        data={'model': model},
        message=message
    )


