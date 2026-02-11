"""内存缓存管理类"""
from typing import Dict, Any, Optional, List


class MemoryCache:
    """内存缓存管理类，负责管理内存中的数据"""
    
    def __init__(self):
        """初始化内存缓存"""
        self._cache = {
            'system_settings': None,
            'vector_settings': None,
            'chats': []
        }
    
    def get(self, key: str) -> Optional[Any]:
        """从内存缓存获取数据
        
        Args:
            key: 缓存键名
            
        Returns:
            缓存的数据，如果不存在返回None
        """
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        """设置内存缓存数据
        
        Args:
            key: 缓存键名
            value: 缓存数据
            
        Returns:
            操作是否成功
        """
        try:
            self._cache[key] = value
            return True
        except Exception as e:
            print(f"设置内存缓存数据失败: {e}")
            return False
    
    def update(self, key: str, updates: Dict[str, Any]) -> Optional[Any]:
        """更新内存缓存数据
        
        Args:
            key: 缓存键名
            updates: 更新的数据字典
            
        Returns:
            更新后的数据，如果不存在返回None
        """
        try:
            existing_data = self._cache.get(key)
            if not existing_data:
                return None
            
            # 更新现有数据
            for k, v in updates.items():
                if hasattr(existing_data, k):
                    setattr(existing_data, k, v)
            
            return existing_data
        except Exception as e:
            print(f"更新内存缓存数据失败: {e}")
            return None
    
    def clear(self, key: Optional[str] = None) -> bool:
        """清除内存缓存
        
        Args:
            key: 缓存键名，如果为None则清除所有缓存
            
        Returns:
            操作是否成功
        """
        try:
            if key:
                if key in self._cache:
                    self._cache[key] = None
            else:
                # 重置所有缓存
                self._cache = {
                    'system_settings': None,
                    'vector_settings': None,
                    'chats': []
                }
            return True
        except Exception as e:
            print(f"清除内存缓存失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在
        
        Args:
            key: 缓存键名
            
        Returns:
            缓存是否存在
        """
        return key in self._cache and self._cache[key] is not None
