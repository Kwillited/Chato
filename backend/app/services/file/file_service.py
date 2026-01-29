"""文件服务模块 - 封装文件管理、文件夹管理和内容检索功能"""
import os
from typing import List, Dict, Any
from app.services.base_service import BaseService
from app.services.data_service import DataService
from app.services.vector.vector_service import VectorService

class FileService(BaseService):
    """文件服务类，封装所有文件相关的操作"""
    
    def __init__(self):
        """初始化文件服务"""
        super().__init__()
        self.data_service = DataService()
        self.vector_service = VectorService()
    
    def upload_document(self, file, folder_id=''):
        """上传文档并进行向量化处理
        
        Args:
            file: 文件对象
            folder_id: 文件夹ID
            
        Returns:
            dict: 上传结果
        """
        try:
            # 1. 保存文件到文件系统
            # 这里需要实现实际的文件保存逻辑，暂时返回模拟结果
            # 实际实现时，需要将文件保存到磁盘，并记录文件路径
            file_path = f"/tmp/{file.filename}"
            
            # 2. 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                doc_content = f.read()
            
            # 3. 调用向量服务进行向量化处理
            vector_result = self.vector_service.embed_document(
                doc_content=doc_content,
                metadata={'file_path': file_path, 'folder_id': folder_id}
            )
            
            # 4. 返回整合结果
            return {
                'success': True,
                'file_path': file_path,
                'vector_result': vector_result
            }
        except Exception as e:
            self.log_error(f"❌ 文件上传失败: {str(e)}")
            return {
                'success': False,
                'message': f'文件上传失败: {str(e)}',
                'file_path': '',
                'vector_result': None
            }
    
    def search_files(self, query: str, search_type='vector', k=5):
        """搜索文件内容
        
        Args:
            query (str): 查询文本
            search_type (str): 搜索类型 ('vector' 或 'traditional')
            k (int): 返回结果数量
            
        Returns:
            list: 搜索结果
        """
        try:
            self.log_info(f"🔍 开始文件搜索: 查询='{query}', 类型='{search_type}', 结果数量={k}")
            
            if search_type == 'vector':
                # 调用向量服务进行向量检索
                vector_results = self.vector_service.search_vectors(query, k=k)
                if vector_results['success']:
                    # 根据向量检索结果获取文件信息
                    file_results = self._get_files_from_vector_results(vector_results['results'])
                    return file_results
                else:
                    self.log_error(f"❌ 向量检索失败: {vector_results['message']}")
                    return []
            else:
                # 传统内容检索逻辑
                return self._traditional_search(query, k=k)
        except Exception as e:
            self.log_error(f"❌ 文件搜索失败: {str(e)}")
            return []
    
    def _get_files_from_vector_results(self, vector_results):
        """根据向量检索结果获取文件信息
        
        Args:
            vector_results: 向量检索结果
            
        Returns:
            list: 文件信息列表
        """
        file_results = []
        for result in vector_results:
            metadata = result.get('metadata', {})
            file_path = metadata.get('file_path', '')
            if file_path:
                filename = os.path.basename(file_path)
                file_results.append({
                    'file': filename,
                    'path': file_path,
                    'folder': metadata.get('folder_id', ''),
                    'content': result.get('content', '')[:200] + '...' if len(result.get('content', '')) > 200 else result.get('content', '')
                })
        return file_results
    
    def _traditional_search(self, query: str, k=5):
        """传统内容检索
        
        Args:
            query (str): 查询文本
            k (int): 返回结果数量
            
        Returns:
            list: 搜索结果
        """
        try:
            # 从数据服务获取所有文档
            documents = self.data_service.get_documents()
            
            results = []
            query_lower = query.lower()
            
            for doc in documents:
                file_path = doc.get('path', '')
                if file_path:
                    try:
                        # 尝试读取文本文件内容进行搜索
                        if file_path.lower().endswith(('.txt', '.md', '.csv', '.pdf', '.docx')):
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query_lower in content.lower():
                                    results.append({
                                        'file': doc.get('name', ''),
                                        'path': file_path,
                                        'folder': doc.get('folder', '')
                                    })
                        # 对于其他类型的文件，只搜索文件名
                        elif query_lower in doc.get('name', '').lower():
                            results.append({
                                'file': doc.get('name', ''),
                                'path': file_path,
                                'folder': doc.get('folder', '')
                            })
                    except Exception as file_error:
                        self.log_error(f"❌ 读取文件 {doc.get('name', '')} 时出错: {file_error}")
            
            # 返回前k个结果
            return results[:k]
        except Exception as e:
            self.log_error(f"❌ 传统搜索失败: {str(e)}")
            return []
    
    # 文件管理相关方法
    def get_documents(self, folder_id=''):
        """获取文档列表
        
        Args:
            folder_id: 文件夹ID，为空时获取所有文档
            
        Returns:
            list: 文档列表
        """
        try:
            if folder_id:
                return self.data_service.get_documents_by_folder_id(folder_id)
            else:
                return self.data_service.get_documents()
        except Exception as e:
            self.log_error(f"❌ 获取文档列表失败: {str(e)}")
            return []
    
    def get_folders(self):
        """获取文件夹列表
        
        Returns:
            list: 文件夹列表
        """
        try:
            return self.data_service.get_folders()
        except Exception as e:
            self.log_error(f"❌ 获取文件夹列表失败: {str(e)}")
            return []
    
    def create_folder(self, folder_id, name, created_at, updated_at):
        """创建文件夹
        
        Args:
            folder_id: 文件夹ID
            name: 文件夹名称
            created_at: 创建时间
            updated_at: 更新时间
            
        Returns:
            dict: 创建结果
        """
        try:
            return self.data_service.create_folder(folder_id, name, created_at, updated_at)
        except Exception as e:
            self.log_error(f"❌ 创建文件夹失败: {str(e)}")
            return {'success': False, 'message': f'创建文件夹失败: {str(e)}'}
    
    def delete_document(self, document_id):
        """删除文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            dict: 删除结果
        """
        try:
            # 1. 删除文档记录
            result = self.data_service.delete_document(document_id)
            
            if result['success']:
                # 2. 删除相关向量
                vector_result = self.vector_service.delete_vectors_by_document_id(document_id)
                self.log_info(f"🗑️  文档向量删除结果: {vector_result}")
            
            return result
        except Exception as e:
            self.log_error(f"❌ 删除文档失败: {str(e)}")
            return {'success': False, 'message': f'删除文档失败: {str(e)}'}
    
    def delete_folder(self, folder_id):
        """删除文件夹
        
        Args:
            folder_id: 文件夹ID
            
        Returns:
            dict: 删除结果
        """
        try:
            return self.data_service.delete_folder(folder_id)
        except Exception as e:
            self.log_error(f"❌ 删除文件夹失败: {str(e)}")
            return {'success': False, 'message': f'删除文件夹失败: {str(e)}'}
