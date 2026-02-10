"""对话数据访问类"""
from sqlalchemy import desc
from app.repositories.base_repository import BaseRepository
from app.models.database.models import Chat, Message
from app.core.memory_database import memory_db

class ChatRepository(BaseRepository):
    """对话数据访问类，处理对话相关的数据访问"""
    
    def get_all_chats(self):
        """获取所有对话"""
        chats = memory_db.get('chats')
        # 按更新时间倒序排序
        chats.sort(key=lambda x: x.updated_at, reverse=True)
        return chats
    
    def get_chat_by_id(self, chat_id):
        """根据ID获取对话"""
        chats = memory_db.get('chats')
        return next((chat for chat in chats if chat.id == chat_id), None)
    
    def create_chat(self, chat_id, title, preview, created_at, updated_at):
        """创建新对话"""
        chat = Chat(
            id=chat_id,
            title=title,
            preview=preview,
            created_at=created_at,
            updated_at=updated_at
        )
        # 添加到内存数据库
        chats = memory_db.get('chats')
        chats.insert(0, chat)
        # 同步到SQLite
        memory_db.set('chats', chats)
        return chat
    
    def update_chat(self, chat_id, title, preview, updated_at, pinned=0):
        """更新对话"""
        chat = self.get_chat_by_id(chat_id)
        if chat:
            chat.title = title
            chat.preview = preview
            chat.updated_at = updated_at
            chat.pinned = pinned
            # 同步到SQLite
            chats = memory_db.get('chats')
            memory_db.set('chats', chats)
            return chat
        return None
    
    def delete_chat(self, chat_id):
        """删除对话"""
        chat = self.get_chat_by_id(chat_id)
        if chat:
            # 从内存数据库中删除
            chats = memory_db.get('chats')
            chats = [c for c in chats if c.id != chat_id]
            # 同步到SQLite
            memory_db.set('chats', chats)
            return True
        return False
    
    def delete_all_chats(self):
        """删除所有对话"""
        # 清空内存数据库中的聊天
        memory_db.set('chats', [])
        return True
    
    def get_chat_with_messages(self, chat_id):
        """获取对话及其所有消息"""
        return self.get_chat_by_id(chat_id)
