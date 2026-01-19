"""向量数据库Repository类 - 封装向量数据库的所有操作"""
from typing import List, Dict, Any, Optional
from app.repositories.base_repository import BaseRepository

class VectorRepository(BaseRepository):
    """向量数据库Repository类，封装所有向量数据库相关的操作"""
    
    def __init__(self, vector_store=None):
        """初始化向量数据库Repository
        
        Args:
            vector_store: 向量存储实例，用于依赖注入
        """
        # 不调用父类的SQLAlchemy会话初始化，因为向量数据库不需要SQLite会话
        self.vector_store = vector_store
    
    def add_documents(self, documents: List[Any]) -> bool:
        """将文档片段添加到向量库中
        
        Args:
            documents: 文档片段列表
            
        Returns:
            bool: 是否成功添加
        """
        try:
            if not self.vector_store:
                raise ValueError("向量存储未初始化")
            
            # 将文档片段添加到向量库
            self.vector_store.add_documents(documents)
            return True
        except Exception as e:
            raise e
    
    def clear_vector_store(self) -> bool:
        """清空向量库
        
        Returns:
            bool: 是否成功清空
        """
        try:
            if not self.vector_store:
                raise ValueError("向量存储未初始化")
            
            # 获取集合并清空
            if hasattr(self.vector_store, '_collection'):
                try:
                    # 尝试使用不同的方式清空集合
                    # 方法1: 尝试删除所有文档，不指定where条件
                    self.vector_store._collection.delete()
                    return True
                except Exception as e1:
                    try:
                        # 方法2: 使用更明确的删除方式
                        # 获取所有文档ID然后删除
                        all_ids = self.vector_store._collection.get()['ids']
                        if all_ids:
                            self.vector_store._collection.delete(ids=all_ids)
                        return True
                    except Exception as e2:
                        # 备选方案：重新初始化向量存储
                        raise ValueError(f"尝试清空集合失败: {e1}, {e2}")
            else:
                # 备选方案：重新初始化向量存储
                raise ValueError("向量存储不支持直接清空操作")
        except Exception as e:
            raise e
    
    def get_vector_count(self) -> int:
        """获取向量数量
        
        Returns:
            int: 向量数量
        """
        try:
            if not self.vector_store:
                raise ValueError("向量存储未初始化")
            
            # 尝试获取向量数量
            if hasattr(self.vector_store, '_collection'):
                return self.vector_store._collection.count()
            return 0
        except Exception as e:
            raise e
    
    def search_documents(self, query: str, k: int = 5, score_threshold: Optional[float] = None, 
                        search_type: str = "similarity", fetch_k: int = 20, 
                        filter: Optional[Dict[str, Any]] = None) -> List[Any]:
        """搜索相关文档 - 支持多种搜索类型
        
        Args:
            query: 查询文本
            k: 返回结果数量
            score_threshold: 相似度分数阈值，低于该阈值的结果将被过滤
            search_type: 搜索类型，可选值：similarity, mmr, similarity_score_threshold
            fetch_k: 用于MMR搜索的候选文档数量
            filter: 元数据过滤器，用于过滤特定条件的文档，格式为 {"key": "value"} 或 {"$and": [{"key1": "value1"}, {"key2": "value2"}]}
            
        Returns:
            list: 相关文档列表
        """
        try:
            if not self.vector_store:
                raise ValueError("向量存储未初始化")
            
            result = []
            
            # 处理过滤器，转换为Chroma支持的格式
            chroma_filter = None
            if filter:
                # 如果filter是简单的键值对，并且包含多个键，则转换为$and格式
                if isinstance(filter, dict) and len(filter) > 1 and all(isinstance(v, (str, int, float, bool)) for v in filter.values()):
                    # 转换为$and格式
                    chroma_filter = {"$and": [{k: v} for k, v in filter.items()]}
                else:
                    # 单条件或已经是正确格式，直接使用
                    chroma_filter = filter
            
            # 根据搜索类型执行不同的搜索方法
            if search_type == "mmr":
                # 使用最大边缘相关性搜索
                result = self.vector_store.max_marginal_relevance_search(
                    query=query,
                    k=k,
                    fetch_k=fetch_k,
                    filter=chroma_filter  # 添加元数据过滤
                )
            elif search_type == "similarity_score_threshold" and score_threshold is not None:
                # 使用带分数阈值的相似性搜索
                result = self.vector_store.similarity_search_with_score(
                    query=query,
                    k=k,
                    score_threshold=score_threshold,
                    filter=chroma_filter  # 添加元数据过滤
                )
                # 只保留文档，不保留分数
                result = [doc for doc, _ in result]
            elif score_threshold is not None:
                # 执行带分数的相似性搜索并手动过滤
                results_with_scores = self.vector_store.similarity_search_with_score(
                    query=query, 
                    k=k,
                    filter=chroma_filter  # 添加元数据过滤
                )
                
                # 过滤结果
                result = []
                for doc, score in results_with_scores:
                    if score <= score_threshold:
                        result.append(doc)
            else:
                # 执行普通相似性搜索
                result = self.vector_store.similarity_search(
                    query=query, 
                    k=k,
                    filter=chroma_filter  # 添加元数据过滤
                )
            
            return result
        except Exception as e:
            raise e
    
    def set_vector_store(self, vector_store):
        """设置向量存储实例
        
        Args:
            vector_store: 向量存储实例
        """
        self.vector_store = vector_store
    
    def get_vector_store(self):
        """获取向量存储实例
        
        Returns:
            向量存储实例
        """
        return self.vector_store
