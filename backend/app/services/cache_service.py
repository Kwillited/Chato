"""缓存管理服务"""
import threading
from typing import Dict, List, Any, Optional

class CacheManager:
    """缓存管理器，处理内存缓存与数据库的同步"""
    
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
        self._dirty_flags: Dict[str, bool] = {}
        self._cache: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def get_cache(self, key: str) -> Any:
        """获取缓存数据"""
        with self._lock:
            return self._cache.get(key)
    
    def set_cache(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        with self._lock:
            self._cache[key] = value
    
    def clear_cache(self, key: str) -> None:
        """清除指定缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def set_dirty_flag(self, key: str, value: bool = True) -> None:
        """设置脏标记"""
        with self._lock:
            self._dirty_flags[key] = value
    
    def is_dirty(self, key: str) -> bool:
        """检查是否有脏标记"""
        with self._lock:
            return self._dirty_flags.get(key, False)
    
    def clear_dirty_flag(self, key: str) -> None:
        """清除脏标记"""
        with self._lock:
            if key in self._dirty_flags:
                del self._dirty_flags[key]
    
    def sync_cache_to_db(self, key: str, sync_func) -> bool:
        """同步缓存到数据库
        
        Args:
            key: 缓存键
            sync_func: 同步函数，负责将缓存数据写入数据库
        
        Returns:
            bool: 同步是否成功
        """
        with self._lock:
            if not self.is_dirty(key):
                return True
            
            try:
                # 执行同步函数
                success = sync_func()
                if success:
                    self.clear_dirty_flag(key)
                return success
            except Exception as e:
                # 记录错误
                from app.core.logging_config import logger
                logger.error(f"同步缓存到数据库失败: {e}")
                return False
    
    def batch_sync(self, sync_tasks: List[Dict[str, Any]]) -> Dict[str, bool]:
        """批量同步缓存到数据库
        
        Args:
            sync_tasks: 同步任务列表，每个任务包含 'key' 和 'sync_func'
        
        Returns:
            Dict[str, bool]: 每个任务的同步结果
        """
        results = {}
        for task in sync_tasks:
            key = task.get('key')
            sync_func = task.get('sync_func')
            if key and sync_func:
                results[key] = self.sync_cache_to_db(key, sync_func)
        return results

# 创建全局缓存管理器实例
cache_manager = CacheManager()
