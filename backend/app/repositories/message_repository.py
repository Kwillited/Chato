"""消息数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.database.models import Message
from app.core.memory_database import memory_db

class MessageRepository(BaseRepository):
    """消息数据访问类，处理消息相关的数据访问"""
    
    def get_messages_by_chat_id(self, chat_id):
        """根据对话ID获取所有消息"""
        # 从内存数据库查询消息
        messages = memory_db.query('messages', chat_id=chat_id)
        # 按created_at排序
        return sorted(messages, key=lambda x: x.created_at)
    
    def get_message_by_id(self, message_id):
        """根据ID获取消息"""
        # 从内存数据库获取消息
        return memory_db.get('messages', message_id)
    
    def create_message(self, message_id, chat_id, role, content, reasoning_content, created_at, model, files=None, 
                       message_type="normal", agent_session_id=None, agent_node="", agent_step=0, agent_metadata=""):
        """创建新消息"""
        message = Message(
            id=message_id,
            chat_id=chat_id,
            role=role,
            message_type=message_type,
            content=content,
            reasoning_content=reasoning_content,
            created_at=created_at,
            model=model,
            files=files,
            agent_session_id=agent_session_id,
            agent_node=agent_node,
            agent_step=agent_step,
            agent_metadata=agent_metadata
        )
        return self.add(message)
    
    def update_message(self, message_id, role, content, reasoning_content, created_at, model, files=None, 
                       message_type=None, agent_session_id=None, agent_node=None, agent_step=None, agent_metadata=None):
        """更新消息"""
        message = self.get_message_by_id(message_id)
        if message:
            message.role = role
            message.content = content
            message.reasoning_content = reasoning_content
            message.created_at = created_at
            message.model = model
            if files is not None:
                message.files = files
            if message_type is not None:
                message.message_type = message_type
            if agent_session_id is not None:
                message.agent_session_id = agent_session_id
            if agent_node is not None:
                message.agent_node = agent_node
            if agent_step is not None:
                message.agent_step = agent_step
            if agent_metadata is not None:
                message.agent_metadata = agent_metadata
            return self.update(message)
        return None
    
    def delete_messages_by_chat_id(self, chat_id):
        """根据对话ID删除所有消息"""
        # 从内存数据库查询消息
        messages = memory_db.query('messages', chat_id=chat_id)
        # 删除所有消息
        for message in messages:
            memory_db.delete('messages', message.id)
        return len(messages)
    
    def delete_all_messages(self):
        """删除所有消息"""
        # 从内存数据库获取所有消息
        messages = memory_db.get('messages')
        # 删除所有消息
        for message in messages:
            memory_db.delete('messages', message.id)
        return len(messages)
    
    def delete_message(self, message_id):
        """删除消息"""
        message = self.get_message_by_id(message_id)
        if message:
            self.delete(message)
            return True
        return False
    
    def create_or_update_message(self, message_id, chat_id, role, content, reasoning_content, created_at, model, files=None, 
                                message_type="normal", agent_session_id=None, agent_node="", agent_step=0, agent_metadata=""):
        """创建或更新消息"""
        message = self.get_message_by_id(message_id)
        if message:
            # 更新现有消息
            message.chat_id = chat_id
            message.role = role
            message.content = content
            message.reasoning_content = reasoning_content
            message.created_at = created_at
            message.model = model
            if files is not None:
                message.files = files
            if message_type is not None:
                message.message_type = message_type
            if agent_session_id is not None:
                message.agent_session_id = agent_session_id
            if agent_node is not None:
                message.agent_node = agent_node
            if agent_step is not None:
                message.agent_step = agent_step
            if agent_metadata is not None:
                message.agent_metadata = agent_metadata
            return self.update(message)
        else:
            # 创建新消息
            return self.create_message(message_id, chat_id, role, content, reasoning_content, created_at, model, files, 
                                     message_type, agent_session_id, agent_node, agent_step, agent_metadata)
