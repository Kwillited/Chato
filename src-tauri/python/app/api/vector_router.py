"""向量相关API路由"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.vector.vector_service import VectorService
from app.dependencies import get_vector_service

router = APIRouter(prefix='/api/vectors')


@router.post("/embed-document", tags=["vectors"])
async def embed_document(doc_content: str, metadata: dict, vector_service: VectorService = Depends(get_vector_service)):
    """将文档内容转换为向量表示并存储
    
    Args:
        doc_content (str): 文档内容
        metadata (dict): 文档元数据
        
    Returns:
        dict: 向量化结果
    """
    result = vector_service.embed_document(doc_content, metadata)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.get("/search", tags=["vectors"])
async def search_vectors(query: str, k: int = 5, filter: dict = None, vector_service: VectorService = Depends(get_vector_service)):
    """根据查询向量检索相关文档
    
    Args:
        query (str): 查询文本
        k (int): 返回结果数量
        filter (dict): 过滤条件
        
    Returns:
        dict: 向量检索结果
    """
    result = vector_service.search_vectors(query, k, filter)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.post("/manage", tags=["vectors"])
async def manage_vector_store(action: str, params: dict = None, vector_service: VectorService = Depends(get_vector_service)):
    """向量数据库管理
    
    Args:
        action (str): 操作类型 (clear, stats)
        params (dict): 操作参数
        
    Returns:
        dict: 管理操作结果
    """
    result = vector_service.manage_vector_store(action, params)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.delete("/document/{document_id}", tags=["vectors"])
async def delete_vectors_by_document_id(document_id: str, vector_service: VectorService = Depends(get_vector_service)):
    """根据文档ID删除相关向量
    
    Args:
        document_id (str): 文档ID
        
    Returns:
        dict: 删除结果
    """
    result = vector_service.delete_vectors_by_document_id(document_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.post("/clear", tags=["vectors"])
async def clear_vector_store(vector_service: VectorService = Depends(get_vector_service)):
    """清空向量存储
    
    Returns:
        dict: 清空结果
    """
    result = vector_service.clear_vector_store()
    if not result:
        raise HTTPException(status_code=500, detail="清空向量存储失败")
    return {"success": True, "message": "向量存储已清空"}


@router.post("/search-documents", tags=["vectors"])
async def search_documents(
    query: str, 
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


@router.post("/enhanced-prompt", tags=["vectors"])
async def get_enhanced_prompt(question: str, rag_config: dict = None, vector_service: VectorService = Depends(get_vector_service)):
    """获取增强提示，将查询和检索到的上下文结合
    
    Args:
        question: 用户查询
        rag_config: RAG配置
        
    Returns:
        dict: 增强后的提示
    """
    enhanced_prompt = vector_service.get_enhanced_prompt(question, rag_config)
    return {"success": True, "enhanced_prompt": enhanced_prompt}
