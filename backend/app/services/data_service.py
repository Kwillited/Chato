"""数据服务层 - 封装内存数据管理和脏标记机制"""
from app.core.data_manager import save_data, set_dirty_flag
from app.core.cache import cache_manager
from app.services.base_service import BaseService
from app.repositories.folder_repository import FolderRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository

class DataService(BaseService):
    """数据服务类，封装所有数据相关的操作"""
    
    def __init__(self):
        """初始化数据服务"""
        self.folder_repo = FolderRepository()
        self.document_repo = DocumentRepository()
        self.chunk_repo = DocumentChunkRepository()
    
    # 对话相关方法
    @staticmethod
    def get_chats():
        """获取所有对话"""
        chats = cache_manager.get('chats') or {}
        # 对对话列表进行排序，先按置顶状态排序，再按updatedAt降序排列
        chat_list = list(chats.values())
        chat_list.sort(key=lambda x: (not x.get('pinned', False), x.get('updatedAt', '')) , reverse=True)
        return chat_list
    
    @staticmethod
    def get_chat_by_id(chat_id):
        """根据ID获取对话"""
        import json
        # 先从缓存中查找
        chat = cache_manager.get_chat(chat_id)
        
        # 如果缓存中没有，从数据库中查询
        if not chat:
            try:
                from app.repositories.chat_repository import ChatRepository
                from app.core.database import get_db
                
                # 获取数据库会话
                db_session = next(get_db())
                chat_repo = ChatRepository(db_session)
                
                # 从数据库获取对话及其消息
                db_chat = chat_repo.get_chat_with_messages(chat_id)
                if db_chat:
                    # 构建对话字典
                    chat = {
                        'id': db_chat.id,
                        'title': db_chat.title,
                        'preview': db_chat.preview,
                        'createdAt': db_chat.created_at,
                        'updatedAt': db_chat.updated_at,
                        'pinned': bool(db_chat.pinned),
                        'messages': []
                    }
                    
                    # 添加消息
                    if hasattr(db_chat, 'messages') and db_chat.messages:
                        for msg in db_chat.messages:
                            # 反序列化 files 字段
                            files = []
                            if msg.files:
                                try:
                                    files = json.loads(msg.files)
                                except:
                                    files = []
                            
                            message_dict = {
                                'id': msg.id,
                                'role': msg.role,
                                'content': msg.content,
                                'reasoning_content': msg.reasoning_content,
                                'createdAt': msg.created_at,
                                'model': msg.model,
                                'files': files,  # 使用反序列化后的列表
                                'message_type': msg.message_type,
                                'agent_session_id': msg.agent_session_id,
                                'agent_node': msg.agent_node or '',  # 提供默认值
                                'agent_step': msg.agent_step or 0,  # 提供默认值
                                'agent_metadata': msg.agent_metadata
                            }
                            chat['messages'].append(message_dict)
                    
                    # 将对话添加到缓存（不设置脏标记）
                    cache_manager.update_chat_no_dirty(chat_id, chat)
                    
            except Exception as e:
                from app.core.logging_config import logger
                logger.error(f"从数据库获取对话失败: {str(e)}")
        else:
            # 检查消息是否为空，如果为空，从数据库加载
            if not chat.get('messages'):
                try:
                    from app.repositories.chat_repository import ChatRepository
                    from app.core.database import get_db
                    
                    # 获取数据库会话
                    db_session = next(get_db())
                    chat_repo = ChatRepository(db_session)
                    
                    # 从数据库获取对话及其消息
                    db_chat = chat_repo.get_chat_with_messages(chat_id)
                    if db_chat and hasattr(db_chat, 'messages') and db_chat.messages:
                        # 更新消息
                        chat['messages'] = []
                        for msg in db_chat.messages:
                            # 反序列化 files 字段
                            files = []
                            if msg.files:
                                try:
                                    files = json.loads(msg.files)
                                except:
                                    files = []
                            
                            message_dict = {
                                'id': msg.id,
                                'role': msg.role,
                                'content': msg.content,
                                'reasoning_content': msg.reasoning_content,
                                'createdAt': msg.created_at,
                                'model': msg.model,
                                'files': files,  # 使用反序列化后的列表
                                'message_type': msg.message_type,
                                'agent_session_id': msg.agent_session_id,
                                'agent_node': msg.agent_node or '',  # 提供默认值
                                'agent_step': msg.agent_step or 0,  # 提供默认值
                                'agent_metadata': msg.agent_metadata
                            }
                            chat['messages'].append(message_dict)
                        
                        # 更新缓存（不设置脏标记）
                        cache_manager.update_chat_no_dirty(chat_id, chat)
                        
                except Exception as e:
                    from app.core.logging_config import logger
                    logger.error(f"从数据库加载对话消息失败: {str(e)}")
        
        return chat
    
    @staticmethod
    def add_chat(chat):
        """添加对话"""
        chat_id = chat.get('id')
        if chat_id:
            cache_manager.set_chat(chat_id, chat)
    
    @staticmethod
    def remove_chat(chat_id):
        """移除对话"""
        chats = cache_manager.get('chats') or {}
        if chat_id in chats:
            # 先获取被删除的对话数据，用于标记脏标记
            deleted_chat = chats[chat_id]
            # 移除聊天
            del chats[chat_id]
            # 手动将被删除的对话ID标记为脏
            with cache_manager._lock:
                dirty_flags = cache_manager._dirty_flags.get('chats', {})
                if isinstance(dirty_flags, dict):
                    dirty_flags[chat_id] = True
            # 更新缓存
            cache_manager.set('chats', chats)
            
            # 移除相关的智能体会话
            sessions = cache_manager.get('agent_sessions') or []
            sessions_to_remove = [s for s in sessions if s['chat_id'] == chat_id]
            if sessions_to_remove:
                for session in sessions_to_remove:
                    sessions.remove(session)
                cache_manager.set('agent_sessions', sessions)
                cache_manager.set_dirty_flag('agent_sessions')
    
    @staticmethod
    def clear_chats():
        """清空对话"""
        # 先获取所有对话ID，用于标记脏标记
        chats = cache_manager.get('chats') or {}
        chat_ids = list(chats.keys())
        # 清空对话
        cache_manager.set('chats', {})
        # 手动将所有对话ID标记为脏
        with cache_manager._lock:
            dirty_flags = cache_manager._dirty_flags.get('chats', {})
            if isinstance(dirty_flags, dict):
                for chat_id in chat_ids:
                    dirty_flags[chat_id] = True
        
        # 清空所有智能体会话
        cache_manager.set('agent_sessions', [])
        cache_manager.set_dirty_flag('agent_sessions')
    
    @staticmethod
    def update_chat(chat_id, updated_data):
        """更新对话信息"""
        chat = DataService.get_chat_by_id(chat_id)
        if chat:
            chat.update(updated_data)
            # 更新缓存并设置脏标记
            cache_manager.set_chat(chat_id, chat)
    
    @staticmethod
    def add_message_to_chat(chat_id, message):
        """添加消息到对话"""
        chat = DataService.get_chat_by_id(chat_id)
        if chat:
            if 'messages' not in chat:
                chat['messages'] = []
            chat['messages'].append(message)
            # 更新缓存并设置脏标记
            cache_manager.set_chat(chat_id, chat)
    
    @staticmethod
    def update_chat_pin(chat_id, pinned):
        """更新对话置顶状态"""
        chat = DataService.get_chat_by_id(chat_id)
        if chat:
            chat['pinned'] = bool(pinned)
            # 更新缓存并设置脏标记
            cache_manager.set_chat(chat_id, chat)
    
    # 模型相关方法
    @staticmethod
    def get_models():
        """获取所有模型"""
        return cache_manager.get('models')
    
    @staticmethod
    def get_model_by_name(model_name):
        """根据名称获取模型"""
        models = cache_manager.get('models') or []
        return next((m for m in models if m['name'] == model_name), None)
    
    @staticmethod
    def update_model(model_name, updated_model):
        """更新模型"""
        model = DataService.get_model_by_name(model_name)
        if model:
            model.update(updated_model)
            # 由于model是引用，直接设置脏标记即可
            cache_manager.set_dirty_flag('models')
    
    # 设置相关方法
    @staticmethod
    def get_settings():
        """获取所有设置"""
        return cache_manager.get('settings')
    
    @staticmethod
    def update_setting(key, value):
        """更新设置"""
        settings = cache_manager.get('settings') or {}
        settings[key] = value
        cache_manager.set('settings', settings)
    
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
    
    def create_folder(self, folder_id, name, path, vector_db_path=None, embedding_model=None, created_at=None, updated_at=None, description=None):
        """创建文件夹"""
        return self.folder_repo.create_folder(folder_id, name, path, vector_db_path, embedding_model, created_at, updated_at, description)
    
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
    
    def create_document(self, document_id, name, path, size, type, uploaded_at, folder_id):
        """创建文档"""
        return self.document_repo.create_document(document_id, name, path, size, type, uploaded_at, folder_id)
    
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
    
    @staticmethod
    def set_dirty_flag(data_type, is_dirty=True):
        """设置脏标记"""
        cache_manager.set_dirty_flag(data_type, is_dirty)
    
    @staticmethod
    def save_data():
        """保存数据"""
        save_data()
    
    # 智能体会话相关方法
    @staticmethod
    def get_agent_sessions():
        """获取所有智能体会话"""
        return cache_manager.get('agent_sessions')
    
    @staticmethod
    def get_agent_session_by_id(session_id):
        """根据ID获取智能体会话"""
        sessions = cache_manager.get('agent_sessions') or []
        return next((s for s in sessions if s['id'] == session_id), None)
    
    @staticmethod
    def add_agent_session(session):
        """添加智能体会话"""
        sessions = cache_manager.get('agent_sessions') or []
        sessions.insert(0, session)
        cache_manager.set('agent_sessions', sessions)
    
    @staticmethod
    def update_agent_session(session_id, updated_session):
        """更新智能体会话"""
        session = DataService.get_agent_session_by_id(session_id)
        if session:
            session.update(updated_session)
            # 由于session是引用，直接设置脏标记即可
            cache_manager.set_dirty_flag('agent_sessions')
    
    @staticmethod
    def remove_agent_session(session_id):
        """移除智能体会话"""
        sessions = cache_manager.get('agent_sessions') or []
        session_index = next((i for i, s in enumerate(sessions) if s['id'] == session_id), None)
        if session_index is not None:
            sessions.pop(session_index)
            cache_manager.set('agent_sessions', sessions)
    
    @staticmethod
    def clear_agent_sessions():
        """清空智能体会话"""
        cache_manager.set('agent_sessions', [])
    
    @staticmethod
    def get_agent_sessions_by_chat_id(chat_id):
        """根据对话ID获取智能体会话"""
        sessions = cache_manager.get('agent_sessions') or []
        return [s for s in sessions if s['chat_id'] == chat_id]
    
    @staticmethod
    def get_latest_agent_session(chat_id):
        """获取对话的最新智能体会话"""
        sessions = DataService.get_agent_sessions_by_chat_id(chat_id)
        if sessions:
            return sorted(sessions, key=lambda x: x['created_at'], reverse=True)[0]
        return None