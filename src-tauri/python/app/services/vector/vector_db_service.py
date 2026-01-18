"""向量数据库服务 - 管理向量存储的初始化和操作，位于数据层"""
import os
from typing import List, Dict, Any, Optional
from app.core.config import config_manager
from app.services.base_service import BaseService
from app.repositories.vector_repository import VectorRepository

class VectorDBService(BaseService):
    """向量数据库服务类，管理向量存储的初始化和操作"""
    
    # 单例实例
    _instance = None
    _lock = None  # 用于线程安全的单例实现
    
    def __init__(self, vector_db_path=None, embedder_model='all-MiniLM-L6-v2'):
        """初始化向量数据库服务
        
        Args:
            vector_db_path: 向量数据库的存储路径
            embedder_model: 使用的嵌入模型名称
        """
        # 使用配置管理器获取用户数据目录
        self.config_manager = config_manager
        self.user_data_dir = self.config_manager.get_user_data_dir()
        
        # 设置默认路径
        self.vector_db_path = vector_db_path or os.path.join(
            self.user_data_dir, 'Retrieval-Augmented Generation', 'vectorDb'
        )
        
        self.embedder_model = embedder_model
        self._embeddings = None  # 嵌入模型实例
        self._vector_store = None  # 向量存储实例
        self._directories_ensured = False  # 目录是否已创建
        
        # 创建标准的embedding模型目录
        self.embedding_models_dir = os.path.join(self.user_data_dir, 'models', 'embedding')
        
        # 初始化向量数据库Repository
        self.vector_repository = VectorRepository()
    
    @property
    def embeddings(self):
        """获取嵌入模型实例（懒加载）"""
        if self._embeddings is None:
            self.log_info("Embeddings not initialized, starting initialization...")
            self._ensure_directories()
            self._init_embeddings()
        return self._embeddings
    
    @property
    def vector_store(self):
        """获取向量存储实例（懒加载）"""
        if self._vector_store is None:
            self.log_info("Vector store not initialized, starting initialization...")
            if self._embeddings is None:  # 确保嵌入模型已初始化
                self.log_info("Embeddings not available, initializing first...")
                self._ensure_directories()
                self._init_embeddings()
            self._init_vector_store()
        return self._vector_store
    
    @classmethod
    def get_instance(cls, vector_db_path=None, embedder_model='all-MiniLM-L6-v2'):
        """获取单例实例
        
        Args:
            vector_db_path: 向量数据库的存储路径
            embedder_model: 使用的嵌入模型名称
            
        Returns:
            VectorDBService: 向量数据库服务单例实例
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
    
    def _ensure_directories(self) -> bool:
        """确保所有必要的目录存在
        
        Returns:
            bool: 是否成功创建目录
        """
        if self._directories_ensured:
            return True
            
        try:
            # 一次性创建所有需要的目录
            directories = [
                self.embedding_models_dir,
                os.path.dirname(self.vector_db_path)
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            self.log_info(f"初始化目录结构完成: embedding_models_dir={self.embedding_models_dir}")
            self._directories_ensured = True
            return True
        except Exception as e:
            self.log_error(f"初始化目录失败: {e}")
            return False
    
    def _init_embeddings(self) -> bool:
        """初始化嵌入模型
        
        Returns:
            bool: 是否成功初始化嵌入模型
        """
        try:
            # 尝试从新位置导入（推荐方式）
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
                self.log_info("使用langchain-huggingface包中的HuggingFaceEmbeddings")
            except ImportError:
                # 兼容旧版本
                self.log_warning("langchain-huggingface包未安装，尝试使用langchain_community中的HuggingFaceEmbeddings")
                from langchain_community.embeddings import HuggingFaceEmbeddings
            
            # 模型路径搜索逻辑 - 优化版：减少不必要的文件系统调用
            model_path = None
            
            # 1. 优先检查用户指定的本地模型路径
            user_local_model_path = r'C:\Users\Admin\.cache\modelscope\hub\models\Qwen\Qwen3-Embedding-0___6B'
            if os.path.exists(user_local_model_path):
                self.log_info(f"使用用户指定的本地模型路径: {user_local_model_path}")
                model_path = user_local_model_path
            elif os.path.exists(self.embedder_model):
                # 2. 如果直接指定了本地路径且存在，优先使用
                model_path = self.embedder_model
            else:
                # 3. 构建并检查标准用户数据目录下的模型路径
                standard_model_path = os.path.join(self.embedding_models_dir, self.embedder_model)
                if os.path.exists(standard_model_path):
                    model_path = standard_model_path
                else:
                    # 4. 检查特定的qwen3-embedding模型路径
                    qwen_model_path = os.path.join(self.embedding_models_dir, 'qwen3-embedding')
                    if os.path.exists(qwen_model_path):
                        model_path = qwen_model_path
                    else:
                        # 5. 检查本地缓存路径
                        local_cache_path = os.path.join(os.path.dirname(__file__), '.cache', self.embedder_model)
                        if os.path.exists(local_cache_path):
                            model_path = local_cache_path
                        else:
                            # 6. 检查HuggingFace缓存路径
                            hf_cache_path = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'hub', 
                                                       f'models--{self.embedder_model.replace('/', '--')}', 'snapshots')
                            if os.path.exists(hf_cache_path):
                                model_path = hf_cache_path
            
            # 加载模型
            if model_path:
                self.log_info(f"找到嵌入模型路径: {model_path}")
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=model_path,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
            else:
                # 从HuggingFace下载模型
                self.log_info(f"从HuggingFace下载嵌入模型: {self.embedder_model}")
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=self.embedder_model,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True},
                    cache_folder=self.embedding_models_dir
                )
                model_path = self.embedder_model
            
            self.log_info(f"嵌入模型初始化成功: {model_path}")
            return True
            
        except ImportError as e:
            self.log_error(f"嵌入模型依赖包未安装: {e}")
            self.log_info("请安装必要的包: pip install langchain-huggingface sentence-transformers")
            self._embeddings = None
            return False
        except Exception as e:
            self.log_error(f"嵌入模型初始化失败: {e}")
            
            # 尝试使用替代缓存位置
            try:
                alternative_cache_dir = os.path.join(os.path.dirname(__file__), '.cache', 'sentence-transformers', self.embedder_model)
                if os.path.exists(alternative_cache_dir):
                    self.log_info(f"尝试使用替代本地缓存模型: {alternative_cache_dir}")
                    self._embeddings = HuggingFaceEmbeddings(
                        model_name=alternative_cache_dir,
                        model_kwargs={'device': 'cpu'},
                        encode_kwargs={'normalize_embeddings': True}
                    )
                    return True
            except Exception as alt_error:
                self.log_error(f"替代模型加载也失败: {alt_error}")
                
            self._embeddings = None
            return False
    
    def _init_vector_store(self) -> bool:
        """初始化向量存储
        
        Returns:
            bool: 是否成功初始化向量存储
        """
        try:
            from langchain_chroma import Chroma
            
            # 确保嵌入模型已初始化
            if not self._embeddings:
                self.log_error("无法初始化向量存储：嵌入模型未初始化")
                return False
            
            # 如果向量库路径存在，则加载现有的向量库
            if os.path.exists(self.vector_db_path):
                self._vector_store = Chroma(
                    persist_directory=self.vector_db_path,
                    embedding_function=self._embeddings
                )
                self.log_info("向量库加载成功")
            else:
                # 如果没有现有向量库，创建一个空的
                self._vector_store = Chroma(
                    persist_directory=self.vector_db_path,
                    embedding_function=self._embeddings
                )
                self.log_info("向量库创建成功")
            
            # 将向量存储实例传递给Repository
            self.vector_repository.set_vector_store(self._vector_store)
            return True
        except Exception as e:
            self.log_error(f"向量库初始化失败: {e}")
            self._vector_store = None
            return False
    
    def add_documents(self, documents: List[Any]) -> bool:
        """将文档片段添加到向量库中
        
        Args:
            documents: 文档片段列表
            
        Returns:
            bool: 是否成功添加
        """
        try:
            if not documents:
                self.log_warning("没有找到文档或文档为空")
                return False
            
            if not self.vector_store:
                self.log_error("向量存储未初始化")
                return False
            
            # 使用Repository添加文档
            result = self.vector_repository.add_documents(documents)
            
            if result:
                self.log_info(f"成功将 {len(documents)} 个文档片段添加到向量库")
            return result
        except Exception as e:
            self.log_error(f"添加文档失败: {e}")
            return False
    
    def clear_vector_store(self) -> bool:
        """清空向量库
        
        Returns:
            bool: 是否成功清空
        """
        max_retries = 3
        retry_delay = 1  # 秒
        
        for attempt in range(max_retries):
            try:
                if not self.vector_store:
                    self.log_error("向量存储未初始化")
                    return False
                
                # 使用Repository清空向量存储
                result = self.vector_repository.clear_vector_store()
                
                if result:
                    self.log_info("向量库清空成功")
                    return True
            except Exception as e:
                self.log_error(f"清空向量库失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                
        return False
    
    def get_vector_statistics(self) -> Dict[str, Any]:
        """获取向量库统计信息
        
        Returns:
            dict: 向量库统计信息
        """
        try:
            if not self.vector_store:
                return {
                    'status': 'error',
                    'error': '向量存储未初始化',
                    'total_vectors': 0
                }
            
            stats = {
                'status': 'ok',
                'embedding_model': self.embedder_model,
                'vector_store_type': 'chroma',
                'vector_store_path': self.vector_db_path,
                'total_vectors': 0
            }
            
            # 使用Repository获取向量数量
            stats['total_vectors'] = self.vector_repository.get_vector_count()
            
            return stats
        except Exception as e:
            self.log_error(f"获取向量库统计信息失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'total_vectors': 0
            }
    
    def search_documents(self, query: str, k: int = 5, score_threshold: Optional[float] = None, 
                       search_type: str = "similarity", fetch_k: int = 20) -> List[Any]:
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
            # 触发搜索开始回调
            from app.utils.callback_manager import trigger_callback
            trigger_callback('search_start', 
                           query=query[:50] + "..." if len(query) > 50 else query,
                           k=k,
                           score_threshold=score_threshold,
                           search_type=search_type)
            
            self.log_info(f"Starting search for query: '{query[:50]}...' with k={k}, score_threshold={score_threshold}, search_type={search_type}, fetch_k={fetch_k}")
            
            if not self.vector_store:
                self.log_error("搜索失败：向量存储未初始化")
                trigger_callback('error', 
                               event='search',
                               error="向量存储未初始化")
                return []
            
            # 使用Repository搜索文档
            result = self.vector_repository.search_documents(
                query=query,
                k=k,
                score_threshold=score_threshold,
                search_type=search_type,
                fetch_k=fetch_k
            )
            
            self.log_info(f"搜索完成，找到 {len(result)} 个相关文档")
            
            # 触发搜索结束回调
            trigger_callback('search_end', 
                           query=query[:50] + "..." if len(query) > 50 else query,
                           result_count=len(result),
                           cache_hit=False)
            
            return result
        except Exception as e:
            self.log_error(f"搜索文档失败: {str(e)}")
            self.log_error(f"错误类型: {type(e).__name__}")
            import traceback
            self.log_error(f"错误堆栈: {traceback.format_exc()}")
            
            # 触发错误回调
            from app.utils.callback_manager import trigger_callback
            trigger_callback('error', 
                           event='search',
                           error=str(e))
            
            return []
