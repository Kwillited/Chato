"""消息数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.models import Message

class MessageRepository(BaseRepository):
    """消息数据访问类，处理消息相关的数据访问"""
    
    def get_messages_by_chat_id(self, chat_id):
        """根据对话ID获取所有消息"""
        return self.db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
    
    def get_message_by_id(self, message_id):
        """根据ID获取消息"""
        return self.db.query(Message).filter(Message.id == message_id).first()
    
    def create_message(self, message_id, chat_id, role, actual_content, thinking, created_at, model, files=None):
        """创建新消息"""
        message = Message(
            id=message_id,
            chat_id=chat_id,
            role=role,
            actual_content=actual_content,
            thinking=thinking,
            created_at=created_at,
            model=model,
            files=files
        )
        return self.add(message)
    
    def update_message(self, message_id, role, actual_content, thinking, created_at, model, files=None):
        """更新消息"""
        message = self.get_message_by_id(message_id)
        if message:
            message.role = role
            message.actual_content = actual_content
            message.thinking = thinking
            message.created_at = created_at
            message.model = model
            if files is not None:
                message.files = files
            return self.update(message)
        return None
    
    def delete_messages_by_chat_id(self, chat_id):
        """根据对话ID删除所有消息"""
        # 批量删除，利用SQLAlchemy的删除API
        result = self.db.query(Message).filter(Message.chat_id == chat_id).delete()
        self.db.commit()
        return result
    
    def delete_all_messages(self):
        """删除所有消息"""
        result = self.db.query(Message).delete()
        self.db.commit()
        return result
    
    def delete_message(self, message_id):
        """删除消息"""
        message = self.get_message_by_id(message_id)
        if message:
            self.delete(message)
            return True
        return False
    
    def create_or_update_message(self, message_id, chat_id, role, actual_content, thinking, created_at, model, files=None):
        """创建或更新消息"""
        message = self.get_message_by_id(message_id)
        if message:
            # 更新现有消息
            message.chat_id = chat_id
            message.role = role
            message.actual_content = actual_content
            message.thinking = thinking
            message.created_at = created_at
            message.model = model
            message.files = files
            return self.update(message)
        else:
            # 创建新消息
            return self.create_message(message_id, chat_id, role, actual_content, thinking, created_at, model, files)
