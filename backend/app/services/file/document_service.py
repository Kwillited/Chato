"""文档管理服务 - 负责文档的上传、存储、管理和检索"""
import os
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
from app.core.config import config_manager
from app.services.base_service import BaseService
from app.services.data_service import DataService
from app.services.vector.vector_service import VectorService

# 使用config_manager获取标准用户数据目录
user_data_dir = config_manager.get_user_data_dir()

RAG_DIR = os.path.join(user_data_dir, 'Retrieval-Augmented Generation')
DATA_DIR = os.path.join(RAG_DIR, 'files')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)

class DocumentService(BaseService):
    """文档管理服务类 - 封装所有与文档文件系统相关的操作"""
    
    def __init__(self):
        """初始化文档管理服务"""
        self.data_service = DataService()
        self.vector_service = VectorService()
    
    def _get_folder_name_by_id(self, folder_id):
        """根据folder_id查找对应的folder_name"""
        if not folder_id:
            return ''
        
        # 通过DataService获取文件夹名称
        folder = self.data_service.get_folder_by_id(folder_id)
        return folder.name if folder else folder_id
    
    def _get_file_save_path(self, filename, folder_name):
        """构建文件保存路径"""
        if folder_name:
            # 如果指定了文件夹，保存到该文件夹
            # 保留原始文件夹名称，确保中文文件夹名不被截断
            # 注意：这里直接使用folder_name，不再使用secure_filename，确保中文文件夹名正确保存
            folder_path = os.path.join(DATA_DIR, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            # 直接使用原始文件名，确保包含中文
            return os.path.join(folder_path, filename)
        else:
            # 否则保存到根目录，直接使用原始文件名
            return os.path.join(DATA_DIR, filename)
    
    def save_document(self, file, folder_id=''):
        """保存文档到文件系统和数据库"""
        # 检查文件名是否为空
        if file.filename == '':
            raise ValueError('文件名不能为空')
        
        # 保留原始文件名，确保中文文件名不被截断
        original_filename = file.filename
        
        # 根据folder_id获取实际的folder_name
        folder_name = self._get_folder_name_by_id(folder_id)
        
        # 确定保存路径，使用原始文件名
        file_path = self._get_file_save_path(original_filename, folder_name)
        
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
        
        # 将文档信息保存到数据库，通过DataService层
        self.data_service.create_document(
            document_id=document_id,
            name=original_filename,
            path=file_path,
            size=file_size,
            type=file_type,
            uploaded_at=now,
            folder_id=folder_id
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
            folder_name = ''
            if doc.folder_id:
                folder = self.data_service.get_folder_by_id(doc.folder_id)
                folder_name = folder.name if folder else ''
            
            documents.append({
                'name': doc.name,
                'folder': folder_name,
                'path': doc.path
            })
        return documents
    
    def delete_document(self, filename, folder_name=''):
        """删除指定文档/文件"""
        # 参数验证
        if not filename:
            raise ValueError('文件名不能为空')
        
        # 构建文件路径，直接使用原始文件名
        if folder_name:
            # 如果指定了文件夹，构建完整路径
            # 保留原始文件夹名称，确保中文文件夹名不被截断
            folder_path = os.path.join(DATA_DIR, folder_name)
            file_path = os.path.join(folder_path, filename)
        else:
            # 在根目录查找文件，直接使用原始文件名
            file_path = os.path.join(DATA_DIR, filename)
        
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
                return {
                    'deleted_file': filename,
                    'folder': folder_name,
                    'message': f'文档 {filename} 已成功删除',
                    'success': True
                }
            except Exception as e:
                self.log_error(f"删除文件 {file_path} 时出错: {e}")
                return {
                    'deleted_file': filename,
                    'folder': folder_name,
                    'message': f'删除文档 {filename} 失败: {str(e)}',
                    'success': False
                }
        
        # 文件不存在的情况
        self.log_warning(f"尝试删除不存在的文件: {file_path}")
        return {
            'deleted_file': filename,
            'folder': folder_name,
            'message': f'文档 {filename} 不存在',
            'success': True  # 返回True，因为文件已经不存在
        }
    
    def get_folders(self):
        """获取文件夹列表"""
        # 通过DataService获取文件夹列表
        db_folders = self.data_service.get_folders()
        
        # 转换为前端需要的格式
        folders = []
        for folder in db_folders:
            if folder:
                # 构建文件夹路径
                folder_path = os.path.join(DATA_DIR, folder.name)
                
                folders.append({
                    'id': folder.id,
                    'name': folder.name,
                    'path': folder_path
                })
        return folders
    
    def create_folder(self, folder_name, embedding_model=None):
        """创建文件夹/知识库"""
        # 保留原始文件夹名称，确保中文文件夹名不被截断
        # 只对文件夹名进行基本验证，不使用secure_filename（会移除中文等非ASCII字符）
        if not folder_name or not folder_name.strip():
            raise ValueError('文件夹名称不能为空')
        
        # 检查文件夹是否已存在（数据库中）
        existing_folder = self.data_service.get_folder_by_name(folder_name)
        if existing_folder:
            raise ValueError('文件夹已存在')
        
        # 生成唯一ID（UUID前8位）
        folder_id = str(uuid.uuid4())[:8]
        
        # 获取当前时间
        now = datetime.now().isoformat()
        
        # 创建文件夹（文件系统）
        folder_path = os.path.join(DATA_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # 在数据库中创建文件夹记录，通过DataService层
        self.data_service.create_folder(
            folder_id=folder_id,
            name=folder_name,
            embedding_model=embedding_model,
            created_at=now,
            updated_at=now
        )
        
        # 只有当embedding_model不为空时才初始化向量数据库
        if embedding_model:
            try:
                from app.services.vector.vector_service import VectorService
                from app.services.vector.vector_store_service import VectorStoreService
                from app.services.vector.vector_db_service import VectorDBService
                from app.core.config import config_manager
                
                # 获取向量数据库配置
                vector_db_path = os.path.join(config_manager.get_user_data_dir(), 'Retrieval-Augmented Generation', 'vector_db', folder_name)
                
                # 初始化向量数据库服务
                vector_db_service = VectorDBService(vector_db_path, embedding_model, folder_name)
                
                # 触发向量存储初始化
                # 这里会创建空的Chroma实例
                vector_store = vector_db_service.vector_store
                
                # 记录初始化成功
                self.log_info(f"✅ 知识库向量数据库初始化成功: {folder_name}, 嵌入模型: {embedding_model}")
            except Exception as e:
                # 向量数据库初始化失败不影响文件夹创建
                self.log_warning(f"⚠️  知识库向量数据库初始化失败: {e}")
        
        return {
            'id': folder_id,
            'name': folder_name,
            'path': folder_path,
            'embedding_model': embedding_model,
            'message': f'文件夹 {folder_name} 创建成功'
        }
    
    def get_files_in_folder(self, folder_name):
        """获取指定文件夹中的文件"""
        # 根据文件夹名称获取folder_id
        folder = self.data_service.get_folder_by_name(folder_name)
        if not folder:
            raise ValueError('文件夹不存在')
        
        # 通过DataService获取该文件夹下的所有文档
        db_documents = self.data_service.get_documents_by_folder_id(folder.id)
        
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
        
        # 4. 清空向量数据库
        self.vector_service.manage_vector_store('clear')
        
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
        
        # 构建文件夹路径
        folder_path = os.path.join(DATA_DIR, folder_name)
        
        # 检查文件夹是否存在（文件系统）
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            # 检查数据库中是否存在
            folder = self.data_service.get_folder_by_name(folder_name)
            if folder:
                # 数据库中存在但文件系统中不存在，直接删除数据库记录
                self.data_service.delete_folder(folder.id)
                return {
                    'deleted_folder': folder_name,
                    'message': f'文件夹 {folder_name} 已从数据库中删除',
                    'success': True
                }
            
            self.log_warning(f"尝试删除不存在的文件夹: {folder_path}")
            return {
                'deleted_folder': folder_name,
                'message': f'文件夹 {folder_name} 不存在',
                'success': True  # 返回True，因为文件夹已经不存在
            }
        
        # 1. 获取文件夹ID
        folder = self.data_service.get_folder_by_name(folder_name)
        if not folder:
            # 文件夹在文件系统中存在但数据库中不存在，直接删除文件系统中的文件夹
            shutil.rmtree(folder_path)
            return {
                'deleted_folder': folder_name,
                'message': f'文件夹 {folder_name} 已成功删除',
                'success': True
            }
        
        # 2. 删除数据库中的文件夹（级联删除文件夹下的所有文档和分块）
        self.data_service.delete_folder(folder.id)
        
        # 3. 删除相关向量
        self.vector_service.delete_vectors_by_folder_id(folder.id)
        
        # 4. 删除文件系统中的文件夹
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
    
    def get_files_in_folder_by_id(self, folder_id):
        """通过folder_id获取指定文件夹中的文件"""
        if not folder_id:
            raise ValueError('文件夹ID不能为空')
        
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
        if not file_id:
            raise ValueError('文件ID不能为空')
        
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
        if not folder_id:
            raise ValueError('文件夹ID不能为空')
        
        # 通过DataService获取文件夹信息
        folder = self.data_service.get_folder_by_id(folder_id)
        if not folder:
            raise ValueError('指定ID的文件夹不存在')
        
        # 调用现有的delete_folder方法
        return self.delete_folder(folder.name)
    
    def upload_document(self, file, folder_id=''):
        """上传文件到文件系统并进行向量化处理"""
        try:
            original_filename = file.filename
            self.log_info(f"📤 开始上传文档: 文件名='{original_filename}', folder_id='{folder_id}'")
            
            # 1. 保存文件到文件系统和数据库
            save_result = self.save_document(file, folder_id)
            file_path = save_result['full_path']
            self.log_info(f"✅ 文档已保存到: {file_path}")
            
            # 2. 加载文档
            documents = self._load_document(file_path)
            
            # 3. 分割文档
            split_documents, chunk_size, chunk_overlap = self._split_document(documents)
            
            # 4. 向量化文档
            document_id = save_result.get('id', str(uuid.uuid4()))
            vector_result = self._vectorize_document(split_documents, document_id, file_path, folder_id)
            
            # 5. 准备返回信息
            return self._prepare_response(save_result, original_filename, file_path, folder_id, document_id, split_documents, chunk_size, chunk_overlap, vector_result)
            
        except Exception as e:
            self.log_error(f"❌ 文件 {file.filename} 处理失败: {str(e)}")
            return {
                'filename': file.filename,
                'message': f'文件 {file.filename} 处理失败: {str(e)}',
                'file_path': file.filename,
                'document_info': {},
                'full_path': '',
                'folder_name': folder_id,
                'chunk_info': {},
                'vector_info': {}
            }
    
    def _load_document(self, file_path):
        """加载文档内容"""
        from app.utils.rag.document_loader import DocumentLoader
        
        self.log_info(f"📄 加载文档: {file_path}")
        load_result = DocumentLoader.load_document(file_path)
        
        # 检查是否有错误
        if 'error' in load_result:
            error_msg = load_result.get('error', '文档加载失败')
            self.log_error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        # 检查是否有文档
        documents = load_result.get('documents', [])
        if not documents:
            error_msg = '文档加载失败：未找到文档内容'
            self.log_error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        self.log_info(f"✅ 成功加载文档，共 {len(documents)} 个文档对象")
        return documents
    
    def _split_document(self, documents):
        """分割文档为文本块"""
        from app.utils.rag.text_splitter import TextSplitter
        
        chunk_size = config_manager.get('vector.chunk_size', 1000)
        chunk_overlap = config_manager.get('vector.chunk_overlap', 200)
        
        self.log_info("✂️  开始分割文档...")
        split_result = TextSplitter.split_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        if not split_result['success']:
            error_msg = f"文档分割失败: {split_result['error']}"
            self.log_error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        split_documents = split_result['split_documents']
        self.log_info(f"✅ 文档分割完成，生成 {len(split_documents)} 个文本块")
        return split_documents, chunk_size, chunk_overlap
    
    def _vectorize_document(self, split_documents, document_id, file_path, folder_id):
        """向量化文档并存储"""
        self.log_info("🔢 开始向量化文档...")
        vector_result = self.vector_service.vectorize_documents(
            split_documents,
            document_id,
            file_path,
            folder_id=folder_id
        )
        
        if vector_result['vectorized']:
            self.log_info(f"✅ 向量化成功，生成 {vector_result['vector_count']} 个向量")
        else:
            self.log_warning(f"⚠️  向量化部分失败: {vector_result.get('error', '未知错误')}")
        
        return vector_result
    
    def _prepare_response(self, save_result, original_filename, file_path, folder_id, document_id, split_documents, chunk_size, chunk_overlap, vector_result):
        """准备返回信息"""
        document_info = {
            'document_id': document_id,
            'file_path': file_path,
            'filename': save_result['filename'],
            'split_documents_count': len(split_documents),
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap
        }
        
        chunk_info = {
            'total_chunks': len(split_documents),
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap
        }
        
        self.log_info(f"📊 文档处理完成: 文件='{original_filename}', 文本块={len(split_documents)}, 向量={vector_result['vector_count']}")
        
        return {
            'filename': save_result['filename'],
            'message': f'文件 {save_result['filename']} 上传成功',
            'file_path': save_result['filename'],
            'document_info': document_info,
            'full_path': file_path,
            'folder_name': folder_id,
            'chunk_info': chunk_info,
            'vector_info': vector_result
        }
    
    def search_file_content(self, query):
        """搜索文件内容"""
        # 使用VectorService的search_documents方法实现搜索
        return self.vector_service.search_documents(query)

