"""对话数据访问类"""
from sqlalchemy import desc
from app.repositories.base_repository import BaseRepository
from app.models.models import Chat, Message

class ChatRepository(BaseRepository):
    """对话数据访问类，处理对话相关的数据访问"""
    
    def get_all_chats(self):
        """获取所有对话"""
        return self.db.query(Chat).order_by(desc(Chat.updated_at)).all()
    
    def get_chat_by_id(self, chat_id):
        """根据ID获取对话"""
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
            return True
        return False
    
    def delete_all_chats(self):
        """删除所有对话"""
        # 删除所有对话（级联删除消息）
        self.db.query(Chat).delete()
        self.db.commit()
        return True
    
    def get_chat_with_messages(self, chat_id):
        """获取对话及其所有消息"""
        return self.db.query(Chat).filter(Chat.id == chat_id).first()
