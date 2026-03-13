"""统一缓存管理模块"""
import threading
from typing import Dict, Any, Optional, List


class CacheManager:
    """统一缓存管理器，处理内存缓存"""
    
    _instance: Optional['CacheManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CacheManager, cls).__new__(cls)
                    cls._instance._init()
        return cls._instance
    
    def _init(self):
        """初始化缓存管理器"""
        self._cache: Dict[str, Any] = {
            'chats': {},
            'models': [],
            'embedding_models': [],
            'settings': {}
        }
        self._dirty_flags: Dict[str, Any] = {
            'chats': {},
            'models': False,
            'embedding_models': False,
            'settings': False
        }
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """从缓存获取数据
        
        Args:
            key: 缓存键名
            
        Returns:
            缓存的数据，如果不存在返回None
        """
        with self._lock:
            return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        """设置缓存数据
        
        Args:
            key: 缓存键名
            value: 缓存数据
            
        Returns:
            操作是否成功
        """
        try:
            with self._lock:
                self._cache[key] = value
                if key == 'chats':
                    # 对于chats键，保留之前标记为脏的对话ID（包括已删除的对话）
                    if isinstance(value, dict):
                        # 获取之前的脏标记
                        old_dirty_flags = self._dirty_flags.get(key, {})
                        # 保留所有之前标记为脏的对话ID，包括已删除的对话
                        new_dirty_flags = {}
                        for chat_id, is_dirty in old_dirty_flags.items():
                            if is_dirty:
                                new_dirty_flags[chat_id] = True
                        self._dirty_flags[key] = new_dirty_flags
                    else:
                        self._dirty_flags[key] = {}
                else:
                    self._dirty_flags[key] = True
            return True
        except Exception as e:
            print(f"设置缓存数据失败: {e}")
            return False
    
    def update(self, key: str, updates: Dict[str, Any]) -> Optional[Any]:
        """更新缓存数据
        
        Args:
            key: 缓存键名
            updates: 更新的数据字典
            
        Returns:
            更新后的数据，如果不存在返回None
        """
        try:
            with self._lock:
                existing_data = self._cache.get(key)
                if not existing_data:
                    return None
                
                # 更新现有数据
                if isinstance(existing_data, dict):
                    existing_data.update(updates)
                else:
                    for k, v in updates.items():
                        if hasattr(existing_data, k):
                            setattr(existing_data, k, v)
                
                self._dirty_flags[key] = True
                return existing_data
        except Exception as e:
            print(f"更新缓存数据失败: {e}")
            return None
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在
        
        Args:
            key: 缓存键名
            
        Returns:
            缓存是否存在
        """
        with self._lock:
            return key in self._cache and self._cache[key] is not None
    
    def set_dirty_flag(self, key: str, value: bool = True) -> None:
        """设置脏标记
        
        Args:
            key: 缓存键
            value: 是否为脏数据，默认为True
        """
        with self._lock:
            if key == 'chats':
                # 对于chats键，value为True表示所有对话都脏，设置为一个包含所有对话ID的字典
                if value:
                    chats = self._cache.get('chats', {})
                    self._dirty_flags[key] = {chat_id: True for chat_id in chats.keys()}
                else:
                    self._dirty_flags[key] = {}
            else:
                self._dirty_flags[key] = value
    
    def is_dirty(self, key: str) -> bool:
        """检查是否有脏标记
        
        Args:
            key: 缓存键
            
        Returns:
            是否有脏标记
        """
        with self._lock:
            value = self._dirty_flags.get(key, False)
            # 对于chats键，检查字典是否为空
            if key == 'chats' and isinstance(value, dict):
                return len(value) > 0
            return value
    
    def clear_dirty_flag(self, key: str) -> None:
        """清除脏标记
        
        Args:
            key: 缓存键
        """
        with self._lock:
            if key in self._dirty_flags:
                if key == 'chats':
                    self._dirty_flags[key] = {}
                else:
                    self._dirty_flags[key] = False
    
    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """获取单个对话
        
        Args:
            chat_id: 对话ID
            
        Returns:
            对话数据，如果不存在返回None
        """
        with self._lock:
            chats = self._cache.get('chats', {})
            return chats.get(chat_id)
    
    def set_chat(self, chat_id: str, chat_data: Dict[str, Any]) -> bool:
        """设置单个对话
        
        Args:
            chat_id: 对话ID
            chat_data: 对话数据
            
        Returns:
            操作是否成功
        """
        try:
            with self._lock:
                chats = self._cache.get('chats', {})
                chats[chat_id] = chat_data
                self._cache['chats'] = chats
                self._dirty_flags['chats'][chat_id] = True
            return True
        except Exception as e:
            print(f"设置对话数据失败: {e}")
            return False
    
    def update_message(self, chat_id: str, message_id: str, message_data: Dict[str, Any]) -> bool:
        """更新单条消息
        
        Args:
            chat_id: 对话ID
            message_id: 消息ID
            message_data: 消息数据
            
        Returns:
            操作是否成功
        """
        try:
            with self._lock:
                chats = self._cache.get('chats', {})
                if chat_id not in chats:
                    return False
                
                chat = chats[chat_id]
                messages = chat.get('messages', [])
                
                # 查找并更新消息
                for msg in messages:
                    if msg.get('id') == message_id:
                        msg.update(message_data)
                        self._dirty_flags['chats'][chat_id] = True
                        break
                
                chats[chat_id] = chat
                self._cache['chats'] = chats
            return True
        except Exception as e:
            print(f"更新消息数据失败: {e}")
            return False
    
    def add_message(self, chat_id: str, message_data: Dict[str, Any]) -> bool:
        """添加新消息
        
        Args:
            chat_id: 对话ID
            message_data: 消息数据
            
        Returns:
            操作是否成功
        """
        try:
            with self._lock:
                chats = self._cache.get('chats', {})
                if chat_id not in chats:
                    return False
                
                chat = chats[chat_id]
                messages = chat.get('messages', [])
                messages.append(message_data)
                chat['messages'] = messages
                
                self._dirty_flags['chats'][chat_id] = True
                
                chats[chat_id] = chat
                self._cache['chats'] = chats
            return True
        except Exception as e:
            print(f"添加消息数据失败: {e}")
            return False
    
    def update_chat_no_dirty(self, chat_id: str, chat_data: Dict[str, Any]) -> bool:
        """更新单个对话但不设置脏标记
        
        Args:
            chat_id: 对话ID
            chat_data: 对话数据
            
        Returns:
            操作是否成功
        """
        try:
            with self._lock:
                chats = self._cache.get('chats', {})
                chats[chat_id] = chat_data
                self._cache['chats'] = chats
            return True
        except Exception as e:
            print(f"更新对话数据失败: {e}")
            return False
    
    def is_chat_dirty(self, chat_id: str) -> bool:
        """检查对话是否有脏标记
        
        Args:
            chat_id: 对话ID
            
        Returns:
            是否有脏标记
        """
        with self._lock:
            return self._dirty_flags['chats'].get(chat_id, False)
    
    def clear_chat_dirty_flag(self, chat_id: str) -> None:
        """清除对话脏标记
        
        Args:
            chat_id: 对话ID
        """
        with self._lock:
            if chat_id in self._dirty_flags['chats']:
                del self._dirty_flags['chats'][chat_id]
    
    def get_dirty_chats(self) -> List[str]:
        """获取所有脏对话的ID
        
        Returns:
            脏对话ID列表
        """
        with self._lock:
            return [chat_id for chat_id, is_dirty in self._dirty_flags['chats'].items() if is_dirty]
    
    def clear(self, key: Optional[str] = None) -> bool:
        """清除缓存
        
        Args:
            key: 缓存键名，如果为None则清除所有缓存
            
        Returns:
            操作是否成功
        """
        try:
            with self._lock:
                if key:
                    if key in self._cache:
                        if key == 'chats':
                            self._cache[key] = {}
                            self._dirty_flags[key] = {}
                        elif key in ['models', 'embedding_models']:
                            self._cache[key] = []
                            self._dirty_flags[key] = False
                        elif key == 'settings':
                            self._cache[key] = {}
                            self._dirty_flags[key] = False
                        else:
                            self._cache[key] = None
                            self._dirty_flags[key] = False
                else:
                    # 重置所有缓存
                    self._cache = {
                        'chats': {},
                        'models': [],
                        'embedding_models': [],
                        'settings': {}
                    }
                    # 重置所有脏标记
                    self._dirty_flags = {
                        'chats': {},
                        'models': False,
                        'embedding_models': False,
                        'settings': False
                    }
            return True
        except Exception as e:
            print(f"清除缓存失败: {e}")
            return False

# 创建全局缓存管理器实例
cache_manager = CacheManager()