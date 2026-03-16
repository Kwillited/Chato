"""向量相关API路由"""
from fastapi import APIRouter, Depends, Body, Query, Path
from app.services.vector.vector_service import VectorService
from app.dependencies import get_vector_service
from app.utils.error_handler import handle_api_errors

router = APIRouter(prefix='/api/vectors')


@router.get("/search", tags=["vectors"])
@handle_api_errors()
async def search_vectors(query: str = Query(..., description="查询文本"), k: int = 5, vector_service: VectorService = Depends(get_vector_service)):
    """根据查询向量检索相关文档
    
    Args:
        query (str): 查询文本
        k (int): 返回结果数量
        
    Returns:
        dict: 向量检索结果
    """
    result = vector_service.search_vectors(query, k)
    return result


@router.post("/search-documents", tags=["vectors"])
@handle_api_errors()
async def search_documents(
    query: str = Query(..., description="查询文本"), 
    k: int = 3, 
    score_threshold: float = 0.7, 
    search_type: str = "similarity", 
    filter: dict = None,
    vector_service: VectorService = Depends(get_vector_service)
):
    """搜索相关文档
    
    Args:
        query (str): 查询文本
        k (int): 返回结果数量
        score_threshold (float): 相似度分数阈值
        search_type (str): 搜索类型
        filter (dict): 过滤条件
        
    Returns:
        list: 相关文档列表
    """
    results = vector_service.search_documents(query, k, score_threshold, search_type, filter)
    return {"success": True, "results": results, "result_count": len(results)}



