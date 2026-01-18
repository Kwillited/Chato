"""向量存储服务 - 处理嵌入模型和向量数据库的核心功能"""
import time
from typing import List, Dict, Any, Optional
from app.core.config import config_manager
from app.services.base_service import BaseService
from app.services.vector.vector_db_service import VectorDBService

class VectorStoreService(BaseService):
    """向量存储服务类 - 作为向量数据库服务的上层包装，处理缓存等高级功能"""
    
    # 类级别的缓存设置
    _CACHE_SIZE = 100  # 缓存大小限制
    _CACHE_TTL = 3600  # 缓存过期时间（秒）
    
    # 单例实例
    _instance = None
    _lock = None  # 用于线程安全的单例实现
    
    def __init__(self, vector_db_path=None, embedder_model='all-MiniLM-L6-v2'):
        """初始化向量存储服务
        
        Args:
            vector_db_path: 向量数据库的存储路径
            embedder_model: 使用的嵌入模型名称
        """
        # 初始化向量数据库服务（位于数据层）
        self.vector_db_service = VectorDBService.get_instance(vector_db_path, embedder_model)
        
        # 初始化查询缓存
        self._query_cache = {}  # 缓存字典：key为查询特征，value为(结果, 时间戳)
    
    @property
    def vector_db_service(self):
        """获取向量数据库服务实例"""
        return self._vector_db_service
    
    @vector_db_service.setter
    def vector_db_service(self, value):
        """设置向量数据库服务实例"""
        self._vector_db_service = value
    
    @property
    def vector_store(self):
        """获取向量存储实例（通过向量数据库服务）"""
        return self.vector_db_service.vector_store
    
    @classmethod
    def get_instance(cls, vector_db_path=None, embedder_model='all-MiniLM-L6-v2'):
        """获取单例实例
        
        Args:
            vector_db_path: 向量数据库的存储路径
            embedder_model: 使用的嵌入模型名称
            
        Returns:
            VectorStoreService: 向量存储服务单例实例
        """
        # 延迟初始化锁，避免导入时的循环依赖
        if cls._lock is None:
            import threading
            cls._lock = threading.Lock()
        
        # 双重检查锁定模式 - 线程安全的单例实现
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(vector_db_path, embedder_model)
        return cls._instance
    
    def add_documents(self, documents: List[Any]) -> bool:
        """将文档片段添加到向量库中
        
        Args:
            documents: 文档片段列表
            
        Returns:
            bool: 是否成功添加
        """
        # 使用向量数据库服务添加文档
        return self.vector_db_service.add_documents(documents)
    
    def clear_vector_store(self) -> bool:
        """清空向量库
        
        Returns:
            bool: 是否成功清空
        """
        # 使用向量数据库服务清空向量库
        return self.vector_db_service.clear_vector_store()
    
    def get_vector_statistics(self) -> Dict[str, Any]:
        """获取向量库统计信息
        
        Returns:
            dict: 向量库统计信息
        """
        # 使用向量数据库服务获取统计信息
        return self.vector_db_service.get_vector_statistics()
    
    def _update_cache(self, cache_key: str, result: List[Any], current_time: float) -> None:
        """更新查询缓存
        
        Args:
            cache_key: 缓存键
            result: 搜索结果
            current_time: 当前时间戳
        """
        # 添加新的缓存项
        self._query_cache[cache_key] = (result, current_time)
        
        # 如果缓存大小超过限制，移除最旧的缓存项
        if len(self._query_cache) > self._CACHE_SIZE:
            # 找到最旧的缓存项
            oldest_key = min(self._query_cache.keys(), 
                           key=lambda k: self._query_cache[k][1])
            # 移除最旧的缓存项
            del self._query_cache[oldest_key]
            self.log_debug(f"缓存大小超过限制，移除最旧项: {oldest_key[:50]}...")
    
    def search_documents(self, query: str, k: int = 5, score_threshold: Optional[float] = None, search_type: str = "similarity", fetch_k: int = 20) -> List[Any]:
        """搜索相关文档 - 支持多种搜索类型
        
        Args:
            query: 查询文本
            k: 返回结果数量
            score_threshold: 相似度分数阈值，低于该阈值的结果将被过滤
            search_type: 搜索类型，可选值：similarity, mmr, similarity_score_threshold
            fetch_k: 用于MMR搜索的候选文档数量
            
        Returns:
            list: 相关文档列表
        """
        import time
        
        try:
            # 构建缓存键：包含所有搜索参数
            cache_key = f"{query}:{k}:{score_threshold}:{search_type}:{fetch_k}"
            current_time = time.time()
            
            # 检查缓存
            if cache_key in self._query_cache:
                cached_result, cache_time = self._query_cache[cache_key]
                # 检查缓存是否过期
                if current_time - cache_time < self._CACHE_TTL:
                    self.log_debug(f"查询缓存命中: {query[:50]}...")
                    return cached_result
                else:
                    # 缓存过期，移除
                    del self._query_cache[cache_key]
                    self.log_debug(f"查询缓存过期: {query[:50]}...")
            
            # 使用向量数据库服务搜索文档
            result = self.vector_db_service.search_documents(
                query=query,
                k=k,
                score_threshold=score_threshold,
                search_type=search_type,
                fetch_k=fetch_k
            )
            
            # 更新缓存
            self._update_cache(cache_key, result, current_time)
            
            return result
        except Exception as e:
            self.log_error(f"搜索文档失败: {str(e)}")
            self.log_error(f"错误类型: {type(e).__name__}")
            import traceback
            self.log_error(f"错误堆栈: {traceback.format_exc()}")
            return []
