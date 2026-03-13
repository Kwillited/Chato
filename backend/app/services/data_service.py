"""数据服务层 - 封装内存数据管理和脏标记机制"""
from app.core.data_manager import save_data, get_data
from app.core.cache import cache_manager
from app.services.base_service import BaseService
from app.repositories.folder_repository import FolderRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository

class DataService(BaseService):
    """数据服务类，封装所有数据相关的操作"""
    
    def __init__(self):
        """初始化数据服务"""
        from app.repositories.chat_repository import ChatRepository
        from app.core.database import get_db
        
        self.folder_repo = FolderRepository()
        self.document_repo = DocumentRepository()
        self.chunk_repo = DocumentChunkRepository()
        self.db_session = next(get_db())
        self.chat_repo = ChatRepository(self.db_session)
    
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
            cache_manager.set_chat(chat_id, chat)
    
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
            # 使用仓库更新对话
            self.chat_repo.update_chat(
                chat_id=chat_id,
                title=updated_data.get('title', chat.get('title')),
                preview=updated_data.get('preview', chat.get('preview')),
                updated_at=updated_data.get('updatedAt', chat.get('updatedAt')),
                pinned=int(updated_data.get('pinned', chat.get('pinned', 0)))
            )
    
    def add_message_to_chat(self, chat_id, message):
        """添加消息到对话"""
        # 这里需要实现消息的添加逻辑
        # 暂时使用缓存操作，后续可以移到仓库层
        chat = self.get_chat_by_id(chat_id)
        if chat:
            if 'messages' not in chat:
                chat['messages'] = []
            chat['messages'].append(message)
            # 更新缓存并设置脏标记
            cache_manager.set_chat(chat_id, chat)
    
    def update_chat_pin(self, chat_id, pinned):
        """更新对话置顶状态"""
        # 先获取对话
        chat = self.get_chat_by_id(chat_id)
        if chat:
            # 使用仓库更新对话
            self.chat_repo.update_chat(
                chat_id=chat_id,
                title=chat.get('title'),
                preview=chat.get('preview'),
                updated_at=chat.get('updatedAt'),
                pinned=int(pinned)
            )
    
    # 模型相关方法
    def get_models(self):
        """获取所有模型"""
        return get_data('models')
    
    def get_model_by_name(self, model_name):
        """根据名称获取模型"""
        models = get_data('models') or []
        return next((m for m in models if m['name'] == model_name), None)
    
    def update_model(self, model_name, updated_model):
        """更新模型"""
        model = self.get_model_by_name(model_name)
        if model:
            model.update(updated_model)
            # 由于model是引用，直接设置脏标记即可
            cache_manager.set_dirty_flag('models')
    
    # 设置相关方法
    def get_settings(self):
        """获取所有设置"""
        return get_data('settings')
    
    def update_setting(self, key, value):
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
    
    def set_dirty_flag(self, data_type, is_dirty=True):
        """设置脏标记"""
        cache_manager.set_dirty_flag(data_type, is_dirty)
    
    def save_data(self):
        """保存数据"""
        save_data()