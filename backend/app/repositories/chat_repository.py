"""对话数据访问类"""
from sqlalchemy import desc
from app.repositories.base_repository import BaseRepository
from app.models.database.models import Chat, Message

class ChatRepository(BaseRepository):
    """对话数据访问类，处理对话相关的数据访问"""
    
    def get_all_chats(self):
        """获取所有对话"""
        # 从数据库获取所有对话，按更新时间倒序排序
        return self.db.query(Chat).order_by(desc(Chat.updated_at)).all()
    
    def get_chat_by_id(self, chat_id):
        """根据ID获取对话"""
        # 从数据库获取指定ID的对话
        return self.db.query(Chat).filter(Chat.id == chat_id).first()
    
    def create_chat(self, chat_id, title, preview, created_at, updated_at):
        """创建新对话"""
        chat = Chat(
            id=chat_id,
            title=title,
            preview=preview,
            created_at=created_at,
            updated_at=updated_at
        )
        # 添加到数据库
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat
    
    def update_chat(self, chat_id, title, preview, updated_at, pinned=0):
        """更新对话"""
        chat = self.get_chat_by_id(chat_id)
        if chat:
            chat.title = title
            chat.preview = preview
            chat.updated_at = updated_at
            chat.pinned = pinned
            self.db.commit()
            self.db.refresh(chat)
            return chat
        return None
    
    def delete_chat(self, chat_id):
        """删除对话"""
        chat = self.get_chat_by_id(chat_id)
        if chat:
            # 从数据库中删除
            self.db.delete(chat)
            # 同时删除相关的消息
            self.db.query(Message).filter(Message.chat_id == chat_id).delete()
            self.db.commit()
            return True
        return False
    
    def delete_all_chats(self):
        """删除所有对话"""
        # 先删除所有消息
        self.db.query(Message).delete()
        # 再删除所有对话
        self.db.query(Chat).delete()
        self.db.commit()
        return True
    
    def get_chat_with_messages(self, chat_id):
        """获取对话及其所有消息"""
        # 从数据库获取对话
        chat = self.get_chat_by_id(chat_id)
        if chat:
            # 加载相关的消息
            messages = self.db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
            chat.messages = messages
        return chat