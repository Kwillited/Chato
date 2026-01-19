"""RAG服务层模块 - 封装RAG相关的业务逻辑"""
import time
from app.services.base_service import BaseService
from app.services.rag.rag_coordinator import RagCoordinator

class RAGService(BaseService):
    """RAG服务类 - 封装所有RAG相关的业务逻辑，使用拆分后的服务组件"""
    
    def __init__(self, rag_coordinator=None):
        """初始化RAG服务
        
        Args:
            rag_coordinator: RAG协调服务实例，用于依赖注入
        """
        self.rag_coordinator = rag_coordinator or RagCoordinator()
        
        # 初始化缓存
        self._cache = {
            'documents': {'data': None, 'timestamp': 0},
            'folders': {'data': None, 'timestamp': 0}
        }
        self._cache_ttl = 60  # 缓存有效期，单位：秒
    
    def _get_cached_data(self, cache_key):
        """获取缓存数据
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存数据或None
        """
        cache_entry = self._cache.get(cache_key)
        if cache_entry and time.time() - cache_entry['timestamp'] < self._cache_ttl:
            return cache_entry['data']
        return None
    
    def _set_cached_data(self, cache_key, data):
        """设置缓存数据
        
        Args:
            cache_key: 缓存键
            data: 缓存数据
        """
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def _invalidate_cache(self, *cache_keys):
        """使缓存失效
        
        Args:
            cache_keys: 缓存键列表
        """
        for key in cache_keys:
            if key in self._cache:
                self._cache[key] = {'data': None, 'timestamp': 0}
    
    def upload_document(self, file, folder_id=''):
        """上传文档到RAG系统并进行向量化处理"""
        try:
            original_filename = file.filename
            self.log_info(f"📤 开始上传文档: 文件名='{original_filename}', 大小={file.size} 字节, folder_id='{folder_id}'")
            
            # 执行完整的文档处理流程
            result = self.rag_coordinator.process_document(file, folder_id)
            
            if not result['success']:
                error_msg = result.get("error", "未知错误")
                self.log_error(f"❌ 文件 {original_filename} 处理失败: {error_msg}")
                return {
                    'filename': original_filename,
                    'message': f'文件 {original_filename} 处理失败: {error_msg}',
                    'file_path': original_filename,
                    'document_info': {},
                    'full_path': '',
                    'folder_name': folder_id,
                    'chunk_info': {},
                    'vector_info': {}
                }
            
            saved_filename = result['file_save_result']['filename']
            self.log_info(f"✅ 文件 {saved_filename} 上传成功，生成 {result['chunk_info']['total_chunks']} 个文本块")
            
            return {
                'filename': saved_filename,
                'message': f'文件 {saved_filename} 上传成功',
                'file_path': saved_filename,
                'document_info': result['document_info'],
                'full_path': result['file_save_result']['full_path'],
                'folder_name': folder_id,
                'chunk_info': result['chunk_info'],
                'vector_info': result['vector_info']
            }
        except Exception as e:
            self.log_error(f"❌ 上传文档时发生异常: {str(e)}")
            return {
                'filename': file.filename,
                'message': f'文件 {file.filename} 上传失败: {str(e)}',
                'file_path': file.filename,
                'document_info': {},
                'full_path': '',
                'folder_name': folder_id,
                'chunk_info': {},
                'vector_info': {}
            }
    
    def get_documents(self):
        """获取文档列表"""
        # 尝试从缓存获取
        cached = self._get_cached_data('documents')
        if cached is not None:
            return cached
        
        # 缓存不存在，从服务获取
        documents = self.rag_coordinator.document_service.get_documents()
        
        # 设置缓存
        self._set_cached_data('documents', documents)
        return documents
    
    def delete_document(self, filename, folder_name=''):
        """删除指定文档/文件"""
        result = self.rag_coordinator.delete_document(filename, folder_name)
        
        # 使文档缓存失效
        self._invalidate_cache('documents')
        return result
    
    def get_folders(self):
        """获取文件夹列表"""
        # 尝试从缓存获取
        cached = self._get_cached_data('folders')
        if cached is not None:
            return cached
        
        # 缓存不存在，从服务获取
        folders = self.rag_coordinator.document_service.get_folders()
        
        # 设置缓存
        self._set_cached_data('folders', folders)
        return folders
    
    def create_folder(self, folder_name):
        """创建文件夹/知识库"""
        result = self.rag_coordinator.document_service.create_folder(folder_name)
        
        # 使文件夹缓存失效
        self._invalidate_cache('folders')
        return result
    
    def get_files_in_folder(self, folder_name):
        """获取指定文件夹中的文件"""
        return self.rag_coordinator.document_service.get_files_in_folder(folder_name)
    
    def get_files_in_folder_by_id(self, folder_id):
        """通过folder_id获取指定文件夹中的文件"""
        # 先获取文件夹名称
        folders = self.get_folders()
        folder_name = next((f['name'] for f in folders if f['id'] == folder_id), '')
        if not folder_name:
            raise ValueError('指定ID的文件夹不存在')
        return self.get_files_in_folder(folder_name)
    
    def delete_all_documents(self):
        """删除所有文档，包括所有文件夹和文件，并清空向量数据库"""
        result = self.rag_coordinator.delete_all_documents()
        
        # 使所有缓存失效
        self._invalidate_cache('documents', 'folders')
        return result
    
    def search_file_content(self, query):
        """搜索文件内容"""
        # 这里可以扩展为同时搜索文件内容和向量数据库
        # 目前保持原有逻辑，只搜索文件系统
        from app.services.rag.document_service import DocumentService
        document_service = DocumentService()
        
        # 简单实现文件内容搜索
        results = []
        query = query.strip().lower()
        
        # 获取所有文档
        documents = document_service.get_documents()
        
        for doc in documents:
            file_path = doc['path']
            try:
                # 尝试读取文本文件内容进行搜索
                if file_path.lower().endswith(('.txt', '.md', '.csv')):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if query in content.lower():
                            results.append({
                                'file': doc['name'],
                                'path': file_path,
                                'folder': doc['folder']
                            })
                # 对于其他类型的文件，只搜索文件名
                elif query in doc['name'].lower():
                    results.append({
                        'file': doc['name'],
                        'path': file_path,
                        'folder': doc['folder']
                    })
            except Exception as file_error:
                self.log_error(f"读取文件 {doc['name']} 时出错: {file_error}")
        
        return results
    
    def get_document_details(self, file_id):
        """获取文件详情"""
        from app.services.rag.document_service import DocumentService
        document_service = DocumentService()
        
        # 这里简化处理，直接将file_id视为文件名
        file_name = file_id
        
        # 获取所有文档
        documents = document_service.get_documents()
        
        # 查找匹配的文档
        doc = next((d for d in documents if d['name'] == file_name), None)
        if not doc:
            raise ValueError('文件不存在')
        
        # 获取文件详情
        import os
        file_stats = os.stat(doc['path'])
        file_details = {
            'id': file_name,
            'name': file_name,
            'path': doc['path'],
            'size': file_stats.st_size,
            'created_at': file_stats.st_ctime,
            'modified_at': file_stats.st_mtime,
            'folder': doc['folder']
        }
        
        return file_details
    
    def delete_folder_by_id(self, folder_id):
        """通过folder_id删除文件夹/知识库"""
        # 先获取文件夹名称
        folders = self.get_folders()
        folder_name = next((f['name'] for f in folders if f['id'] == folder_id), '')
        if not folder_name:
            raise ValueError('指定ID的文件夹不存在')
        return self.delete_folder(folder_name)
    
    def delete_folder(self, folder_name):
        """删除文件夹/知识库"""
        result = self.rag_coordinator.delete_folder(folder_name)
        
        # 使所有缓存失效
        self._invalidate_cache('documents', 'folders')
        return result
    
    def reload_documents(self):
        """重新加载文档到向量库"""
        return self.rag_coordinator.reload_documents()
    
    def _get_folder_name_by_id(self, folder_id):
        """根据folder_id查找对应的文件夹名称"""
        if not folder_id:
            return ''
        
        folders = self.get_folders()
        for folder in folders:
            if folder.get('id') == folder_id:
                return folder['name']
        return ''
