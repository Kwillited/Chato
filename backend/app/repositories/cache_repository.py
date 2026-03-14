"""缓存操作Repository"""
from typing import Optional, Any, Dict, List
from app.core.cache import cache_manager
from app.repositories.base_repository import BaseRepository


class CacheRepository(BaseRepository):
    """缓存操作Repository，负责所有缓存相关操作"""
    
    def get(self, key: str) -> Optional[Any]:
        """从缓存获取数据
        
        Args:
            key: 缓存键名
            
        Returns:
            缓存的数据，如果不存在返回None
        """
        return cache_manager.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        """设置缓存数据
        
        Args:
            key: 缓存键名
            value: 缓存数据
            
        Returns:
            操作是否成功
        """
        return cache_manager.set(key, value)
    
    def update(self, key: str, updates: Dict[str, Any]) -> Optional[Any]:
        """更新缓存数据
        
        Args:
            key: 缓存键名
            updates: 更新的数据字典
            
        Returns:
            更新后的数据，如果不存在返回None
        """
        return cache_manager.update(key, updates)
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在
        
        Args:
            key: 缓存键名
            
        Returns:
            缓存是否存在
        """
        return cache_manager.exists(key)
    
    def set_dirty_flag(self, key: str, value: bool = True) -> None:
        """设置脏标记
        
        Args:
            key: 缓存键
            value: 是否为脏数据，默认为True
        """
        cache_manager.set_dirty_flag(key, value)
    
    def is_dirty(self, key: str) -> bool:
        """检查是否有脏标记
        
        Args:
            key: 缓存键
            
        Returns:
            是否有脏标记
        """
        return cache_manager.is_dirty(key)
    
    def clear_dirty_flag(self, key: str) -> None:
        """清除脏标记
        
        Args:
            key: 缓存键
        """
        cache_manager.clear_dirty_flag(key)
    
    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """获取单个对话
        
        Args:
            chat_id: 对话ID
            
        Returns:
            对话数据，如果不存在返回None
        """
        return cache_manager.get_chat(chat_id)
    
    def set_chat(self, chat_id: str, chat_data: Dict[str, Any]) -> bool:
        """设置单个对话
        
        Args:
            chat_id: 对话ID
            chat_data: 对话数据
            
        Returns:
            操作是否成功
        """
        return cache_manager.set_chat(chat_id, chat_data)
    
    def update_message(self, chat_id: str, message_id: str, message_data: Dict[str, Any]) -> bool:
        """更新单条消息
        
        Args:
            chat_id: 对话ID
            message_id: 消息ID
            message_data: 消息数据
            
        Returns:
            操作是否成功
        """
        return cache_manager.update_message(chat_id, message_id, message_data)
    
    def add_message(self, chat_id: str, message_data: Dict[str, Any]) -> bool:
        """添加新消息
        
        Args:
            chat_id: 对话ID
            message_data: 消息数据
            
        Returns:
            操作是否成功
        """
        return cache_manager.add_message(chat_id, message_data)
    
    def update_chat_no_dirty(self, chat_id: str, chat_data: Dict[str, Any]) -> bool:
        """更新单个对话但不设置脏标记
        
        Args:
            chat_id: 对话ID
            chat_data: 对话数据
            
        Returns:
            操作是否成功
        """
        return cache_manager.update_chat_no_dirty(chat_id, chat_data)
    
    def is_chat_dirty(self, chat_id: str) -> bool:
        """检查对话是否有脏标记
        
        Args:
            chat_id: 对话ID
            
        Returns:
            是否有脏标记
        """
        return cache_manager.is_chat_dirty(chat_id)
    
    def clear_chat_dirty_flag(self, chat_id: str) -> None:
        """清除对话脏标记
        
        Args:
            chat_id: 对话ID
        """
        cache_manager.clear_chat_dirty_flag(chat_id)
    
    def get_dirty_chats(self) -> List[str]:
        """获取所有脏对话的ID
        
        Returns:
            脏对话ID列表
        """
        return cache_manager.get_dirty_chats()
    
    def clear(self, key: Optional[str] = None) -> bool:
        """清除缓存
        
        Args:
            key: 缓存键名，如果为None则清除所有缓存
            
        Returns:
            操作是否成功
        """
        return cache_manager.clear(key)
