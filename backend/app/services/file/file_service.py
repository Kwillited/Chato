"""文件服务模块 - 封装文件管理、文件夹管理和内容检索功能"""
from app.services.base_service import BaseService
from app.utils import FileUtils

class FileService(BaseService):
    """文件服务类，封装所有文件相关的操作"""
    
    def __init__(self):
        """初始化文件服务"""
        super().__init__()
        from app.core.service_container import service_container
        from app.services.data_service import DataService
        from app.services.vector.vector_service import VectorService
        self.data_service = service_container.get_service('data_service')
        self.vector_service = service_container.get_service('vector_service')
    
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
        return FileUtils.search_files(
            query=query,
            search_type=search_type,
            k=k,
            vector_service=self.vector_service,
            data_service=self.data_service
        )
    

    
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
