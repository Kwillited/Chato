"""RAG相关API路由"""
from fastapi import APIRouter, Form, File, UploadFile, Query, Path, HTTPException, Depends

# 导入RAG服务层
from app.services.rag.rag_service import RAGService
from app.utils.decorators import handle_exception
from app.dependencies import get_rag_service

# 创建RAG API路由（前缀统一为 /api/rag）
router = APIRouter(prefix='/api/rag')

# 上传文档
@router.post('/upload')
@handle_exception
def upload_document(file: UploadFile = File(...), folder_id: str = Form(''), rag_service: RAGService = Depends(get_rag_service)):
    # 调用服务层方法，传递folder_id参数
    result = rag_service.upload_document(file, folder_id=folder_id)
    
    return {
        'success': True,
        'message': result['message'],
        'file_path': result['file_path']
    }

# 搜索文件内容
@router.get('/search')
@handle_exception
def search_file_content(query: str = Query('', description='搜索关键词'), rag_service: RAGService = Depends(get_rag_service)):
    query = query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail='搜索关键词不能为空')
    
    # 调用服务层方法
    results = rag_service.search_file_content(query)
    
    return {
        'success': True,
        'results': results
    }