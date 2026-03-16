"""文档管理服务 - 负责文档的上传、存储、管理和检索"""
import os
import shutil
import time
from datetime import datetime
import uuid
from app.core.config import config_manager
from app.services.base_service import BaseService
from app.utils.path_manager import PathManager
from app.services.vector.vector_service import VectorService
from app.core.service_container import service_container
from app.utils.rag.document_loader import DocumentLoader
from app.utils.rag.text_splitter import TextSplitter
from app.utils.error_handler import handle_api_errors
from app.utils.validators import ValidationUtils

# 使用PathManager获取目录路径
DATA_DIR = PathManager.get_data_dir()


class DocumentService(BaseService):
    """文档管理服务类 - 封装所有与文档文件系统相关的操作"""
    
    def __init__(self, data_service, vector_service):
        """初始化文档管理服务
        
        Args:
            data_service: 数据服务实例，用于依赖注入
            vector_service: 向量服务实例，用于依赖注入
        """
        self.data_service = data_service
        self.vector_service = vector_service
    
    def _cleanup_vector_services(self):
        """清理向量服务连接和实例"""
        try:
            # 清除 data_service 中的向量服务实例
            try:
                data_service = service_container.get_service('data_service')
                if hasattr(data_service, 'vector_services'):
                    # 清除向量服务实例缓存
                    data_service.vector_services = {}
            except Exception as e:
                self.log_warning(f"清除 data_service 中的向量服务实例失败: {e}")
            
            # 清除向量服务实例缓存
            if hasattr(VectorService, '_instance'):
                VectorService._instance = None
            
            self.log_info("✅ 向量服务连接已释放")
            return True
        except Exception as e:
            self.log_warning(f"⚠️  释放向量服务连接失败: {e}")
            return False

    def _get_folder_info(self, folder_id):
        """根据folder_id获取文件夹完整信息"""
        if not folder_id:
            return None
        return self.data_service.get_folder_by_id(folder_id)
    
    def _get_folder_name_by_id(self, folder_id):
        """根据folder_id查找对应的folder_name"""
        folder = self._get_folder_info(folder_id)
        return folder.name if folder else folder_id
    
    def _get_folder_path_by_id(self, folder_id):
        """根据folder_id获取文件夹路径"""
        folder = self._get_folder_info(folder_id)
        return folder.path if folder else ''
    
    def _get_vector_db_path_by_id(self, folder_id):
        """根据folder_id获取向量数据库路径"""
        folder = self._get_folder_info(folder_id)
        return folder.vector_db_path if folder else ''
    
    def _get_chunk_parameters(self, folder_id=''):
        """获取分块参数"""
        chunk_size = 1000
        chunk_overlap = 200
        if folder_id:
            folder = self._get_folder_info(folder_id)
            if folder:
                chunk_size = folder.chunk_size if hasattr(folder, 'chunk_size') and folder.chunk_size else 1000
                chunk_overlap = folder.chunk_overlap if hasattr(folder, 'chunk_overlap') and folder.chunk_overlap else 200
        else:
            # 如果没有folder_id，使用配置中的默认值
            chunk_size = config_manager.get('vector.chunk_size', 1000)
            chunk_overlap = config_manager.get('vector.chunk_overlap', 200)
        return chunk_size, chunk_overlap
    
    def _get_file_save_path(self, filename, folder_id=''):
        """构建文件保存路径"""
        if folder_id:
            folder = self._get_folder_info(folder_id)
            if folder and hasattr(folder, 'path') and folder.path:
                # 确保文件夹存在
                PathManager.ensure_dir(folder.path)
                # 直接使用原始文件名，确保包含中文
                return os.path.join(folder.path, filename)
            else:
                # 如果获取路径失败，回退到原方法
                folder_name = folder.name if folder else folder_id
                folder_path = PathManager.get_folder_path(folder_name)
                PathManager.ensure_dir(folder_path)
                return os.path.join(folder_path, filename)
        else:
            # 否则保存到根目录，直接使用原始文件名
            return os.path.join(DATA_DIR, filename)
    
    def save_document(self, file, folder_id=''):
        """保存文档到文件系统和数据库"""
        # 检查文件名是否为空
        ValidationUtils.validate_string_parameter('文件名', file.filename, min_length=1)
        
        # 保留原始文件名，确保中文文件名不被截断
        original_filename = file.filename
        
        # 确定保存路径，使用原始文件名
        file_path = self._get_file_save_path(original_filename, folder_id)
        
        # 保存文件 - 处理FastAPI UploadFile对象
        with open(file_path, 'wb') as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取文件类型
        file_type = original_filename.split('.')[-1].lower() if '.' in original_filename else 'unknown'
        
        # 生成文档ID
        document_id = str(uuid.uuid4())[:12]
        
        # 获取当前时间
        now = datetime.now().isoformat()
        
        # 获取分块参数，优先从文件夹获取
        chunk_size, chunk_overlap = self._get_chunk_parameters(folder_id)
        
        # 将文档信息保存到数据库，通过DataService层
        self.data_service.create_document(
            document_id=document_id,
            name=original_filename,
            path=file_path,
            size=file_size,
            type=file_type,
            uploaded_at=now,
            folder_id=folder_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        return {
            'id': document_id,
            'filename': original_filename,
            'full_path': file_path,
            'file_path': original_filename,
            'folder_id': folder_id
        }
    
    def get_documents(self):
        """获取文档列表"""
        # 通过DataService获取文档列表
        db_documents = self.data_service.get_documents()
        
        # 转换为前端需要的格式
        documents = []
        for doc in db_documents:
            # 获取文件夹名称
            folder_name = self._get_folder_name_by_id(doc.folder_id) if doc.folder_id else ''
            
            documents.append({
                'name': doc.name,
                'folder': folder_name,
                'path': doc.path
            })
        return documents
    
    def get_documents_with_folder_map(self):
        """获取文档列表和文件夹ID映射"""
        # 获取文档列表
        documents = self.get_documents()
        
        # 获取所有文件夹信息，建立id到name的映射
        folders = self.get_folders()
        folder_id_map = {folder['id']: folder['name'] for folder in folders if folder['id']}
        
        return {
            'documents': documents,
            'folder_id_map': folder_id_map
        }
    
    def delete_document(self, filename, folder_name=''):
        """删除指定文档/文件"""
        # 参数验证
        ValidationUtils.validate_string_parameter('文件名', filename, min_length=1)
        
        # 构建文件路径，直接使用原始文件名
        if folder_name:
            # 如果指定了文件夹，构建完整路径
            # 保留原始文件夹名称，确保中文文件夹名不被截断
            folder_path = PathManager.get_folder_path(folder_name)
            file_path = PathManager.get_file_path(folder_path, filename)
        else:
            # 在根目录查找文件，直接使用原始文件名
            file_path = PathManager.get_file_path(DATA_DIR, filename)
        
        # 1. 获取folder_id（如果提供了folder_name）
        folder_id = None
        if folder_name:
            folder = self.data_service.get_folder_by_name(folder_name)
            if folder:
                folder_id = folder.id
        
        # 2. 从数据库中删除文档（级联删除文档分块）
        document = self.data_service.get_document_by_name(filename)
        if document and (not folder_id or document.folder_id == folder_id):
            self.data_service.delete_document(document.id)
        
        # 3. 删除文件系统中的文件
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                os.remove(file_path)
                return self.build_response(
                    success=True,
                    message=f'文档 {filename} 已成功删除',
                    deleted_file=filename,
                    folder=folder_name
                )
            except Exception as e:
                self.log_error(f"删除文件 {file_path} 时出错: {e}")
                return self.build_response(
                    success=False,
                    message=f'删除文档 {filename} 失败: {str(e)}',
                    deleted_file=filename,
                    folder=folder_name
                )
        
        # 文件不存在的情况
        self.log_warning(f"尝试删除不存在的文件: {file_path}")
        return self.build_response(
            success=True,
            message=f'文档 {filename} 不存在',
            deleted_file=filename,
            folder=folder_name
        )
    
    def get_folders(self):
        """获取文件夹列表"""
        # 通过DataService获取文件夹列表
        db_folders = self.data_service.get_folders()
        
        # 转换为前端需要的格式
        folders = []
        for folder in db_folders:
            if folder:
                # 使用数据库中存储的路径
                folder_path = folder.path if hasattr(folder, 'path') else PathManager.get_folder_path(folder.name)
                
                folders.append({
                    'id': folder.id,
                    'name': folder.name,
                    'path': folder_path
                })
        return folders
    
    def create_folder(self, folder_name, embedding_model=None, description='', chunk_size=1000, chunk_overlap=200):
        """创建文件夹/知识库"""
        # 保留原始文件夹名称，确保中文文件夹名不被截断
        # 只对文件夹名进行基本验证，不使用secure_filename（会移除中文等非ASCII字符）
        ValidationUtils.validate_string_parameter('文件夹名称', folder_name, min_length=1)
        
        # 检查文件夹是否已存在（数据库中）
        existing_folder = self.data_service.get_folder_by_name(folder_name)
        if existing_folder:
            raise ValueError('文件夹已存在')
        
        # 生成唯一ID（UUID前8位）
        folder_id = str(uuid.uuid4())[:8]
        
        # 获取当前时间
        now = datetime.now().isoformat()
        
        # 使用PathManager构建路径
        folder_path = PathManager.get_folder_path(folder_name)
        vector_db_path = PathManager.get_vector_db_path(folder_name)
        
        # 确保文件夹存在
        PathManager.ensure_dir(folder_path)
        
        # 在数据库中创建文件夹记录，通过DataService层
        self.data_service.create_folder(
            folder_id=folder_id,
            name=folder_name,
            path=folder_path,
            vector_db_path=vector_db_path,
            embedding_model=embedding_model,
            created_at=now,
            updated_at=now,
            description=description,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # 向量数据库表会在首次添加文档时自动创建
        if embedding_model:
            self.log_info(f"✅ 知识库配置成功: {folder_name}, 嵌入模型: {embedding_model}")
        
        return {
            'id': folder_id,
            'name': folder_name,
            'path': folder_path,
            'embedding_model': embedding_model,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap,
            'message': f'文件夹 {folder_name} 创建成功'
        }
    
    def get_files_in_folder(self, folder_name):
        """获取指定文件夹中的文件"""
        # 根据文件夹名称获取folder_id
        folder = self.data_service.get_folder_by_name(folder_name)
        if not folder:
            raise ValueError('文件夹不存在')
        
        # 调用 get_files_in_folder_by_id 方法
        return self.get_files_in_folder_by_id(folder.id)
    
    def delete_all_documents(self):
        """删除所有文档，包括所有文件夹、文件和向量数据库"""
        # 先检查DATA_DIR是否存在
        if not os.path.exists(DATA_DIR):
            return {
                'deleted_count': 0,
                'skipped_count': 0,
                'message': '没有文档需要删除',
                'success': True
            }
        
        # 统计删除的文件数量和跳过的文件数量
        deleted_count = 0
        skipped_count = 0
        
        # 1. 从数据库获取所有文档，用于统计数量
        all_documents = self.data_service.get_documents()
        deleted_count = len(all_documents)
        
        # 2. 删除数据库中的所有文档和文件夹（通过DataService）
        self.data_service.delete_all_documents()
        self.data_service.delete_all_folders()
        
        # 3. 递归删除文件系统中的所有文件和文件夹
        for root, dirs, files in os.walk(DATA_DIR, topdown=False):
            # 先删除所有文件
            for file in files:
                if not file.startswith('.') and file != 'Thumbs.db':
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        self.log_error(f"删除文件 {file_path} 时出错: {e}")
                        skipped_count += 1
            
            # 然后删除所有子目录
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    self.log_error(f"删除目录 {dir_path} 时出错: {e}")
                    skipped_count += 1
        
        # 4. 删除向量数据库表
        try:
            # 调用向量服务清理方法
            self._cleanup_vector_services()
            
            # 连接到LanceDB并删除所有向量表
            vector_db_root = PathManager.get_vector_db_root()
            import lancedb
            db = lancedb.connect(vector_db_root)
            
            # 获取所有表名
            table_names = db.table_names()
            
            # 删除所有表
            for table_name in table_names:
                try:
                    db.drop_table(table_name)
                    self.log_info(f"✅ 向量数据库表已删除: {table_name}")
                except Exception as e:
                    self.log_warning(f"⚠️  删除向量数据库表 {table_name} 失败: {e}")
            
            self.log_info(f"✅ 所有向量数据库表已清空")
        except Exception as e:
            # 向量数据库表删除失败不影响其他操作
            self.log_warning(f"⚠️  向量数据库表清空失败: {e}")
        
        # 5. 重新初始化DATA_DIR目录（如果被删除）
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 构建返回消息
        message = f'已删除 {deleted_count} 个文件、所有文件夹和向量数据库'
        if skipped_count > 0:
            message += f'，跳过了 {skipped_count} 个无法删除的项目'
        
        return {
            'deleted_count': deleted_count,
            'skipped_count': skipped_count,
            'message': message,
            'success': True
        }
    
    def delete_folder(self, folder_name):
        """删除文件夹/知识库"""
        # 保留原始文件夹名称，确保中文文件夹名不被截断
        # 只对文件夹名进行基本验证，不使用secure_filename（会移除中文等非ASCII字符）
        if not folder_name or not folder_name.strip():
            raise ValueError('文件夹名称不能为空')
        
        # 1. 获取文件夹信息（包括路径）
        folder = self.data_service.get_folder_by_name(folder_name)
        if not folder:
            # 检查文件系统中是否存在
            folder_path = os.path.join(DATA_DIR, folder_name)
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                # 文件夹在文件系统中存在但数据库中不存在，直接删除文件系统中的文件夹
                shutil.rmtree(folder_path)
                return {
                    'deleted_folder': folder_name,
                    'message': f'文件夹 {folder_name} 已成功删除',
                    'success': True
                }
            
            self.log_warning(f"尝试删除不存在的文件夹: {folder_name}")
            return {
                'deleted_folder': folder_name,
                'message': f'文件夹 {folder_name} 不存在',
                'success': True  # 返回True，因为文件夹已经不存在
            }
        
        # 2. 从数据库获取路径信息
        folder_path = folder.path
        vector_db_path = folder.vector_db_path
        
        # 3. 删除数据库中的文件夹（级联删除文件夹下的所有文档和分块）
        self.data_service.delete_folder(folder.id)
        
        # 4. 删除相关向量数据库表
        if vector_db_path:
            try:
                # 构建表名，直接使用文件夹名称作为表名
                table_name = folder_name.replace(' ', '_').lower()
                
                # 清除向量服务实例
                self._cleanup_vector_services()
                
                # 连接到LanceDB并删除对应表
                import lancedb
                db = lancedb.connect(PathManager.get_vector_db_root())
                if table_name in db.table_names():
                    db.drop_table(table_name)
                    self.log_info(f"✅ 向量数据库表已删除: {table_name}")
            except Exception as e:
                # 向量数据库表删除失败不影响文件夹删除
                self.log_warning(f"⚠️  向量数据库表删除失败: {e}")
        
        # 5. 删除文件系统中的文件夹
        if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)
                return {
                    'deleted_folder': folder_name,
                    'message': f'文件夹 {folder_name} 已成功删除',
                    'success': True
                }
            except Exception as e:
                self.log_error(f"删除文件夹 {folder_path} 时出错: {e}")
                return {
                    'deleted_folder': folder_name,
                    'message': f'删除文件夹 {folder_name} 失败: {str(e)}',
                    'success': False
                }
        else:
            return {
                'deleted_folder': folder_name,
                'message': f'文件夹 {folder_name} 已从数据库中删除',
                'success': True
            }
    
    def get_files_in_folder_by_id(self, folder_id):
        """通过folder_id获取指定文件夹中的文件"""
        ValidationUtils.validate_string_parameter('文件夹ID', folder_id, min_length=1)
        
        # 通过DataService获取该文件夹下的所有文档
        db_documents = self.data_service.get_documents_by_folder_id(folder_id)
        
        # 转换为前端需要的格式
        files = []
        for doc in db_documents:
            # 从文件系统获取文件大小和修改时间
            file_size = os.path.getsize(doc.path) if os.path.exists(doc.path) else 0
            modified_at = os.path.getmtime(doc.path) if os.path.exists(doc.path) else 0
            
            files.append({
                'name': doc.name,
                'path': doc.path,
                'size': file_size,
                'modified_at': modified_at
            })
        return files
    
    def get_document_details(self, file_id):
        """获取文件详情"""
        ValidationUtils.validate_string_parameter('文件ID', file_id, min_length=1)
        
        # 这里简化处理，直接将file_id视为文件名
        file_name = file_id
        
        # 获取所有文档
        documents = self.get_documents()
        
        # 查找匹配的文档
        doc = next((d for d in documents if d['name'] == file_name), None)
        if not doc:
            raise ValueError('文件不存在')
        
        # 获取文件详情
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
        ValidationUtils.validate_string_parameter('文件夹ID', folder_id, min_length=1)
        
        # 通过DataService获取文件夹信息
        folder = self._get_folder_info(folder_id)
        if not folder:
            raise ValueError('指定ID的文件夹不存在')
        
        # 调用现有的delete_folder方法
        return self.delete_folder(folder.name)
    
    def get_folder_by_id(self, folder_id):
        """通过folder_id获取文件夹详细信息"""
        ValidationUtils.validate_string_parameter('文件夹ID', folder_id, min_length=1)
        
        # 通过DataService获取文件夹信息
        folder = self._get_folder_info(folder_id)
        if not folder:
            raise ValueError('指定ID的文件夹不存在')
        
        # 获取文件夹中的文件数量
        file_count = len(self.data_service.get_documents_by_folder_id(folder_id))
        
        # 转换为前端需要的格式
        folder_info = {
            'id': folder.id,
            'name': folder.name,
            'path': folder.path,
            'embedding_model': folder.embedding_model if hasattr(folder, 'embedding_model') else None,
            'description': folder.description if hasattr(folder, 'description') else '',
            'created_at': folder.created_at if hasattr(folder, 'created_at') else None,
            'chunk_size': folder.chunk_size if hasattr(folder, 'chunk_size') else 1000,
            'chunk_overlap': folder.chunk_overlap if hasattr(folder, 'chunk_overlap') else 200,
            'file_count': file_count
        }
        
        return folder_info
    

    
    def _process_document(self, file, folder_id=''):
        """通用文档处理流程"""
        try:
            original_filename = file.filename
            self.log_info(f"📤 开始处理文档: 文件名='{original_filename}', folder_id='{folder_id}'")
            
            # 1. 保存文件到文件系统和数据库
            save_result = self.save_document(file, folder_id)
            file_path = save_result['full_path']
            self.log_info(f"✅ 文档已保存到: {file_path}")
            
            # 2. 加载文档 - 直接调用 DocumentLoader
            self.log_info(f"📄 加载文档: {file_path}")
            loader = DocumentLoader()
            documents = loader.load_document(file_path)
            self.log_info(f"✅ 成功加载文档，共 {len(documents)} 个文档对象")
            
            # 3. 分割文档 - 使用 TextSplitter
            split_documents = TextSplitter.split_documents(documents)
            self.log_info(f"✅ 文档分割完成，生成 {len(split_documents)} 个文本块")
            
            # 4. 向量化文档
            document_id = save_result.get('id', str(uuid.uuid4()))
            vector_result = {}
            try:
                self.log_info(f"🔢 开始向量化文档: 文本块数量={len(split_documents)}, 知识库='{folder_id}'")
                
                # 直接通过 data_service 获取向量仓库实例并执行向量化（使用from_documents）
                vector_repo = self.data_service.upload_document_vectors(folder_id=folder_id, documents=split_documents)
                
                # 检查向量存储是否成功初始化
                if vector_repo.vector_store:
                    self.log_info(f"✅ 文档向量化成功: 生成 {len(split_documents)} 个向量, 知识库='{folder_id}'")
                    vector_result = {
                        'vectorized': True,
                        'vector_count': len(split_documents),
                        'message': '文档向量化成功'
                    }
                else:
                    self.log_error(f"❌ 文档向量化失败, 知识库='{folder_id}'")
                    vector_result = {
                        'vectorized': False,
                        'vector_count': 0,
                        'message': '文档向量化失败',
                        'error': '向量存储初始化失败'
                    }
            except Exception as e:
                self.log_error(f"❌ 文档向量化失败: {str(e)}")
                vector_result = {
                    'vectorized': False,
                    'vector_count': 0,
                    'message': f'文档向量化失败: {str(e)}',
                    'error': str(e)
                }
            
            # 5. 准备返回信息
            return {
                'filename': save_result['filename'],
                'message': f'文件 {save_result['filename']} 处理成功',
                'document_id': document_id,
                'full_path': file_path,
                'folder_name': folder_id,
                'vector_info': vector_result
            }
            
        except Exception as e:
            self.log_error(f"❌ 文件 {file.filename} 处理失败: {str(e)}")
            base_error_response = {
                'filename': file.filename,
                'message': f'文件 {file.filename} 处理失败: {str(e)}',
                'document_id': '',
                'full_path': '',
                'folder_name': folder_id,
                'vector_info': {}
            }
            return base_error_response
    
    def upload_document(self, file, folder_id=''):
        """上传文件到文件系统并进行向量化处理"""
        return self._process_document(file, folder_id)
    
    def search_file_content(self, query):
        """搜索文件内容"""
        # 使用VectorService的search_documents方法实现搜索
        return self.vector_service.search_documents(query)

