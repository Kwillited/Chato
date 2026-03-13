"""对话数据访问类"""
import json
from sqlalchemy import desc
from app.repositories.base_repository import BaseRepository
from app.models.database.models import Chat, Message
from app.core.cache import cache_manager

class ChatRepository(BaseRepository):
    """对话数据访问类，处理对话相关的数据访问"""
    
    def _convert_chat_to_dict(self, chat):
        """将Chat对象转换为字典"""
        if isinstance(chat, dict):
            return chat
        
        return {
            'id': chat.id,
            'title': chat.title,
            'preview': chat.preview,
            'createdAt': chat.created_at,
            'updatedAt': chat.updated_at,
            'pinned': bool(chat.pinned),
            'messages': []
        }
    
    def _convert_message_to_dict(self, message):
        """将Message对象转换为字典"""
        if isinstance(message, dict):
            return message
        
        # 反序列化 files 字段
        files = []
        if message.files:
            try:
                files = json.loads(message.files)
            except:
                files = []
        
        return {
            'id': message.id,
            'role': message.role,
            'content': message.content,
            'reasoning_content': message.reasoning_content,
            'createdAt': message.created_at,
            'model': message.model,
            'files': files,
            'agent_node': message.agent_node or '',
            'agent_step': message.agent_step or 0,
            'agent_metadata': message.agent_metadata
        }
    
    def get_all_chats(self):
        """获取所有对话"""
        # 从数据库获取所有对话，按更新时间倒序排序
        chats = self.db.query(Chat).order_by(desc(Chat.updated_at)).all()
        return [self._convert_chat_to_dict(chat) for chat in chats]
    
    def get_chat_by_id(self, chat_id):
        """根据ID获取对话"""
        # 先从缓存获取
        cached_chat = cache_manager.get_chat(chat_id)
        if cached_chat:
            return cached_chat
        
        # 缓存未命中，从数据库获取
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat_dict = self._convert_chat_to_dict(chat)
            # 将对话添加到缓存（不设置脏标记）
            cache_manager.update_chat_no_dirty(chat_id, chat_dict)
            return chat_dict
        return None
    
    def create_chat(self, chat_id, title, preview, created_at, updated_at):
        """创建新对话"""
        # 检查对话ID是否已经存在
        existing_chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if existing_chat:
            # 如果对话已存在，返回现有对话的字典形式
            chat_dict = self._convert_chat_to_dict(existing_chat)
            # 更新缓存
            cache_manager.set_chat(chat_id, chat_dict)
            return chat_dict
        
        # 创建新对话
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
        
        # 转换为字典
        chat_dict = self._convert_chat_to_dict(chat)
        
        # 更新缓存
        cache_manager.set_chat(chat_id, chat_dict)
        
        return chat_dict
    
    def update_chat(self, chat_id, title, preview, updated_at, pinned=0):
        """更新对话"""
        # 直接从数据库获取
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat.title = title
            chat.preview = preview
            chat.updated_at = updated_at
            chat.pinned = pinned
            self.db.commit()
            self.db.refresh(chat)
            
            # 转换为字典
            chat_dict = self._convert_chat_to_dict(chat)
            
            # 更新缓存
            cache_manager.set_chat(chat_id, chat_dict)
            
            return chat_dict
        return None
    
    def delete_chat(self, chat_id):
        """删除对话"""
        # 从缓存中删除对话
        chats = cache_manager.get('chats') or {}
        if chat_id in chats:
            # 从缓存中删除
            del chats[chat_id]
            cache_manager.set('chats', chats)
            # 设置脏标记，以便在保存时从数据库中删除
            with cache_manager._lock:
                dirty_flags = cache_manager._dirty_flags.get('chats', {})
                if isinstance(dirty_flags, dict):
                    dirty_flags[chat_id] = True
            return True
        return False
    
    def delete_all_chats(self):
        """删除所有对话"""
        # 清空缓存
        chats = cache_manager.get('chats') or {}
        chat_ids = list(chats.keys())
        cache_manager.set('chats', {})
        
        # 设置所有对话的脏标记，以便在保存时从数据库中删除
        with cache_manager._lock:
            dirty_flags = cache_manager._dirty_flags.get('chats', {})
            if isinstance(dirty_flags, dict):
                for chat_id in chat_ids:
                    dirty_flags[chat_id] = True
        
        return True
    
    def get_chat_with_messages(self, chat_id):
        """获取对话及其所有消息"""
        # 先从缓存获取
        cached_chat = cache_manager.get_chat(chat_id)
        if cached_chat and cached_chat.get('messages'):
            return cached_chat
        
        # 缓存未命中，从数据库获取
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            # 转换为字典
            chat_dict = self._convert_chat_to_dict(chat)
            
            # 加载相关的消息
            messages = self.db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
            # 转换消息为字典
            chat_dict['messages'] = [self._convert_message_to_dict(msg) for msg in messages]
            
            # 更新缓存（不设置脏标记）
            cache_manager.update_chat_no_dirty(chat_id, chat_dict)
            return chat_dict
        
        return None