"""统一实例管理器 - 管理所有类型的实例"""
from typing import Dict, Any, Optional, Callable, TypeVar, Generic
from collections import OrderedDict
import json
import threading

T = TypeVar('T')

class InstanceManager(Generic[T]):
    """统一实例管理器"""
    
    _instance = None
    _instance_locks = {}  # 每种类型的实例锁
    _caches = {}  # 每种类型的实例缓存
    _cache_strategies = {}  # 每种类型的缓存策略
    _cache_sizes = {}  # 每种类型的缓存大小限制
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(InstanceManager, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        """初始化实例管理器"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        # 注册默认实例类型
        self.register_default_types()
    
    def register_default_types(self):
        """注册默认实例类型"""
        self.register_type('llm', 'unbounded', 20)
        self.register_type('embedding', 'lru', 10)
        self.register_type('mcp', 'unbounded', 5)
    
    def register_type(self, instance_type: str, cache_strategy: str = 'unbounded', cache_size: int = 10):
        """注册实例类型和缓存策略
        
        Args:
            instance_type: 实例类型（如 'llm', 'embedding', 'mcp'）
            cache_strategy: 缓存策略（'unbounded', 'lru'）
            cache_size: 缓存大小限制（仅对 'lru' 策略有效）
        """
        InstanceManager._instance_locks[instance_type] = threading.Lock()
        InstanceManager._caches[instance_type] = OrderedDict() if cache_strategy == 'lru' else {}
        InstanceManager._cache_strategies[instance_type] = cache_strategy
        InstanceManager._cache_sizes[instance_type] = cache_size
        print(f"[InstanceManager] 已注册实例类型: {instance_type}, 缓存策略: {cache_strategy}, 缓存大小: {cache_size}")
    
    @classmethod
    def get_instance(cls, instance_type: str, key: str, create_func: Callable[[], T]) -> T:
        """获取实例，如果不存在则创建
        
        Args:
            instance_type: 实例类型
            key: 实例缓存键
            create_func: 创建实例的函数
            
        Returns:
            实例对象
        """
        # 确保实例类型已注册
        if instance_type not in cls._instance_locks:
            cls._instance_locks[instance_type] = threading.Lock()
            cls._caches[instance_type] = {}
            cls._cache_strategies[instance_type] = 'unbounded'
            cls._cache_sizes[instance_type] = 10
            print(f"[InstanceManager] 自动注册实例类型: {instance_type}")
        
        with cls._instance_locks[instance_type]:
            # 检查缓存中是否存在
            if key in cls._caches[instance_type]:
                # 对于 LRU 策略，将实例移到缓存末尾
                if cls._cache_strategies[instance_type] == 'lru':
                    instance = cls._caches[instance_type].pop(key)
                    cls._caches[instance_type][key] = instance
                    print(f"[InstanceManager] 从 LRU 缓存加载实例: {instance_type}, 键: {key[:50]}...")
                else:
                    instance = cls._caches[instance_type][key]
                    print(f"[InstanceManager] 从缓存加载实例: {instance_type}, 键: {key[:50]}...")
                return instance
            
            # 缓存未命中，创建新实例
            print(f"[InstanceManager] 创建新实例: {instance_type}, 键: {key[:50]}...")
            instance = create_func()
            
            # 添加到缓存
            if cls._cache_strategies[instance_type] == 'lru':
                # 检查缓存大小
                if len(cls._caches[instance_type]) >= cls._cache_sizes[instance_type]:
                    # 移除最旧的实例
                    oldest_key, _ = cls._caches[instance_type].popitem(last=False)
                    print(f"[InstanceManager] 缓存已满，移除最旧实例: {instance_type}, 键: {oldest_key[:50]}...")
                # 添加新实例到缓存末尾
                cls._caches[instance_type][key] = instance
                print(f"[InstanceManager] 实例已添加到 LRU 缓存: {instance_type}, 键: {key[:50]}...")
            else:
                # 无界缓存，直接添加
                cls._caches[instance_type][key] = instance
                print(f"[InstanceManager] 实例已添加到缓存: {instance_type}, 键: {key[:50]}...")
            
            # 打印当前缓存状态
            cache_size = len(cls._caches[instance_type])
            print(f"[InstanceManager] 当前 {instance_type} 缓存大小: {cache_size}")
            return instance
    
    @classmethod
    def clear_cache(cls, instance_type: str = None):
        """清空缓存
        
        Args:
            instance_type: 实例类型，如果为 None，则清空所有类型的缓存
        """
        if instance_type:
            if instance_type in cls._instance_locks:
                with cls._instance_locks[instance_type]:
                    cache_size = len(cls._caches[instance_type])
                    cls._caches[instance_type].clear()
                    print(f"[InstanceManager] 已清空 {instance_type} 类型的缓存，共 {cache_size} 个实例")
        else:
            # 清空所有类型的缓存
            for inst_type in cls._instance_locks:
                with cls._instance_locks[inst_type]:
                    cache_size = len(cls._caches[inst_type])
                    cls._caches[inst_type].clear()
                    print(f"[InstanceManager] 已清空 {inst_type} 类型的缓存，共 {cache_size} 个实例")
    
    @classmethod
    def get_cache_size(cls, instance_type: str = None) -> Dict[str, int]:
        """获取缓存大小
        
        Args:
            instance_type: 实例类型，如果为 None，则返回所有类型的缓存大小
            
        Returns:
            缓存大小字典
        """
        if instance_type:
            size = len(cls._caches.get(instance_type, {}))
            print(f"[InstanceManager] {instance_type} 缓存大小: {size}")
            return {instance_type: size}
        else:
            sizes = {inst_type: len(cls._caches.get(inst_type, {})) for inst_type in cls._instance_locks}
            print(f"[InstanceManager] 所有类型缓存大小: {sizes}")
            return sizes


# 创建全局实例
instance_manager = InstanceManager()
