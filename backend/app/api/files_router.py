"""文件系统相关API路由"""
from fastapi import APIRouter, Form, File, UploadFile, Query, Path, HTTPException, Depends

# 导入文件管理相关服务
from app.services.file.document_service import DocumentService
from app.utils.decorators import handle_exception
from app.dependencies import get_document_service
from app.models.pydantic_models import (
    DocumentListResponse, FolderListResponse, FolderCreateResponse,
    FilesInFolderResponse, DocumentDetailsResponse, DeleteAllResponse,
    DocumentDeleteResponse, FolderDeleteResponse, SearchResponse
)

# 创建文件系统API路由（前缀统一为 /api/files）
router = APIRouter(prefix='/api/files')

# 获取文档列表
@router.get('/documents', response_model=DocumentListResponse)
@handle_exception
def get_documents(document_service: DocumentService = Depends(get_document_service)):
    """获取所有文档列表"""
    # 调用服务层方法获取文档列表
    documents = document_service.get_documents()
    
    # 获取所有文件夹信息，建立id到name的映射
    folders = document_service.get_folders()
    folder_id_to_name = {folder['id']: folder['name'] for folder in folders if folder['id']}
    
    # 直接返回文档列表和文件夹ID映射
    return DocumentListResponse(
        success=True,
        documents=documents,
        folder_id_map=folder_id_to_name  # 返回ID到名称的映射供前端使用
    )

# 获取文件夹列表
@router.get('/folders', response_model=FolderListResponse)
@handle_exception
def get_folders(document_service: DocumentService = Depends(get_document_service)):
    """获取所有文件夹列表"""
    # 调用服务层方法
    folders = document_service.get_folders()
    
    return FolderListResponse(
        success=True,
        folders=folders
    )

# 创建文件夹/知识库
@router.post('/folders', response_model=FolderCreateResponse)
@handle_exception
def create_folder(folder_data: dict, document_service: DocumentService = Depends(get_document_service)):
    """创建新的文件夹/知识库"""
    folder_name = folder_data.get('name')
    
    # 调用服务层方法
    result = document_service.create_folder(folder_name)
    
    return FolderCreateResponse(
        success=True,
        message=result['message'],
        id=result['id'],
        name=result['name'],
        path=result['path']
    )

# 获取指定文件夹中的文件(通过folder_id)
@router.get('/folders/by-id/{folder_id}/files', response_model=FilesInFolderResponse)
@handle_exception
def get_files_in_folder_by_id(folder_id: str = Path(...), document_service: DocumentService = Depends(get_document_service)):
    """通过文件夹ID获取文件夹中的文件列表"""
    # 调用服务层方法，使用folder_id获取文件夹内容
    files = document_service.get_files_in_folder_by_id(folder_id)
    
    return FilesInFolderResponse(
        success=True,
        files=files,
        folder_id=folder_id
    )

# 获取文件详情
@router.get('/documents/{file_id}', response_model=DocumentDetailsResponse)
@handle_exception
def get_document_details(file_id: str = Path(...), document_service: DocumentService = Depends(get_document_service)):
    """获取指定文件的详细信息"""
    # 调用服务层方法
    details = document_service.get_document_details(file_id)
    
    return DocumentDetailsResponse(
        success=True,
        details=details
    )

# 删除所有文档
@router.delete('/documents/delete-all', response_model=DeleteAllResponse)
@handle_exception
def delete_all_documents(document_service: DocumentService = Depends(get_document_service)):
    """删除所有文档，包括所有文件夹和文件"""
    # 调用服务层方法
    result = document_service.delete_all_documents()
    
    # 检查结果是否成功
    if result.get('success') is False:
        # 处理失败情况
        raise HTTPException(status_code=500, detail=result.get('error', '删除所有文档失败'))
    
    # 处理成功情况
    return DeleteAllResponse(
        success=True,
        message=result['message'],
        deleted_count=result['deleted_count']
    )

# 删除文档
@router.delete('/{foldername}/{filename}', response_model=DocumentDeleteResponse)
@handle_exception
def delete_document(foldername: str = Path(...), filename: str = Path(...), document_service: DocumentService = Depends(get_document_service)):
    """删除指定的文档"""
    # 调用服务层方法，传递foldername参数
    result = document_service.delete_document(filename, foldername)
    
    # 检查结果是否成功
    if result.get('success') is False:
        # 处理失败情况
        raise HTTPException(status_code=500, detail=result.get('error', '删除文档失败'))
    
    # 处理成功情况
    return DocumentDeleteResponse(
        success=True,
        message=result['message'],
        deleted_file=result['deleted_file'],
        folder=result['folder']
    )

# 删除文件夹/知识库
@router.delete('/folders', response_model=FolderDeleteResponse)
@handle_exception
def delete_folder(folder_id: str = Query(..., description='文件夹ID'), document_service: DocumentService = Depends(get_document_service)):
    """通过文件夹ID删除文件夹/知识库"""
    # 调用服务层方法，现在使用folder_id参数
    result = document_service.delete_folder_by_id(folder_id)
    
    # 检查结果是否成功
    if result.get('success') is False:
        # 处理失败情况
        raise HTTPException(status_code=500, detail=result.get('error', '删除文件夹失败'))
    
    # 处理成功情况
    return FolderDeleteResponse(
        success=True,
        message=result['message'],
        deleted_folder=result['deleted_folder'],
        folder_id=folder_id
    )

# 上传文档
@router.post('/upload')
@handle_exception
def upload_document(file: UploadFile = File(...), folder_id: str = Form(''), document_service: DocumentService = Depends(get_document_service)):
    """上传文件到文件系统并进行向量化处理"""
    # 调用服务层方法，传递folder_id参数
    result = document_service.upload_document(file, folder_id=folder_id)
    
    return {
        'success': True,
        'message': result['message'],
        'file_path': result['file_path']
    }

# 搜索文件内容
@router.get('/search', response_model=SearchResponse)
@handle_exception
def search_file_content(query: str = Query('', description='搜索关键词'), document_service: DocumentService = Depends(get_document_service)):
    query = query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail='搜索关键词不能为空')
    
    # 调用服务层方法
    results = document_service.search_file_content(query)
    
    return SearchResponse(
        success=True,
        results=results
    )
