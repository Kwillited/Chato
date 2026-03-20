"""模型相关API路由"""
from fastapi import APIRouter, Body, Path, HTTPException, Response, Depends

# 导入模型服务层
from app.services.model.model_service import ModelService
from app.utils.error_handler import handle_api_errors as handle_exception
from app.dependencies import get_model_service

# 创建模型API路由（前缀统一为 /api/models）
router = APIRouter(prefix='/api/models')

# 获取所有模型供应商以及模型版本
@router.get('')
@handle_exception()
def get_models(model_service: ModelService = Depends(get_model_service)):
    models = model_service.get_all_models()
    return {'models': models}

# 获取模型供应商图标
@router.get('/icons/{filename}')
@handle_exception()
def get_model_icon(filename: str = Path(...), model_service: ModelService = Depends(get_model_service)):
    """
    提供模型供应商图标文件下载功能
    参数: filename - 图标文件名，如 'OpenAI.png'
    """
    success, icon_data, message = model_service.get_model_icon(filename)
    
    if success and icon_data:
        # 根据文件扩展名设置正确的媒体类型
        if filename.lower().endswith('.svg'):
            media_type = 'image/svg+xml'
        else:
            media_type = 'image/png'
        # 设置缓存头，缓存时间为1周
        response = Response(content=icon_data, media_type=media_type)
        response.headers["Cache-Control"] = "public, max-age=604800"  # 7 days
        response.headers["ETag"] = f"{hash(icon_data)}"
        response.headers["Last-Modified"] = "Mon, 01 Jan 2024 00:00:00 GMT"  # 固定的修改时间
        return response
    else:
        raise HTTPException(status_code=404, detail=message)

# 配置特定模型（按名称）
@router.post('/{model_name}')
@handle_exception()
def configure_model(model_name: str = Path(...), data: dict = Body(...), model_service: ModelService = Depends(get_model_service)):
    success, message, model = model_service.configure_model(model_name, data)
    
    if not success:
        # 根据错误类型返回不同的状态码
        if message == '模型不存在':
            raise HTTPException(status_code=404, detail=message)
        else:
            # 其他错误返回500状态码
            raise HTTPException(status_code=500, detail=message)
    
    return {
        'message': message,
        'model': model
    }

# 删除特定模型配置（按名称）
@router.delete('/{model_name}')
@handle_exception()
def delete_model(model_name: str = Path(...), model_service: ModelService = Depends(get_model_service)):
    success, message = model_service.delete_model(model_name)
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return {'message': message}

# 更新模型所有版本的启用状态
@router.patch('/{model_name}/enabled')
@handle_exception()
def update_model_enabled(model_name: str = Path(...), data: dict = Body(...), model_service: ModelService = Depends(get_model_service)):
    enabled = data.get('enabled', True)
    success, message = model_service.update_model_versions_enabled(model_name, enabled)
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return {
        'message': message,
        'enabled': enabled
    }

# 删除特定模型的特定版本
@router.delete('/{model_name}/versions/{version_name}')
@handle_exception()
def delete_version(model_name: str = Path(...), version_name: str = Path(...), model_service: ModelService = Depends(get_model_service)):
    success, message, model = model_service.delete_version(model_name, version_name)
    
    if not success:
        if message == '模型不存在':
            raise HTTPException(status_code=404, detail=message)
        elif message == '该模型没有版本信息' or message == '版本不存在':
            raise HTTPException(status_code=400, detail=message)
        else:
            raise HTTPException(status_code=400, detail=message)
    
    return {
        'message': message,
        'model': model
    }

# 设置默认模型版本
@router.patch('/{model_name}/versions/{version_name}/default')
@handle_exception()
def set_default_version(model_name: str = Path(...), version_name: str = Path(...), model_service: ModelService = Depends(get_model_service)):
    success, message, model = model_service.set_default_version(model_name, version_name)
    
    if not success:
        if message == '模型不存在':
            raise HTTPException(status_code=404, detail=message)
        elif message == '版本不存在':
            raise HTTPException(status_code=400, detail=message)
        else:
            raise HTTPException(status_code=500, detail=message)
    
    return {
        'message': message,
        'model': model
    }


