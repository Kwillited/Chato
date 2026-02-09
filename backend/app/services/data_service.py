"""数据服务层 - 封装内存数据管理和脏标记机制"""
from app.core.data_manager import db, save_data
from app.services.base_service import BaseService
from app.services.cache_service import cache_manager
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
        return db['chats']
    
    @staticmethod
    def get_chat_by_id(chat_id):
        """根据ID获取对话"""
        return next((c for c in db['chats'] if c['id'] == chat_id), None)
    
    @staticmethod
    def add_chat(chat):
        """添加对话"""
        db['chats'].insert(0, chat)
        DataService.set_dirty_flag('chats')
    
    @staticmethod
    def remove_chat(chat_id):
        """移除对话"""
        chat_index = next((i for i, c in enumerate(db['chats']) if c['id'] == chat_id), None)
        if chat_index is not None:
            db['chats'].pop(chat_index)
            DataService.set_dirty_flag('chats')
    
    @staticmethod
    def clear_chats():
        """清空对话"""
        db['chats'] = []
        DataService.set_dirty_flag('chats')
    
    @staticmethod
    def update_chat(chat_id, updated_data):
        """更新对话信息"""
        chat = DataService.get_chat_by_id(chat_id)
        if chat:
            chat.update(updated_data)
            DataService.set_dirty_flag('chats')
    
    @staticmethod
    def add_message_to_chat(chat_id, message):
        """添加消息到对话"""
        chat = DataService.get_chat_by_id(chat_id)
        if chat:
            if 'messages' not in chat:
                chat['messages'] = []
            chat['messages'].append(message)
            DataService.set_dirty_flag('chats')
    
    @staticmethod
    def update_chat_pin(chat_id, pinned):
        """更新对话置顶状态"""
        chat = DataService.get_chat_by_id(chat_id)
        if chat:
            chat['pinned'] = bool(pinned)
            DataService.set_dirty_flag('chats')
    
    # 模型相关方法
    @staticmethod
    def get_models():
        """获取所有模型"""
        return db['models']
    
    @staticmethod
    def get_model_by_name(model_name):
        """根据名称获取模型"""
        return next((m for m in db['models'] if m['name'] == model_name), None)
    
    @staticmethod
    def update_model(model_name, updated_model):
        """更新模型"""
        model = DataService.get_model_by_name(model_name)
        if model:
            model.update(updated_model)
            DataService.set_dirty_flag('models')
    
    # 设置相关方法
    @staticmethod
    def get_settings():
        """获取所有设置"""
        return db['settings']
    
    @staticmethod
    def update_setting(key, value):
        """更新设置"""
        db['settings'][key] = value
        DataService.set_dirty_flag('settings')
    
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
    
    def create_folder(self, folder_id, name, created_at, updated_at):
        """创建文件夹"""
        return self.folder_repo.create_folder(folder_id, name, created_at, updated_at)
    
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
        from app.core.data_manager import dirty_flags
        if data_type in dirty_flags:
            dirty_flags[data_type] = is_dirty
    
    @staticmethod
    def save_data():
        """保存数据"""
        save_data()
    
    # 智能体会话相关方法
    @staticmethod
    def get_agent_sessions():
        """获取所有智能体会话"""
        return db['agent_sessions']
    
    @staticmethod
    def get_agent_session_by_id(session_id):
        """根据ID获取智能体会话"""
        return next((s for s in db['agent_sessions'] if s['id'] == session_id), None)
    
    @staticmethod
    def add_agent_session(session):
        """添加智能体会话"""
        db['agent_sessions'].insert(0, session)
        DataService.set_dirty_flag('agent_sessions')
    
    @staticmethod
    def update_agent_session(session_id, updated_session):
        """更新智能体会话"""
        session = DataService.get_agent_session_by_id(session_id)
        if session:
            session.update(updated_session)
            DataService.set_dirty_flag('agent_sessions')
    
    @staticmethod
    def remove_agent_session(session_id):
        """移除智能体会话"""
        session_index = next((i for i, s in enumerate(db['agent_sessions']) if s['id'] == session_id), None)
        if session_index is not None:
            db['agent_sessions'].pop(session_index)
            DataService.set_dirty_flag('agent_sessions')
    
    @staticmethod
    def clear_agent_sessions():
        """清空智能体会话"""
        db['agent_sessions'] = []
        DataService.set_dirty_flag('agent_sessions')
    
    @staticmethod
    def get_agent_sessions_by_chat_id(chat_id):
        """根据对话ID获取智能体会话"""
        return [s for s in db['agent_sessions'] if s['chat_id'] == chat_id]
    
    @staticmethod
    def get_latest_agent_session(chat_id):
        """获取对话的最新智能体会话"""
        sessions = DataService.get_agent_sessions_by_chat_id(chat_id)
        if sessions:
            return sorted(sessions, key=lambda x: x['created_at'], reverse=True)[0]
        return None
