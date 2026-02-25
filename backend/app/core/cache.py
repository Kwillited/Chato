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
            'chats': [],
            'models': [],
            'embedding_models': [],
            'settings': {},
            'agent_sessions': []
        }
        self._dirty_flags: Dict[str, bool] = {
            'chats': False,
            'models': False,
            'embedding_models': False,
            'settings': False,
            'agent_sessions': False
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
                        if key in ['chats', 'models', 'embedding_models', 'agent_sessions']:
                            self._cache[key] = []
                        elif key == 'settings':
                            self._cache[key] = {}
                        else:
                            self._cache[key] = None
                        self._dirty_flags[key] = True
                else:
                    # 重置所有缓存
                    self._cache = {
                        'chats': [],
                        'models': [],
                        'embedding_models': [],
                        'settings': {},
                        'agent_sessions': []
                    }
                    # 重置所有脏标记
                    for k in self._dirty_flags:
                        self._dirty_flags[k] = True
            return True
        except Exception as e:
            print(f"清除缓存失败: {e}")
            return False
    
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
            self._dirty_flags[key] = value
    
    def is_dirty(self, key: str) -> bool:
        """检查是否有脏标记
        
        Args:
            key: 缓存键
            
        Returns:
            是否有脏标记
        """
        with self._lock:
            return self._dirty_flags.get(key, False)
    
    def clear_dirty_flag(self, key: str) -> None:
        """清除脏标记
        
        Args:
            key: 缓存键
        """
        with self._lock:
            if key in self._dirty_flags:
                self._dirty_flags[key] = False
    
# 创建全局缓存管理器实例
cache_manager = CacheManager()