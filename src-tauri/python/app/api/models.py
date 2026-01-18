"""模型相关API路由"""
from fastapi import APIRouter, Body, Path, HTTPException, Response, Depends
from fastapi.responses import FileResponse
import os

# 导入模型服务层
from app.services.model.model_service import ModelService
from app.utils.decorators import handle_exception
from app.dependencies import get_model_service

# 创建模型API路由（前缀统一为 /api/models）
router = APIRouter(prefix='/api/models')

# 获取图标目录的绝对路径
ICONS_DIR = r'C:\Users\admin\AppData\Local\Chato\Chato\icon'

# 获取所有模型供应商以及模型版本
@router.get('')
@handle_exception
def get_models(model_service: ModelService = Depends(get_model_service)):
    models = model_service.get_all_models()
    return {'models': models}

# 获取模型供应商图标
@router.get('/icons/{filename}')
@handle_exception
def get_model_icon(filename: str = Path(...)):
    """
    提供模型供应商图标文件下载功能
    参数: filename - 图标文件名，如 'OpenAI.png'
    """
    try:
        # 从数据库获取图片
        from app.repositories.model_repository import ModelRepository
        from app.core.database import get_db
        from sqlalchemy.orm import Session
        
        db: Session = next(get_db())
        model_repo = ModelRepository(db)
        
        # 提取模型名称（去掉文件扩展名）
        model_name = filename.replace('.png', '')
        
        # 查询数据库中的图标
        result = model_repo.get_model_icon(model_name)
        
        if result and result[0]:
            # 从数据库返回图片
            return Response(content=result[0], media_type='image/png')
        else:
            # 从文件系统返回图片（向后兼容）
            if os.path.exists(os.path.join(ICONS_DIR, filename)):
                return FileResponse(os.path.join(ICONS_DIR, filename))
            else:
                raise HTTPException(status_code=404, detail='图标文件不存在')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='图标文件不存在')

# 配置特定模型（按名称）
@router.post('/{model_name}')
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
    
    return {
        'message': message,
        'model': model
    }

# 删除特定模型配置（按名称）
@router.delete('/{model_name}')
@handle_exception
def delete_model(model_name: str = Path(...), model_service: ModelService = Depends(get_model_service)):
    success, message = model_service.delete_model(model_name)
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return {'message': message}

# 更新模型启用状态
@router.post('/{model_name}/enabled')
@handle_exception
def update_model_enabled(model_name: str = Path(...), data: dict = Body(...), model_service: ModelService = Depends(get_model_service)):
    enabled = data.get('enabled', True)
    success, message = model_service.update_model_enabled(model_name, enabled)
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return {
        'message': message,
        'enabled': enabled
    }

# 删除特定模型的特定版本
@router.delete('/{model_name}/versions/{version_name}')
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
    
    return {
        'message': message,
        'model': model
    }

# 辅助函数：从模型的versions数组中获取特定版本的配置信息
def get_version_config(model, version_name):
    from app.dependencies import get_model_service
    model_service = next(get_model_service())
    return model_service.get_version_config(model, version_name)
