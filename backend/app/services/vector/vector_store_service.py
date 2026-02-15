"""向量存储服务 - 处理嵌入模型和向量数据库的核心功能"""
import time
import threading
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import config_manager
from app.services.base_service import BaseService
from app.services.vector.vector_db_service import VectorDBService

class VectorStoreService(BaseService):
    """向量存储服务类 - 作为向量数据库服务的上层包装，处理缓存等高级功能"""
    
    # 类级别的缓存设置
    _CACHE_SIZE = 100  # 缓存大小限制
    _CACHE_TTL = 3600  # 缓存过期时间（秒）
    
    # 单例实例字典，按知识库名称区分
    _instances = {}
    _lock = threading.Lock()
    
    def __new__(cls, vector_db_path=None, embedder_model=None, knowledge_base_name=None):
        """单例模式实现，按知识库名称区分实例"""
        from app.core.data_manager import db
        knowledge_base_name = knowledge_base_name or "default"
        
        # 如果未提供嵌入模型名称，从db['settings']获取
        if not embedder_model:
            embedder_model = db['settings'].get('vector', {}).get('embedder_model', 'qwen3-embedding-0.6b')
        
        with cls._lock:
            if knowledge_base_name not in cls._instances:
                cls._instances[knowledge_base_name] = super(VectorStoreService, cls).__new__(cls)
                cls._instances[knowledge_base_name].__init__(vector_db_path, embedder_model, knowledge_base_name)
        return cls._instances[knowledge_base_name]
    
    def __init__(self, vector_db_path=None, embedder_model=None, knowledge_base_name=None):
        """初始化向量存储服务
        
        Args:
            vector_db_path: 向量数据库的存储路径
            embedder_model: 使用的嵌入模型名称
            knowledge_base_name: 知识库名称，用于标识不同的知识库实例
        """
        from app.core.data_manager import db
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # 设置知识库名称
        self.knowledge_base_name = knowledge_base_name or "default"
        
        # 如果未提供嵌入模型名称，从db['settings']获取
        if not embedder_model:
            embedder_model = db['settings'].get('vector', {}).get('embedder_model', 'qwen3-embedding-0.6b')
        
        # 初始化向量数据库服务（位于数据层）
        self.vector_db_service = VectorDBService(vector_db_path, embedder_model, self.knowledge_base_name)
        
        # 初始化查询缓存
        self._query_cache = {}  # 缓存字典：key为查询特征，value为(结果, 时间戳)
        
        self.log_info(f"初始化向量存储服务: 知识库='{self.knowledge_base_name}'")
        self._initialized = True
    
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
    
    def add_documents(self, documents: List[Any]) -> Tuple[bool, str]:
        """将文档片段添加到向量库中
        
        Args:
            documents: 文档片段列表
            
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息或"success")
        """
        try:
            if not documents:
                return False, "没有找到文档或文档为空"
            
            self.log_info(f"[{self.knowledge_base_name}] 开始添加文档: 数量={len(documents)}")
            result = self.vector_db_service.add_documents(documents)
            if result:
                self.log_info(f"[{self.knowledge_base_name}] 成功添加 {len(documents)} 个文档")
                return True, "success"
            else:
                error_msg = f"添加文档失败"
                self.log_warning(f"[{self.knowledge_base_name}] {error_msg}")
                return False, error_msg
        except Exception as e:
            error_msg = f"添加文档异常: {str(e)}"
            self.log_error(f"[{self.knowledge_base_name}] {error_msg}")
            return False, error_msg
    
    def clear_vector_store(self) -> Tuple[bool, str]:
        """清空向量库
        
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息或"success")
        """
        try:
            self.log_info(f"[{self.knowledge_base_name}] 开始清空向量库")
            result = self.vector_db_service.clear_vector_store()
            if result:
                self.log_info(f"[{self.knowledge_base_name}] 向量库清空成功")
                # 清空缓存
                self._query_cache.clear()
                self.log_info(f"[{self.knowledge_base_name}] 已清空查询缓存")
                return True, "success"
            else:
                error_msg = "向量库清空失败"
                self.log_warning(f"[{self.knowledge_base_name}] {error_msg}")
                return False, error_msg
        except Exception as e:
            error_msg = f"清空向量库异常: {str(e)}"
            self.log_error(f"[{self.knowledge_base_name}] {error_msg}")
            return False, error_msg
    
    def reload_vector_store(self) -> Tuple[bool, str]:
        """重新加载向量库
        
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息或"success")
        """
        try:
            self.log_info(f"[{self.knowledge_base_name}] 开始重新加载向量库")
            
            # 清空查询缓存
            self._query_cache.clear()
            self.log_info(f"[{self.knowledge_base_name}] 已清空查询缓存")
            
            # 重新初始化向量数据库服务
            from app.services.vector.vector_db_service import VectorDBService
            self._vector_db_service = VectorDBService(None, None, self.knowledge_base_name)
            self.log_info(f"[{self.knowledge_base_name}] 已重新初始化向量数据库服务")
            
            return True, "向量库重新加载成功"
        except Exception as e:
            error_msg = f"重新加载向量库异常: {str(e)}"
            self.log_error(f"[{self.knowledge_base_name}] {error_msg}")
            return False, error_msg
    
    def get_vector_statistics(self) -> Dict[str, Any]:
        """获取向量库统计信息
        
        Returns:
            dict: 向量库统计信息
        """
        try:
            stats = self.vector_db_service.get_vector_statistics()
            # 添加知识库名称到统计信息
            stats['knowledge_base'] = self.knowledge_base_name
            self.log_info(f"[{self.knowledge_base_name}] 获取向量库统计信息: {stats}")
            return stats
        except Exception as e:
            self.log_error(f"[{self.knowledge_base_name}] 获取向量库统计信息异常: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'total_vectors': 0,
                'knowledge_base': self.knowledge_base_name
            }
    
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
    
    def search_documents(self, query: str, k: int = 5, score_threshold: Optional[float] = None, search_type: str = "similarity", fetch_k: int = 20, filter: Optional[Dict[str, Any]] = None) -> List[Any]:
        """搜索相关文档 - 支持多种搜索类型
        
        Args:
            query: 查询文本
            k: 返回结果数量
            score_threshold: 相似度分数阈值，低于该阈值的结果将被过滤
            search_type: 搜索类型，可选值：similarity, mmr, similarity_score_threshold
            fetch_k: 用于MMR搜索的候选文档数量
            filter: 元数据过滤器，用于过滤特定条件的文档，格式为 {"key": "value"}
            
        Returns:
            list: 相关文档列表
        """
        import time
        import json
        
        try:
            # 构建缓存键：包含所有搜索参数，包括filter
            # 将filter转换为JSON字符串以确保唯一性
            filter_str = json.dumps(filter, sort_keys=True) if filter else "None"
            cache_key = f"{query}:{k}:{score_threshold}:{search_type}:{fetch_k}:{filter_str}"
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
                fetch_k=fetch_k,
                filter=filter
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