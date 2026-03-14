"""数据服务层 - 封装内存数据管理和脏标记机制"""
from app.services.base_service import BaseService
from app.repositories.folder_repository import FolderRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.embedding_model_repository import EmbeddingModelRepository
from app.repositories.cache_repository import CacheRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.vector_repository import VectorRepository

class DataService(BaseService):
    """数据服务类，封装所有数据相关的操作"""
    
    def __init__(self):
        """初始化数据服务"""
        from app.repositories.chat_repository import ChatRepository
        from app.repositories.model_repository import ModelRepository
        from app.repositories.setting_repository import SettingRepository
        from app.core.database import get_db
        
        self.folder_repo = FolderRepository()
        self.document_repo = DocumentRepository()
        self.chunk_repo = DocumentChunkRepository()
        self.db_session = next(get_db())
        self.chat_repo = ChatRepository(self.db_session)
        self.embedding_model_repo = EmbeddingModelRepository(self.db_session)
        self.model_repo = ModelRepository(self.db_session)
        self.setting_repo = SettingRepository(self.db_session)
        self.cache_repo = CacheRepository()
        self.memory_repo = MemoryRepository()
        
        # 向量相关初始化
        self.vector_repo = VectorRepository()
        self.vector_services = {}  # 按知识库名称存储向量服务实例
    
    # 对话相关方法
    def get_chats(self):
        """获取所有对话"""
        # 从仓库获取所有对话
        chats = self.chat_repo.get_all_chats()
        # 对对话列表进行排序，先按置顶状态排序，再按updatedAt降序排列
        chats.sort(key=lambda x: (not x.get('pinned', False), x.get('updatedAt', '')) , reverse=True)
        return chats
    
    def get_chat_by_id(self, chat_id):
        """根据ID获取对话"""
        # 从仓库获取对话及其消息
        return self.chat_repo.get_chat_with_messages(chat_id)
    
    def add_chat(self, chat):
        """添加或更新对话"""
        chat_id = chat.get('id')
        if chat_id:
            # 检查对话是否已存在
            existing_chat = self.chat_repo.get_chat_by_id(chat_id)
            if existing_chat:
                # 如果对话已存在，更新对话
                self.chat_repo.update_chat(
                    chat_id=chat_id,
                    title=chat.get('title', existing_chat.get('title')),
                    preview=chat.get('preview', existing_chat.get('preview', '')),
                    updated_at=chat.get('updatedAt', existing_chat.get('updatedAt')),
                    pinned=int(chat.get('pinned', existing_chat.get('pinned', 0)))
                )
            else:
                # 如果对话不存在，创建新对话
                self.chat_repo.create_chat(
                    chat_id=chat_id,
                    title=chat.get('title', '新对话'),
                    preview=chat.get('preview', ''),
                    created_at=chat.get('createdAt', ''),
                    updated_at=chat.get('updatedAt', '')
                )
            
            # 无论对话是创建还是更新，都更新缓存中的消息列表
            # 这样在保存到数据库时，消息也会被保存
            self.cache_repo.set_chat(chat_id, chat)
    
    def remove_chat(self, chat_id):
        """移除对话"""
        # 使用仓库删除对话
        return self.chat_repo.delete_chat(chat_id)
    
    def clear_chats(self):
        """清空对话"""
        # 使用仓库删除所有对话
        return self.chat_repo.delete_all_chats()
    
    def update_chat(self, chat_id, updated_data):
        """更新对话信息"""
        # 先获取对话
        chat = self.get_chat_by_id(chat_id)
        if chat:
            # 更新对话数据
            chat.update(updated_data)
            # 通过 add_chat 方法更新对话，确保数据流向统一
            self.add_chat(chat)
    
    def add_message_to_chat(self, chat_id, message):
        """添加消息到对话"""
        # 获取对话
        chat = self.get_chat_by_id(chat_id)
        if chat:
            if 'messages' not in chat:
                chat['messages'] = []
            chat['messages'].append(message)
            # 通过 add_chat 方法更新对话，确保数据流向统一
            self.add_chat(chat)
    
    def update_chat_pin(self, chat_id, pinned):
        """更新对话置顶状态"""
        # 先获取对话
        chat = self.get_chat_by_id(chat_id)
        if chat:
            # 更新对话数据
            chat['pinned'] = bool(pinned)
            # 通过 add_chat 方法更新对话，确保数据流向统一
            self.add_chat(chat)
    
    # 模型相关方法
    def get_models(self):
        """获取所有模型"""
        # 先尝试从内存缓存获取
        models = self.memory_repo.get_data('models')
        if models:
            return models
        # 如果内存缓存为空，从Repository获取并更新缓存
        try:
            db_models = self.model_repo.get_all_models()
            model_list = []
            for model in db_models:
                # 获取模型的所有版本
                versions = self.model_repo.get_model_versions(model.id)
                version_list = []
                for version in versions:
                    version_list.append({
                        'version_name': version.version_name,
                        'custom_name': version.custom_name,
                        'api_key': version.api_key,
                        'api_base_url': version.api_base_url,
                        'streaming_config': version.streaming_config
                    })
                model_list.append({
                    'name': model.name,
                    'description': model.description,
                    'configured': bool(model.configured),
                    'enabled': bool(model.enabled),
                    'icon_url': model.icon_url,
                    'icon_blob': model.icon_blob,
                    'versions': version_list
                })
            # 更新内存缓存
            self.cache_repo.set('models', model_list)
            return model_list
        except Exception as e:
            self.log_error(f"获取模型失败: {str(e)}")
            return []
    
    def get_model_by_name(self, model_name):
        """根据名称获取模型"""
        # 先尝试从内存缓存获取
        models = self.memory_repo.get_data('models') or []
        model = next((m for m in models if m['name'] == model_name), None)
        if model:
            return model
        # 如果内存缓存中不存在，从Repository获取
        try:
            db_model = self.model_repo.get_model_by_name(model_name)
            if db_model:
                # 获取模型的所有版本
                versions = self.model_repo.get_model_versions(db_model.id)
                version_list = []
                for version in versions:
                    version_list.append({
                        'version_name': version.version_name,
                        'custom_name': version.custom_name,
                        'api_key': version.api_key,
                        'api_base_url': version.api_base_url,
                        'streaming_config': version.streaming_config
                    })
                model_data = {
                    'name': db_model.name,
                    'description': db_model.description,
                    'configured': bool(db_model.configured),
                    'enabled': bool(db_model.enabled),
                    'icon_url': db_model.icon_url,
                    'icon_blob': db_model.icon_blob,
                    'versions': version_list
                }
                # 更新内存缓存
                models = self.memory_repo.get_data('models') or []
                existing_index = next((i for i, m in enumerate(models) if m['name'] == model_name), -1)
                if existing_index >= 0:
                    models[existing_index] = model_data
                else:
                    models.append(model_data)
                self.cache_repo.set('models', models)
                return model_data
        except Exception as e:
            self.log_error(f"获取模型失败: {str(e)}")
        return None
    
    def update_model(self, model_name, updated_model):
        """更新模型"""
        try:
            # 先从内存缓存获取模型
            model = self.get_model_by_name(model_name)
            if model:
                # 更新内存缓存中的模型
                model.update(updated_model)
                # 通过Repository更新数据库
                self.model_repo.update_model(
                    name=model['name'],
                    description=model['description'],
                    configured=model['configured'],
                    enabled=model['enabled'],
                    icon_url=model.get('icon_url', ''),
                    icon_blob=model.get('icon_blob', None)
                )
                # 更新模型版本
                if 'versions' in updated_model:
                    db_model = self.model_repo.get_model_by_name(model_name)
                    if db_model:
                        for version in updated_model['versions']:
                            self.model_repo.update_model_version(
                                model_id=db_model.id,
                                version_name=version['version_name'],
                                custom_name=version.get('custom_name', ''),
                                api_key=version.get('api_key', ''),
                                api_base_url=version.get('api_base_url', ''),
                                streaming_config=version.get('streaming_config', False)
                            )
                # 设置脏标记
                self.memory_repo.set_dirty_flag('models')
        except Exception as e:
            self.log_error(f"更新模型失败: {str(e)}")
    
    # 设置相关方法
    def get_settings(self):
        """获取所有设置"""
        # 先尝试从内存缓存获取
        settings = self.memory_repo.get_data('settings')
        if settings:
            return settings
        # 如果内存缓存为空，从Repository获取并更新缓存
        try:
            system_setting = self.setting_repo.get_system_setting()
            if system_setting:
                settings = {
                    'system': {
                        'darkMode': system_setting.dark_mode,
                        'streamingEnabled': system_setting.streaming_enabled,
                        'chatStyle': system_setting.chat_style,
                        'viewMode': system_setting.view_mode,
                        'defaultModel': system_setting.default_model,
                        'vector_db_path': system_setting.vector_db_path,
                        'default_top_k': system_setting.default_top_k,
                        'default_score_threshold': system_setting.default_score_threshold,
                        'newMessage': system_setting.new_message,
                        'sound': system_setting.sound,
                        'system': system_setting.system,
                        'displayTime': system_setting.display_time
                    }
                }
                # 更新内存缓存
                self.cache_repo.set('settings', settings)
                return settings
        except Exception as e:
            self.log_error(f"获取设置失败: {str(e)}")
        return {}
    
    def update_setting(self, key, value):
        """更新设置"""
        try:
            # 获取当前设置
            settings = self.memory_repo.get_data('settings') or {}
            # 更新设置
            settings[key] = value
            # 更新内存缓存
            self.cache_repo.set('settings', settings)
            # 通过Repository更新数据库
            # 如果更新的是system设置，转换为数据库格式并保存
            if key == 'system' and isinstance(value, dict):
                # 转换为数据库字段名（从驼峰命名转换为蛇形命名）
                system_db_data = {
                    'dark_mode': value.get('darkMode', False),
                    'streaming_enabled': value.get('streamingEnabled', True),
                    'chat_style': value.get('chatStyle', 'bubble'),
                    'view_mode': value.get('viewMode', 'grid'),
                    'default_model': value.get('defaultModel', ''),
                    'vector_db_path': value.get('vector_db_path', ''),
                    'default_top_k': value.get('default_top_k', 3),
                    'default_score_threshold': value.get('default_score_threshold', 0.7),
                    'new_message': value.get('newMessage', True),
                    'sound': value.get('sound', False),
                    'system': value.get('system', True),
                    'display_time': value.get('displayTime', '5秒')
                }
                self.setting_repo.create_or_update_system_setting(system_db_data)
            # 设置脏标记
            self.memory_repo.set_dirty_flag('settings')
        except Exception as e:
            self.log_error(f"更新设置失败: {str(e)}")
    
    # 文件管理相关方法
    def get_folders(self):
        """获取所有文件夹"""
        return self.folder_repo.get_all_folders()
    
    def get_folder_by_id(self, folder_id):
        """根据ID获取文件夹"""
        return self.folder_repo.get_folder_by_id(folder_id)
    
    def get_folder_by_name(self, folder_name):
        """根据名称获取文件夹"""
        return self.folder_repo.get_folder_by_name(folder_name)
    
    def create_folder(self, folder_id, name, path, vector_db_path=None, embedding_model=None, created_at=None, updated_at=None, description=None, chunk_size=1000, chunk_overlap=200):
        """创建文件夹"""
        return self.folder_repo.create_folder(folder_id, name, path, vector_db_path, embedding_model, created_at, updated_at, description, chunk_size, chunk_overlap)
    
    def delete_folder(self, folder_id):
        """删除文件夹"""
        return self.folder_repo.delete_folder(folder_id)
    
    def get_documents(self):
        """获取所有文档"""
        return self.document_repo.get_all_documents()
    
    def get_documents_by_folder_id(self, folder_id):
        """根据文件夹ID获取文档"""
        return self.document_repo.get_documents_by_folder_id(folder_id)
    
    def get_document_by_name(self, name):
        """根据名称获取文档"""
        return self.document_repo.get_document_by_name(name)
    
    def create_document(self, document_id, name, path, size, type, uploaded_at, folder_id, chunk_size=1000, chunk_overlap=200):
        """创建文档"""
        return self.document_repo.create_document(document_id, name, path, size, type, uploaded_at, folder_id, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    def delete_document(self, document_id):
        """删除文档"""
        return self.document_repo.delete_document(document_id)
    
    def delete_all_documents(self):
        """删除所有文档"""
        return self.document_repo.delete_all_documents()
    
    def delete_all_folders(self):
        """删除所有文件夹"""
        return self.folder_repo.delete_all_folders()
    
    def create_chunk(self, chunk_id, document_id, chunk_index, content, extra_metadata, vector_collection):
        """创建文档分块"""
        return self.chunk_repo.create_chunk(chunk_id, document_id, chunk_index, content, extra_metadata, vector_collection)
    
    # 嵌入模型相关方法
    def get_all_embedding_models(self, enabled_only: bool = False):
        """获取所有嵌入模型"""
        return self.embedding_model_repo.get_all_models(enabled_only)
    
    def get_embedding_model_by_name(self, model_name: str):
        """根据名称获取嵌入模型"""
        return self.embedding_model_repo.get_model_by_name(model_name)
    
    def get_embedding_model_by_id(self, model_id: int):
        """根据ID获取嵌入模型"""
        return self.embedding_model_repo.get_model_by_id(model_id)
    
    def create_embedding_model(self, model_data):
        """创建嵌入模型"""
        return self.embedding_model_repo.create_model(model_data)
    
    def update_embedding_model(self, model_id: int, model_data):
        """更新嵌入模型"""
        return self.embedding_model_repo.update_model(model_id, model_data)
    
    def delete_embedding_model(self, model_id: int):
        """删除嵌入模型"""
        return self.embedding_model_repo.delete_model(model_id)
    
    def get_embedding_model_versions(self, model_id: int):
        """获取模型的所有版本"""
        return self.embedding_model_repo.get_model_versions(model_id)
    
    def get_embedding_model_version_by_name(self, model_id: int, version_name: str):
        """根据版本名称获取模型版本"""
        return self.embedding_model_repo.get_version_by_name(model_id, version_name)
    
    def create_embedding_model_version(self, version_data):
        """创建模型版本"""
        return self.embedding_model_repo.create_model_version(version_data)
    
    def update_embedding_model_version(self, version_id: int, version_data):
        """更新模型版本"""
        return self.embedding_model_repo.update_model_version(version_id, version_data)
    
    def delete_embedding_model_version(self, version_id: int):
        """删除模型版本"""
        return self.embedding_model_repo.delete_model_version(version_id)
    
    def get_default_embedding_model(self):
        """获取默认的嵌入模型"""
        return self.embedding_model_repo.get_default_model()
    
    def is_embedding_model_table_empty(self):
        """检查嵌入模型表是否为空"""
        return self.embedding_model_repo.is_embedding_model_table_empty()
    
    # 向量相关方法
    def get_vector_service(self, knowledge_base_name="default", vector_db_path=None, embedder_model=None):
        """获取向量服务实例
        
        Args:
            knowledge_base_name: 知识库名称
            vector_db_path: 向量数据库路径
            embedder_model: 嵌入模型名称
            
        Returns:
            向量服务实例
        """
        if knowledge_base_name not in self.vector_services:
            from app.core.config import config_manager
            from app.utils.path_manager import PathManager
            
            # 获取配置
            vector_db_path = vector_db_path or config_manager.get('vector.vector_db_path', '')
            embedder_model = embedder_model or config_manager.get('vector.embedder_model', 'qwen3-embedding-0.6b')
            
            # 构建默认路径
            if not vector_db_path:
                path_manager = PathManager()
                vector_db_path = path_manager.get_vector_db_path(knowledge_base_name)
            
            # 只使用进程隔离模式的向量服务
            from app.services.vector.vector_db_service_mp import VectorDBServiceMP
            self.vector_services[knowledge_base_name] = VectorDBServiceMP(
                vector_db_path=vector_db_path,
                embedder_model=embedder_model,
                knowledge_base_name=knowledge_base_name
            )
        return self.vector_services[knowledge_base_name]
    
    def embed_document(self, doc_content: str, metadata: dict, knowledge_base_name="default"):
        """将文档内容转换为向量表示并存储
        
        Args:
            doc_content: 文档内容
            metadata: 文档元数据
            knowledge_base_name: 知识库名称
            
        Returns:
            向量化结果
        """
        try:
            vector_service = self.get_vector_service(knowledge_base_name)
            # 从vector_service获取向量仓库实例
            vector_repo = vector_service.vector_repository
            # 执行文档向量化
            result = vector_repo.embed_document(doc_content, metadata)
            
            return {
                'success': True,
                'message': '文档向量化成功',
                'chunk_count': result.get('chunk_count', 0),
                'vector_result': result
            }
        except Exception as e:
            self.log_error(f"文档向量化失败: {str(e)}")
            return {
                'success': False,
                'message': f'文档向量化失败: {str(e)}',
                'chunk_count': 0
            }
    
    def search_vectors(self, query: str, k: int = 5, filter: dict = None, score_threshold: float = None, knowledge_base_name="default"):
        """根据查询向量检索相关文档
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 过滤条件
            score_threshold: 相似度分数阈值
            knowledge_base_name: 知识库名称
            
        Returns:
            向量检索结果
        """
        try:
            vector_service = self.get_vector_service(knowledge_base_name)
            # 从vector_service获取向量仓库实例
            vector_repo = vector_service.vector_repository
            # 执行向量检索
            results = vector_repo.search_vectors(query, k=k, filter=filter, score_threshold=score_threshold)
            
            return {
                'success': True,
                'results': results.get('results', []),
                'result_count': results.get('result_count', 0)
            }
        except Exception as e:
            self.log_error(f"向量检索失败: {str(e)}")
            return {
                'success': False,
                'message': f'向量检索失败: {str(e)}',
                'results': [],
                'result_count': 0
            }
    
    def clear_vector_store(self, knowledge_base_name="default"):
        """清空向量存储
        
        Args:
            knowledge_base_name: 知识库名称
            
        Returns:
            清空结果
        """
        try:
            vector_service = self.get_vector_service(knowledge_base_name)
            success, message = vector_service.clear_vector_store()
            
            if success:
                return {'success': True, 'message': '向量存储已清空'}
            else:
                return {'success': False, 'message': message}
        except Exception as e:
            self.log_error(f"清空向量存储失败: {str(e)}")
            return {'success': False, 'message': f'清空向量存储失败: {str(e)}'}
    
    def get_vector_statistics(self, knowledge_base_name="default"):
        """获取向量库统计信息
        
        Args:
            knowledge_base_name: 知识库名称
            
        Returns:
            向量库统计信息
        """
        try:
            vector_service = self.get_vector_service(knowledge_base_name)
            stats = vector_service.get_vector_statistics()
            return stats
        except Exception as e:
            self.log_error(f"获取向量库统计信息失败: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'total_vectors': 0,
                'knowledge_base': knowledge_base_name
            }
    
    def delete_vectors_by_document_id(self, document_id: str, knowledge_base_name="default"):
        """根据文档ID删除相关向量
        
        Args:
            document_id: 文档ID
            knowledge_base_name: 知识库名称
            
        Returns:
            删除结果
        """
        try:
            vector_service = self.get_vector_service(knowledge_base_name)
            # 从vector_service获取向量仓库实例
            vector_repo = vector_service.vector_repository
            # 删除相关向量
            result = vector_repo.delete_vectors_by_document_id(document_id)
            
            return {
                'success': True,
                'message': '文档向量删除成功',
                'deleted_count': result.get('deleted_count', 0)
            }
        except Exception as e:
            self.log_error(f"删除文档相关向量失败: {str(e)}")
            return {
                'success': False,
                'message': f'文档向量删除失败: {str(e)}',
                'deleted_count': 0
            }
    
    def delete_vectors_by_folder_id(self, folder_id: str, knowledge_base_name="default"):
        """根据文件夹ID删除相关向量
        
        Args:
            folder_id: 文件夹ID
            knowledge_base_name: 知识库名称
            
        Returns:
            删除结果
        """
        try:
            vector_service = self.get_vector_service(knowledge_base_name)
            # 从vector_service获取向量仓库实例
            vector_repo = vector_service.vector_repository
            # 删除相关向量
            result = vector_repo.delete_vectors_by_folder_id(folder_id)
            
            return {
                'success': True,
                'message': '文件夹向量删除成功',
                'deleted_count': result.get('deleted_count', 0)
            }
        except Exception as e:
            self.log_error(f"删除文件夹相关向量失败: {str(e)}")
            return {
                'success': False,
                'message': f'文件夹向量删除失败: {str(e)}',
                'deleted_count': 0
            }
    
    def search_documents(self, query: str, k: int = 3, score_threshold: float = 0.7, search_type: str = "similarity", filter: dict = None, knowledge_base_name="default"):
        """搜索相关文档
        
        Args:
            query: 查询文本
            k: 返回结果数量
            score_threshold: 相似度分数阈值
            search_type: 搜索类型
            filter: 过滤条件
            knowledge_base_name: 知识库名称
            
        Returns:
            相关文档列表
        """
        try:
            vector_service = self.get_vector_service(knowledge_base_name)
            # 执行文档搜索
            results = vector_service.search_documents(
                query=query,
                k=k,
                score_threshold=score_threshold,
                search_type=search_type,
                filter=filter
            )
            return results
        except Exception as e:
            self.log_error(f"搜索文档失败: {str(e)}")
            return []
    
    def set_dirty_flag(self, data_type, is_dirty=True):
        """设置脏标记"""
        self.memory_repo.set_dirty_flag(data_type, is_dirty)
    
    def save_data(self):
        """保存数据"""
        self.memory_repo.save_data()