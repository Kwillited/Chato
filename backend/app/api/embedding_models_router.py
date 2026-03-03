"""嵌入模型相关API路由"""
from fastapi import APIRouter, Depends, Body, Path, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.dependencies import get_db
from app.services.model.embedding_model_service import EmbeddingModelService
from app.utils.error_handler import handle_api_errors

router = APIRouter(prefix='/api/embedding-models')


@router.get("", tags=["embedding-models"])
@handle_api_errors()
async def get_embedding_models(
    enabled_only: bool = False,
    db: Session = Depends(get_db)
):
    """获取所有嵌入模型
    
    Args:
        enabled_only (bool): 是否只获取启用的模型
        
    Returns:
        List[Dict[str, Any]]: 嵌入模型列表
    """
    embedding_model_service = EmbeddingModelService()
    models = embedding_model_service.get_all_models(db, enabled_only)
    return {
        "success": True,
        "models": models,
        "total": len(models)
    }


@router.get("/default", tags=["embedding-models"])
@handle_api_errors()
async def get_default_embedding_model(
    db: Session = Depends(get_db)
):
    """获取默认的嵌入模型
    
    Returns:
        Dict[str, Any]: 默认嵌入模型信息
    """
    embedding_model_service = EmbeddingModelService()
    default_model = embedding_model_service.get_default_model(db)
    if not default_model:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="未找到默认嵌入模型")
    return {
        "success": True,
        "model": default_model
    }


@router.post("/initialize", tags=["embedding-models"])
@handle_api_errors()
async def initialize_embedding_models(
    db: Session = Depends(get_db)
):
    """初始化嵌入模型，将支持的模型添加到数据库
    
    Returns:
        List[Dict[str, Any]]: 初始化的模型列表
    """
    embedding_model_service = EmbeddingModelService()
    initialized_models = embedding_model_service.initialize_models(db)
    return {
        "success": True,
        "models": initialized_models,
        "total": len(initialized_models),
        "message": f"成功初始化 {len(initialized_models)} 个嵌入模型"
    }


@router.post("/{model_id}/update", tags=["embedding-models"])
@handle_api_errors()
async def update_embedding_model(
    model_id: int = Path(...),
    model_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """更新嵌入模型
    
    Args:
        model_id (int): 模型ID
        model_data (Dict[str, Any]): 模型数据
        
    Returns:
        Dict[str, Any]: 更新后的模型信息
    """
    embedding_model_service = EmbeddingModelService()
    updated_model = embedding_model_service.update_model(db, model_id, model_data)
    if not updated_model:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="嵌入模型不存在")
    return {
        "success": True,
        "model": updated_model,
        "message": "嵌入模型更新成功"
    }


@router.post("/version/{version_id}/update", tags=["embedding-models"])
@handle_api_errors()
async def update_embedding_model_version(
    version_id: int = Path(...),
    version_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """更新模型版本
    
    Args:
        version_id (int): 版本ID
        version_data (Dict[str, Any]): 版本数据
        
    Returns:
        Dict[str, Any]: 更新后的版本信息
    """
    embedding_model_service = EmbeddingModelService()
    updated_version = embedding_model_service.update_model_version(db, version_id, version_data)
    if not updated_version:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="模型版本不存在")
    return {
        "success": True,
        "version": updated_version,
        "message": "模型版本更新成功"
    }


@router.post("/clear-cache", tags=["embedding-models"])
@handle_api_errors()
async def clear_embedding_model_cache():
    """清空嵌入模型缓存
    
    Returns:
        Dict[str, Any]: 清空结果
    """
    embedding_model_service = EmbeddingModelService()
    cleared_count = embedding_model_service.clear_model_cache()
    return {
        "success": True,
        "cleared_count": cleared_count,
        "message": f"成功清空 {cleared_count} 个嵌入模型缓存"
    }


@router.post("/load/{model_name}", tags=["embedding-models"])
@handle_api_errors()
async def load_embedding_model(
    model_name: str = Path(...)
):
    """加载嵌入模型
    
    Args:
        model_name (str): 模型名称
        
    Returns:
        Dict[str, Any]: 加载结果
    """
    embedding_model_service = EmbeddingModelService()
    model = embedding_model_service.load_embedding_model(model_name)
    if model:
        return {
            "success": True,
            "model_name": model_name,
            "message": f"成功加载嵌入模型: {model_name}"
        }
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"加载嵌入模型失败: {model_name}")


@router.post("/{model_name}", tags=["embedding-models"])
@handle_api_errors()
async def configure_embedding_model(
    model_name: str = Path(...),
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """配置特定嵌入模型
    
    Args:
        model_name (str): 模型名称
        data (dict): 配置数据
        
    Returns:
        Dict[str, Any]: 配置结果
    """
    embedding_model_service = EmbeddingModelService()
    success, message, model = embedding_model_service.configure_model(db, model_name, data)
    if not success:
        from fastapi import HTTPException
        if message == '模型不存在':
            raise HTTPException(status_code=404, detail=message)
        else:
            raise HTTPException(status_code=500, detail=message)
    return {
        "success": True,
        "message": message,
        "model": model
    }


@router.delete("/{model_name}", tags=["embedding-models"])
@handle_api_errors()
async def delete_embedding_model(
    model_name: str = Path(...),
    db: Session = Depends(get_db)
):
    """删除特定嵌入模型配置
    
    Args:
        model_name (str): 模型名称
        
    Returns:
        Dict[str, Any]: 删除结果
    """
    embedding_model_service = EmbeddingModelService()
    success, message = embedding_model_service.delete_model(db, model_name)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=message)
    return {
        "success": True,
        "message": message
    }


@router.post("/{model_name}/enabled", tags=["embedding-models"])
@handle_api_errors()
async def update_embedding_model_enabled(
    model_name: str = Path(...),
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """更新嵌入模型启用状态
    
    Args:
        model_name (str): 模型名称
        data (dict): 包含enabled字段的数据集
        
    Returns:
        Dict[str, Any]: 更新结果
    """
    enabled = data.get('enabled', True)
    embedding_model_service = EmbeddingModelService()
    success, message = embedding_model_service.update_model_enabled(db, model_name, enabled)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=message)
    return {
        "success": True,
        "message": message,
        "enabled": enabled
    }


@router.delete("/{model_name}/versions/{version_name}", tags=["embedding-models"])
@handle_api_errors()
async def delete_embedding_model_version(
    model_name: str = Path(...),
    version_name: str = Path(...),
    db: Session = Depends(get_db)
):
    """删除特定嵌入模型的特定版本
    
    Args:
        model_name (str): 模型名称
        version_name (str): 版本名称
        
    Returns:
        Dict[str, Any]: 删除结果
    """
    embedding_model_service = EmbeddingModelService()
    success, message, model = embedding_model_service.delete_version(db, model_name, version_name)
    if not success:
        from fastapi import HTTPException
        if message == '模型不存在':
            raise HTTPException(status_code=404, detail=message)
        elif message == '版本不存在':
            raise HTTPException(status_code=400, detail=message)
        else:
            raise HTTPException(status_code=500, detail=message)
    return {
        "success": True,
        "message": message,
        "model": model
    }
