"""文档处理相关API路由"""
from fastapi import APIRouter, Form, File, UploadFile, Query, Path, HTTPException, Depends

# 导入文档和向量服务层
from app.services.file.document_service import DocumentService
from app.services.vector.vector_service import VectorService
from app.utils.decorators import handle_exception
from app.dependencies import get_document_service

# 创建文档处理API路由（前缀统一为 /api/rag）
router = APIRouter(prefix='/api/rag')

# 上传文档
@router.post('/upload')
@handle_exception
def upload_document(file: UploadFile = File(...), folder_id: str = Form(''), document_service: DocumentService = Depends(get_document_service)):
    # 调用服务层方法，传递folder_id参数
    result = document_service.upload_document(file, folder_id=folder_id)
    
    return {
        'success': True,
        'message': result['message'],
        'file_path': result['file_path']
    }

# 搜索文件内容
@router.get('/search')
@handle_exception
def search_file_content(query: str = Query('', description='搜索关键词'), document_service: DocumentService = Depends(get_document_service)):
    query = query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail='搜索关键词不能为空')
    
    # 调用服务层方法
    results = document_service.search_file_content(query)
    
    return {
        'success': True,
        'results': results
    }