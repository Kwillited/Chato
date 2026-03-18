"""LanceDB向量数据库仓储层实现 - 封装向量数据库的所有操作"""
from typing import List, Dict, Any, Optional
from app.repositories.base_repository import BaseRepository
from langchain_core.vectorstores import VectorStore
from langchain_community.vectorstores import LanceDB
import lancedb
import os
from lancedb.query import MatchQuery, PhraseQuery

class LanceDBRepository(BaseRepository):
    """LanceDB向量数据库仓储类，封装所有向量数据库相关的操作"""
    
    def __init__(self, connection=None, embedding_model=None):
        """初始化LanceDB向量数据库仓储
        
        Args:
            connection: LanceDB连接实例
            embedding_model: 嵌入模型实例
        """
        # 不调用父类的SQLAlchemy会话初始化，因为向量数据库不需要SQLite会话
        self.conn = connection
        self.embedding = embedding_model  # 必需：用于向量化
        self._vector_store: Optional[VectorStore] = None
    
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
    
    def connect(self, vector_db_path=None):
        """连接到LanceDB数据库
        
        Args:
            vector_db_path: 向量数据库路径
            
        Returns:
            LanceDBRepository: 自身实例，支持链式调用
        """
        from app.core.config import config_manager
        from app.utils.path_manager import PathManager
        from app.core.logger import logger
        
        # 获取配置作为默认值
        if not vector_db_path:
            vector_db_path = config_manager.get('vector.vector_db_path', '')
            
        # 构建默认路径
        if not vector_db_path:
            path_manager = PathManager()
            vector_db_path = path_manager.get_vector_db_root()
        
        # 初始化LanceDB连接
        os.makedirs(vector_db_path, exist_ok=True)
        
        # 每次都创建新的连接，确保使用正确的LanceDB连接
        self.conn = lancedb.connect(vector_db_path)
        
        return self
    
    def load_embedding_model(self, embedder_model=None):
        """加载嵌入模型
        
        Args:
            embedder_model: 嵌入模型名称
            
        Returns:
            LanceDBRepository: 自身实例，支持链式调用
        """
        from app.core.config import config_manager
        from app.llm.managers.embedding_model_manager import EmbeddingModelManager
        
        # 获取配置作为默认值
        embedder_model = embedder_model or config_manager.get('vector.embedder_model', 'qwen3-embedding-0.6b')
        
        # 解析模型类型和名称
        model_type = 'huggingface'
        model_name = embedder_model
        
        # 每个模型都会有前缀，只需要对第一个-进行分离
        if '-' in model_name:
            # 找到第一个-的位置
            hyphen_index = model_name.index('-')
            # 提取前缀作为模型类型
            vendor = model_name[:hyphen_index].lower()
            # 提取剩余部分作为模型名称
            model_name = model_name[hyphen_index + 1:]
            # 直接使用提取的vendor作为model_type
            model_type = vendor
        
        # 加载嵌入模型
        self.embedding = EmbeddingModelManager.get_embedding_model(
            model_type, model_name
        )
        
        if not self.embedding:
            self.embedding = EmbeddingModelManager.get_embedding_model(
                'huggingface', 'all-MiniLM-L6-v2'
            )
        
        return self
    
    def create_vector_store(self, folder_id=None, documents=None, embedder_model=None):
        """创建向量存储
        
        Args:
            folder_id: 文件夹ID
            documents: 文档列表
            embedder_model: 嵌入模型名称
            
        Returns:
            LanceDBRepository: 自身实例，支持链式调用
        """
        from app.core.logger import logger
        
        # 确保连接到LanceDB
        if not self.conn:
            self.connect()
        
        # 加载嵌入模型
        if not self.embedding:
            self.load_embedding_model(embedder_model)
        
        table_name = folder_id or "default"
        
        # 检查LanceDB中表是否存在
        table_exists = False
        try:
            table_names = self.conn.table_names()
            table_exists = table_name in table_names
        except Exception as e:
            logger.warning(f"⚠️  检查表存在性时出错: {e}")
        
        # 使用from_documents初始化向量存储
        try:
            # 如果表存在，使用append模式避免覆盖
            mode = "append" if table_exists else "create"
            logger.info(f"📁 表 {table_name} {'已存在，使用append模式' if table_exists else '不存在，使用create模式'}")
            
            self._vector_store = LanceDB.from_documents(
                documents=documents or [],
                embedding=self.embedding,
                connection=self.conn,
                table_name=table_name,
                mode=mode  # 设置模式，避免覆盖
            )
            
            # 如果是新建表，创建全文搜索索引
            if not table_exists:
                logger.info(f"🔍 为表 {table_name} 创建全文搜索索引")
                # 直接从连接中获取表并创建索引
                try:
                    table = self.conn.open_table(table_name)
                    table.create_fts_index("text", replace=True)
                    logger.info(f"✅ 表 {table_name} 全文搜索索引创建成功")
                except Exception as e:
                    logger.warning(f"⚠️ 创建全文搜索索引时出错: {e}")
        except Exception as e:
            logger.error(f"❌ 向量存储初始化失败: {e}")
            raise
        return self
    
    def load_vector_store(self, table_name: str, embedder_model=None):
        """加载指定的向量存储表
        
        Args:
            table_name: 表名
            embedder_model: 嵌入模型名称
            
        Returns:
            LanceDBRepository: 自身实例，支持链式调用
        """
        from app.core.logger import logger
        
        logger.info(f"📁 准备加载向量存储表: {table_name}")
        
        # 确保连接到LanceDB
        if not self.conn:
            self.connect()
        
        # 确保加载嵌入模型
        if not self.embedding:
            self.load_embedding_model(embedder_model)
        
        try:
            logger.info(f"🔗 正在加载表: {table_name}")
            self._vector_store = LanceDB(
                connection=self.conn,
                embedding=self.embedding,
                table_name=table_name
            )
            logger.info(f"✅ 向量存储表 {table_name} 加载成功")
        except Exception as e:
            logger.error(f"❌ 向量存储加载失败: {e}")
            raise
        
        return self
    
    def similarity_search(self, query: str, k: int = 3, score_threshold: float = None) -> List[Any]:
        """相似度搜索相关文档 - 调用 similarity_search_with_score
        
        Args:
            query: 查询文本
            k: 返回结果数量，默认3
            score_threshold: 相似度分数阈值，低于该阈值的结果将被过滤
            
        Returns:
            List[Any]: 相关文档列表
        """
        from app.core.logger import logger
        
        try:
            logger.info(f"🔍 开始相似度搜索，查询文本: {query[:50]}...")
            logger.info(f"📋 相似度搜索参数: k={k}, score_threshold={score_threshold}")
            
            # 直接调用 similarity_search_with_score 方法
            logger.info("🔗 执行向量相似度搜索")
            results = self._vector_store.similarity_search_with_score(query, k=k)
            
            logger.info(f"📊 搜索结果数量: {len(results)}")
            
            # 打印详细的搜索结果
            for i, (doc, score) in enumerate(results):
                logger.info(f"📋 相似度搜索结果 {i+1}: 分数={score:.4f}, 内容预览={doc.page_content[:50]}...")
            
            # 如果设置了分数阈值，过滤结果
            if score_threshold is not None:
                logger.info(f"🎯 应用分数阈值: {score_threshold}")
                filtered_results = [(doc, score) for doc, score in results if score >= score_threshold]
                logger.info(f"📊 过滤后结果数量: {len(filtered_results)}")
                results = filtered_results
            
            # 只返回文档对象，不返回分数
            docs = [doc for doc, score in results]
            logger.info(f"✅ 相似度搜索完成，返回 {len(docs)} 个文档")
            return docs
        except Exception as e:
            logger.error(f"❌ 相似度搜索失败: {e}")
            raise e
    
    def search(self, query: str, search_type: str = "similarity", k: int = 3, score_threshold: float = None, table_name: str = None, embedder_model: str = None, case_sensitive: bool = False) -> List[Any]:
        """搜索相关文档 - 根据 search_type 选择搜索方式
        
        Args:
            query: 查询文本
            search_type: 搜索类型，"similarity" 表示相似度搜索，"keyword" 表示关键词搜索，默认 "similarity"
            k: 返回结果数量，默认3
            score_threshold: 相似度分数阈值，仅在 similarity 搜索时使用
            table_name: 表名，如果提供则加载该表
            embedder_model: 嵌入模型名称，如果未加载则使用
            case_sensitive: 是否区分大小写，仅在 keyword 搜索时使用，默认 False
            
        Returns:
            List[Any]: 相关文档列表
        """
        from app.core.logger import logger
        
        try:
            search_type = search_type.lower()
            
            # 统一的初始化逻辑
            logger.info(f"📋 搜索参数: search_type={search_type}, k={k}, score_threshold={score_threshold}, table_name={table_name}, case_sensitive={case_sensitive}")
            
            # 如果提供了表名，加载指定的表
            if table_name:
                logger.info(f"� 准备加载表: {table_name}")
                # 加载嵌入模型
                if not self.embedding:
                    logger.info(f"🤖 加载嵌入模型: {embedder_model or '默认模型'}")
                    self.load_embedding_model(embedder_model)
                self.load_vector_store(table_name)
            else:
                logger.info("📁 未指定表名，使用当前加载的向量存储")
            
            if not self._vector_store:
                logger.error("❌ 向量存储未初始化")
                raise ValueError("向量存储未初始化")
            
            # 检查向量存储表的状态
            if hasattr(self._vector_store, "table"):
                try:
                    vector_count = self._vector_store.table.count_rows()
                    logger.info(f"📊 向量存储表中的向量数量: {vector_count}")
                except Exception as e:
                    logger.warning(f"⚠️  无法获取向量数量: {e}")
            
            # 根据搜索类型调用对应的方法
            if search_type == "similarity":
                logger.info("� 使用相似度搜索方式")
                return self.similarity_search(
                    query=query,
                    k=k,
                    score_threshold=score_threshold
                )
            elif search_type == "keyword":
                logger.info("🔑 使用关键词搜索方式")
                return self.keyword_search(
                    query=query,
                    k=k,
                    case_sensitive=case_sensitive
                )
            else:
                raise ValueError(f"不支持的搜索类型: {search_type}，支持的类型有 'similarity' 和 'keyword'")
        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            raise e
    
    def keyword_search(self, query: str, k: int = 10, case_sensitive: bool = False) -> Dict[str, List[Any]]:
        """关键词搜索文档 - 使用LanceDB的查询API实现多种搜索方式
        
        Args:
            query: 查询关键词
            k: 返回结果数量，默认10
            case_sensitive: 是否区分大小写，默认False
            
        Returns:
            Dict[str, List[Any]]: 包含三种搜索结果的字典
                - exact_match: 精确匹配结果
                - fuzzy_match: 模糊匹配结果
                - phrase_match: 短语匹配结果
        """
        from app.core.logger import logger
        
        try:
            logger.info(f"🔑 开始关键词搜索，查询关键词: {query}")
            logger.info(f"📋 关键词搜索参数: k={k}, case_sensitive={case_sensitive}")
            
            if not hasattr(self._vector_store, "table"):
                logger.error("❌ 向量存储表不存在")
                raise ValueError("向量存储表不存在")
            
            table = self._vector_store.table
            
            # 辅助函数：将DataFrame转换为Document对象列表
            def convert_to_docs(df):
                docs = []
                from langchain_core.documents import Document
                for _, row in df.iterrows():
                    content = row.get('text', '') or row.get('page_content', '')
                    doc = Document(
                        page_content=content,
                        metadata={k: v for k, v in row.items() if k not in ['text', 'page_content', 'vector']}
                    )
                    docs.append(doc)
                return docs
            
            # 1. 精确匹配查询
            logger.info("🔍 执行精确匹配查询")
            exact_query = MatchQuery(query, "text")
            exact_results = table.search(exact_query).limit(k).to_pandas()
            exact_docs = convert_to_docs(exact_results)
            logger.info(f"✅ 精确匹配找到 {len(exact_docs)} 个文档")
            
            # 2. 模糊匹配（允许拼写错误）
            logger.info("🔍 执行模糊匹配查询")
            fuzzy_query = MatchQuery(query, "text", fuzziness=2)  # 允许2个字符的编辑距离
            fuzzy_results = table.search(fuzzy_query).limit(k).to_pandas()
            fuzzy_docs = convert_to_docs(fuzzy_results)
            logger.info(f"✅ 模糊匹配找到 {len(fuzzy_docs)} 个文档")
            
            # 3. 短语查询
            logger.info("🔍 执行短语匹配查询")
            phrase_query = PhraseQuery(query, "text")
            phrase_results = table.search(phrase_query).limit(k).to_pandas()
            phrase_docs = convert_to_docs(phrase_results)
            logger.info(f"✅ 短语匹配找到 {len(phrase_docs)} 个文档")
            
            # 打印详细的搜索结果
            for i, doc in enumerate(exact_docs):
                logger.info(f"📋 精确匹配结果 {i+1}: 内容预览={doc.page_content[:50]}...")
            
            for i, doc in enumerate(fuzzy_docs):
                logger.info(f"📋 模糊匹配结果 {i+1}: 内容预览={doc.page_content[:50]}...")
            
            for i, doc in enumerate(phrase_docs):
                logger.info(f"📋 短语匹配结果 {i+1}: 内容预览={doc.page_content[:50]}...")
            
            logger.info("✅ 关键词搜索完成，返回三种搜索结果")
            return {
                "exact_match": exact_docs,
                "fuzzy_match": fuzzy_docs,
                "phrase_match": phrase_docs
            }
        except Exception as e:
            logger.error(f"❌ 关键词搜索失败: {e}")
            raise e
    
    def clear_vector_store(self) -> bool:
        """清空向量库
        
        Returns:
            bool: 是否成功清空
        """
        try:
            if not self._vector_store:
                raise ValueError("向量存储未初始化")
            
            # LanceDB清空操作
            if hasattr(self._vector_store, "table"):
                self._vector_store.table.delete()
                return True
            else:
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
            
            # 获取LanceDB向量数量
            if hasattr(self._vector_store, "table"):
                return self._vector_store.table.count_rows()
            return 0
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
            if hasattr(self._vector_store, "table"):
                stats['vector_count'] = self._vector_store.table.count_rows()
                
                # 获取表名称
                if hasattr(self._vector_store.table, 'name'):
                    stats['table_name'] = self._vector_store.table.name
            
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
            if hasattr(self._vector_store, "table"):
                # 使用LanceDB的删除语法
                deleted = self._vector_store.table.delete(f"document_id = '{document_id}'")
                return {
                    'success': True,
                    'deleted_count': deleted
                }
            
            return {
                'success': True,
                'deleted_count': 0
            }
        except Exception as e:
            raise e
    
    def delete_vectors_by_folder_id(self, folder_id: str):
        """根据文件夹ID删除相关向量（删除对应表）
        
        Args:
            folder_id (str): 文件夹ID
            
        Returns:
            dict: 删除结果
        """
        try:
            from app.core.logger import logger
            
            # 确保连接到LanceDB
            if not self.conn:
                self.connect()
            
            # 直接删除表
            try:
                self.conn.drop_table(folder_id)
                logger.info(f"✅ 已删除表 {folder_id}")
                return {
                    'success': True,
                    'deleted_count': 0
                }
            except Exception as e:
                # 表不存在时不报错
                logger.info(f"📁 表 {folder_id} 不存在，无需删除")
                return {
                    'success': True,
                    'deleted_count': 0
                }
        except Exception as e:
            raise e