"""向量数据库Repository类 - 封装向量数据库的所有操作"""
from typing import List, Dict, Any, Optional, Tuple
from app.repositories.base_repository import BaseRepository
from langchain_core.vectorstores import VectorStore

class VectorRepository(BaseRepository):
    """向量数据库Repository类，封装所有向量数据库相关的操作"""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """初始化向量数据库Repository
        
        Args:
            vector_store: 向量存储实例，用于依赖注入
        """
        # 不调用父类的SQLAlchemy会话初始化，因为向量数据库不需要SQLite会话
        self._vector_store: Optional[VectorStore] = vector_store
    
    @property
    def vector_store(self) -> Optional[VectorStore]:
        """获取向量存储实例
        
        Returns:
            Optional[VectorStore]: 向量存储实例
        """
        return self._vector_store
    
    @vector_store.setter
    def vector_store(self, vector_store: Optional[VectorStore]) -> None:
        """设置向量存储实例
        
        Args:
            vector_store: 向量存储实例
        """
        self._vector_store = vector_store
    
    def add_documents(self, documents: List[Any]) -> bool:
        """将文档片段添加到向量库中
        
        Args:
            documents: 文档片段列表
            
        Returns:
            bool: 是否成功添加
        """
        try:
            if not self._vector_store:
                raise ValueError("向量存储未初始化")
            
            # 将文档片段添加到向量库
            self._vector_store.add_documents(documents)
            return True
        except Exception as e:
            raise e
    
    def clear_vector_store(self) -> bool:
        """清空向量库
        
        Returns:
            bool: 是否成功清空
        """
        try:
            if not self._vector_store:
                raise ValueError("向量存储未初始化")
            
            # 获取集合并清空
            if hasattr(self._vector_store, '_collection'):
                try:
                    # 尝试使用不同的方式清空集合
                    # 方法1: 尝试删除所有文档，不指定where条件
                    self._vector_store._collection.delete()
                    return True
                except Exception as e1:
                    try:
                        # 方法2: 使用更明确的删除方式
                        # 获取所有文档ID然后删除
                        all_ids = self._vector_store._collection.get()['ids']
                        if all_ids:
                            self._vector_store._collection.delete(ids=all_ids)
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
            if not self._vector_store:
                raise ValueError("向量存储未初始化")
            
            # 尝试获取向量数量
            if hasattr(self._vector_store, '_collection'):
                return self._vector_store._collection.count()
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
            List[Any]: 相关文档列表
        """
        try:
            if not self._vector_store:
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
                result = self._vector_store.max_marginal_relevance_search(
                    query=query,
                    k=k,
                    fetch_k=fetch_k,
                    filter=chroma_filter  # 添加元数据过滤
                )
            elif search_type == "similarity_score_threshold" and score_threshold is not None:
                # 使用带分数阈值的相似性搜索
                result = self._vector_store.similarity_search_with_score(
                    query=query,
                    k=k,
                    score_threshold=score_threshold,
                    filter=chroma_filter  # 添加元数据过滤
                )
                # 只保留文档，不保留分数
                result = [doc for doc, _ in result]
            elif score_threshold is not None:
                # 执行带分数的相似性搜索并手动过滤
                results_with_scores = self._vector_store.similarity_search_with_score(
                    query=query, 
                    k=k,
                    filter=chroma_filter  # 添加元数据过滤
                )
                
                # 过滤结果
                result = []
                for doc, score in results_with_scores:
                    # 注意：Chroma返回的是距离分数，距离越小表示相似度越高
                    # 所以应该保留距离小于等于阈值的结果
                    if score <= score_threshold:
                        result.append(doc)
            else:
                # 执行普通相似性搜索
                result = self._vector_store.similarity_search(
                    query=query, 
                    k=k,
                    filter=chroma_filter  # 添加元数据过滤
                )
            
            return result
        except Exception as e:
            raise e
    
    def set_vector_store(self, vector_store: Optional[VectorStore]) -> None:
        """设置向量存储实例
        
        Args:
            vector_store: 向量存储实例
        """
        self._vector_store = vector_store
    
    def get_vector_store(self) -> Optional[VectorStore]:
        """获取向量存储实例
        
        Returns:
            Optional[VectorStore]: 向量存储实例
        """
        return self._vector_store
    
    def embed_document(self, doc_content: str, metadata: dict):
        """将文档内容转换为向量表示
        
        Args:
            doc_content (str): 文档内容
            metadata (dict): 文档元数据
            
        Returns:
            dict: 向量化结果
        """
        try:
            if not self._vector_store:
                raise ValueError("向量存储未初始化")
            
            # 导入文档分块工具
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            # 文档分块
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.create_documents([doc_content])
            
            # 为每个分块添加元数据
            for chunk in chunks:
                chunk.metadata.update(metadata)
            
            # 向量化并存储
            self._vector_store.add_documents(chunks)
            
            return {
                'success': True,
                'chunk_count': len(chunks),
                'chunks': chunks
            }
        except Exception as e:
            raise e
    
    def search_vectors(self, query: str, k: int = 5, filter: dict = None, score_threshold: float = None):
        """根据查询向量检索相关文档
        
        Args:
            query (str): 查询文本
            k (int): 返回结果数量
            filter (dict): 过滤条件
            score_threshold (float): 相似度分数阈值，低于该阈值的结果将被过滤
            
        Returns:
            dict: 向量检索结果
        """
        try:
            if not self._vector_store:
                raise ValueError("向量存储未初始化")
            
            if score_threshold is not None:
                # 执行带分数的相似性搜索并手动过滤
                results_with_scores = self._vector_store.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter
                )
                
                # 过滤结果
                # 注意：Chroma返回的是距离分数，距离越小表示相似度越高
                # 所以应该保留距离小于等于阈值的结果
                filtered_results = []
                for doc, score in results_with_scores:
                    if score <= score_threshold:
                        filtered_results.append(doc)
                
                return {
                    'success': True,
                    'results': filtered_results,
                    'result_count': len(filtered_results)
                }
            else:
                # 执行普通相似性搜索
                results = self._vector_store.similarity_search(
                    query=query,
                    k=k,
                    filter=filter
                )
                
                return {
                    'success': True,
                    'results': results,
                    'result_count': len(results)
                }
        except Exception as e:
            raise e
    
    def get_vector_store_stats(self):
        """获取向量存储统计信息
        
        Returns:
            dict: 向量存储统计信息
        """
        try:
            if not self._vector_store:
                raise ValueError("向量存储未初始化")
            
            stats = {}
            
            # 获取向量数量
            if hasattr(self._vector_store, '_collection'):
                stats['vector_count'] = self._vector_store._collection.count()
                
                # 获取集合名称
                if hasattr(self._vector_store._collection, 'name'):
                    stats['collection_name'] = self._vector_store._collection.name
            
            # 获取向量存储类型
            stats['vector_store_type'] = str(type(self._vector_store).__name__)
            
            return stats
        except Exception as e:
            raise e
    
    def delete_vectors_by_document_id(self, document_id: str):
        """根据文档ID删除相关向量
        
        Args:
            document_id (str): 文档ID
            
        Returns:
            dict: 删除结果
        """
        try:
            if not self._vector_store:
                raise ValueError("向量存储未初始化")
            
            # 使用过滤器删除指定文档的向量
            if hasattr(self._vector_store, '_collection'):
                # 获取所有匹配的向量ID
                result = self._vector_store._collection.get(
                    where={'document_id': document_id}
                )
                
                if result and result.get('ids'):
                    ids_to_delete = result['ids']
                    # 删除匹配的向量
                    self._vector_store._collection.delete(ids=ids_to_delete)
                    return {
                        'success': True,
                        'deleted_count': len(ids_to_delete)
                    }
                
            return {
                'success': True,
                'deleted_count': 0
            }
        except Exception as e:
            raise e
    
    def delete_vectors_by_folder_id(self, folder_id: str):
        """根据文件夹ID删除相关向量
        
        Args:
            folder_id (str): 文件夹ID
            
        Returns:
            dict: 删除结果
        """
        try:
            if not self._vector_store:
                raise ValueError("向量存储未初始化")
            
            # 使用过滤器删除指定文件夹的向量
            if hasattr(self._vector_store, '_collection'):
                # 获取所有匹配的向量ID
                result = self._vector_store._collection.get(
                    where={'folder_id': folder_id}
                )
                
                if result and result.get('ids'):
                    ids_to_delete = result['ids']
                    # 删除匹配的向量
                    self._vector_store._collection.delete(ids=ids_to_delete)
                    return {
                        'success': True,
                        'deleted_count': len(ids_to_delete)
                    }
                
            return {
                'success': True,
                'deleted_count': 0
            }
        except Exception as e:
            raise e
