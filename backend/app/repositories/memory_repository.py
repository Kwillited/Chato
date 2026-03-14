"""内存数据操作Repository"""
from typing import Optional, Any, List
from app.core.cache import cache_manager
from app.core.data_manager import save_data, get_data
from app.repositories.base_repository import BaseRepository


class MemoryRepository(BaseRepository):
    """内存数据操作Repository，负责内存数据管理和脏标记机制"""
    
    def get_data(self, key: str) -> Optional[Any]:
        """从内存获取数据
        
        Args:
            key: 数据键名
            
        Returns:
            内存中的数据，如果不存在返回None
        """
        return get_data(key)
    
    def set_data(self, key: str, value: Any) -> bool:
        """设置内存数据
        
        Args:
            key: 数据键名
            value: 数据值
            
        Returns:
            操作是否成功
        """
        try:
            # 先更新缓存
            cache_manager.set(key, value)
            return True
        except Exception as e:
            print(f"设置内存数据失败: {e}")
            return False
    
    def save_data(self) -> bool:
        """保存内存数据到持久化存储
        
        Returns:
            操作是否成功
        """
        try:
            save_data()
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False
    
    def set_dirty_flag(self, data_type: str, is_dirty: bool = True) -> None:
        """设置脏标记
        
        Args:
            data_type: 数据类型
            is_dirty: 是否为脏数据，默认为True
        """
        cache_manager.set_dirty_flag(data_type, is_dirty)
    
    def is_dirty(self, data_type: str) -> bool:
        """检查数据是否有脏标记
        
        Args:
            data_type: 数据类型
            
        Returns:
            是否有脏标记
        """
        return cache_manager.is_dirty(data_type)
    
    def clear_dirty_flag(self, data_type: str) -> None:
        """清除脏标记
        
        Args:
            data_type: 数据类型
        """
        cache_manager.clear_dirty_flag(data_type)
    
    def get_dirty_chats(self) -> List[str]:
        """获取所有脏对话的ID
        
        Returns:
            脏对话ID列表
        """
        return cache_manager.get_dirty_chats()
    
    def clear_data(self, key: Optional[str] = None) -> bool:
        """清除内存数据
        
        Args:
            key: 数据键名，如果为None则清除所有数据
            
        Returns:
            操作是否成功
        """
        return cache_manager.clear(key)
