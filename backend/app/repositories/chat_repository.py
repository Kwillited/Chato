"""对话数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import Chat, Message
from app.core.memory_database import memory_db

class ChatRepository(BaseRepository):
    """对话数据访问类，处理对话相关的数据访问"""
    
    def get_all_chats(self):
        """获取所有对话"""
        # 从内存数据库获取所有对话
        chats = memory_db.get('chats')
        # 按updated_at降序排序
        return sorted(chats, key=lambda x: x.updated_at, reverse=True)
    
    def get_chat_by_id(self, chat_id):
        """根据ID获取对话"""
        # 从内存数据库获取对话
        return memory_db.get('chats', chat_id)
    
    def create_chat(self, chat_id, title, preview, created_at, updated_at):
        """创建新对话"""
        chat = Chat(
            id=chat_id,
            title=title,
            preview=preview,
            created_at=created_at,
            updated_at=updated_at
        )
        return self.add(chat)
    
    def update_chat(self, chat_id, title, preview, updated_at, pinned=0):
        """更新对话"""
        chat = self.get_chat_by_id(chat_id)
        if chat:
            chat.title = title
            chat.preview = preview
            chat.updated_at = updated_at
            chat.pinned = pinned
            return self.update(chat)
        return None
    
    def delete_chat(self, chat_id):
        """删除对话"""
        chat = self.get_chat_by_id(chat_id)
        if chat:
            self.delete(chat)
            # 同时删除关联的消息
            messages = memory_db.query('messages', chat_id=chat_id)
            for message in messages:
                memory_db.delete('messages', message.id)
            return True
        return False
    
    def delete_all_chats(self):
        """删除所有对话"""
        # 从内存数据库获取所有对话
        chats = memory_db.get('chats')
        # 删除所有对话
        for chat in chats:
            memory_db.delete('chats', chat.id)
        # 删除所有消息
        messages = memory_db.get('messages')
        for message in messages:
            memory_db.delete('messages', message.id)
        return True
    
    def get_chat_with_messages(self, chat_id):
        """获取对话及其所有消息"""
        # 从内存数据库获取对话
        chat = memory_db.get('chats', chat_id)
        if chat:
            # 获取关联的消息
            chat.messages = memory_db.query('messages', chat_id=chat_id)
        return chat
