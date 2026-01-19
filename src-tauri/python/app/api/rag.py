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

# 获取文档列表
@router.get('/documents')
@handle_exception
def get_documents(rag_service: RAGService = Depends(get_rag_service)):
    # 调用服务层方法获取文档列表
    documents = rag_service.get_documents()
    
    # 获取所有文件夹信息，建立id到name的映射
    folders = rag_service.get_folders()
    folder_id_to_name = {folder['id']: folder['name'] for folder in folders if folder['id']}
    
    # 直接返回文档列表和文件夹ID映射
    return {
        'success': True,
        'documents': documents,
        'folder_id_map': folder_id_to_name  # 返回ID到名称的映射供前端使用
    }

# 获取文件夹列表
@router.get('/folders')
@handle_exception
def get_folders(rag_service: RAGService = Depends(get_rag_service)):
    # 调用服务层方法
    folders = rag_service.get_folders()
    
    return {
        'success': True,
        'folders': folders
    }

# 创建文件夹/知识库
@router.post('/folders')
@handle_exception
def create_folder(folder_data: dict, rag_service: RAGService = Depends(get_rag_service)):
    folder_name = folder_data.get('name')
    
    # 调用服务层方法
    result = rag_service.create_folder(folder_name)
    
    return {
        'success': True,
        'message': result['message'],
        'id': result['id'],
        'name': result['name'],
        'path': result['path']
    }

# 获取指定文件夹中的文件(通过folder_id)
@router.get('/folders/by-id/{folder_id}/files')
@handle_exception
def get_files_in_folder_by_id(folder_id: str = Path(...), rag_service: RAGService = Depends(get_rag_service)):
    # 调用服务层方法，使用folder_id获取文件夹内容
    files = rag_service.get_files_in_folder_by_id(folder_id)
    
    return {
        'success': True,
        'files': files,
        'folder_id': folder_id
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

# 获取文件详情
@router.get('/documents/{file_id}')
@handle_exception
def get_document_details(file_id: str = Path(...), rag_service: RAGService = Depends(get_rag_service)):
    # 调用服务层方法
    details = rag_service.get_document_details(file_id)
    
    return {
        'success': True,
        'details': details
    }

# 删除所有文档
@router.delete('/documents/delete-all')
@handle_exception
def delete_all_documents(rag_service: RAGService = Depends(get_rag_service)):
    # 调用服务层方法
    result = rag_service.delete_all_documents()
    
    # 检查结果是否成功
    if result.get('success') is False:
        # 处理失败情况
        return {
            'success': False,
            'message': result.get('error', '删除所有文档失败')
        }
    
    # 处理成功情况
    return {
        'success': True,
        'message': result['message'],
        'deleted_count': result['deleted_count']
    }

# 删除文档
@router.delete('/{foldername}/{filename}')
@handle_exception
def delete_document(foldername: str = Path(...), filename: str = Path(...), rag_service: RAGService = Depends(get_rag_service)):
    # 调用服务层方法，传递foldername参数
    result = rag_service.delete_document(filename, foldername)
    
    # 检查结果是否成功
    if result.get('success') is False:
        # 处理失败情况
        return {
            'success': False,
            'message': result.get('error', '删除文档失败')
        }
    
    # 处理成功情况
    return {
        'success': True,
        'message': result['message'],
        'deleted_file': result['deleted_file'],
        'folder': result['folder']
    }

# 删除文件夹/知识库
@router.delete('/folders')
@handle_exception
def delete_folder(folder_id: str = Query(..., description='文件夹ID'), rag_service: RAGService = Depends(get_rag_service)):
    # 调用服务层方法，现在使用folder_id参数
    result = rag_service.delete_folder_by_id(folder_id)
    
    # 检查结果是否成功
    if result.get('success') is False:
        # 处理失败情况
        return {
            'success': False,
            'message': result.get('error', '删除文件夹失败')
        }
    
    # 处理成功情况
    return {
        'success': True,
        'message': result['message'],
        'deleted_folder': result['deleted_folder'],
        'folder_id': folder_id
    }