"""向量服务模块 - 封装文档向量化、向量存储和检索功能"""
import threading
from app.services.base_service import BaseService
from app.utils.rag import VectorUtils

class VectorService(BaseService):
    """向量服务类，封装所有向量相关的操作"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VectorService, cls).__new__(cls)
                cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        """初始化向量服务"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        super().__init__()
        
        # 导入service_container并获取依赖
        from app.core.service_container import service_container
        self.data_service = service_container.get_service('data_service')
        
        # 导入配置管理器和路径管理器
        from app.core.config import config_manager
        from app.utils.path_manager import PathManager
        self.config_manager = config_manager
        self.path_manager = PathManager()
        
        self.log_info("向量服务初始化成功，支持多知识库向量存储")
        self._initialized = True
    

    def search_vectors(self, query: str, k: int = 5, score_threshold: float = None, knowledge_base_name="default", vector_db_path=None, embedder_model=None):
        """根据查询向量检索相关文档
        
        Args:
            query (str): 查询文本
            k (int): 返回结果数量
            score_threshold (float): 相似度分数阈值，低于该阈值的结果将被过滤
            knowledge_base_name: 知识库名称
            vector_db_path: 向量数据库路径
            embedder_model: 嵌入模型名称
            
        Returns:
            dict: 向量检索结果
        """
        try:
            self.log_info(f"🔍 开始向量检索: 查询='{query}', 结果数量={k}, 分数阈值={score_threshold}, 知识库='{knowledge_base_name}'")
            
            # 通过 data_service 执行向量检索
            results = self.data_service.search_vectors(query, k=k, score_threshold=score_threshold, folder_id=knowledge_base_name)
            
            self.log_info(f"✅ 向量检索成功: 找到 {len(results.get('results', []))} 个相关结果, 知识库='{knowledge_base_name}'")
            
            # 格式化结果
            formatted_results = VectorUtils.format_vector_results(results.get('results', []))
            
            return {
                'success': True,
                'results': formatted_results,
                'result_count': len(formatted_results)
            }
        except Exception as e:
            self.log_error(f"❌ 向量检索失败: {str(e)}")
            return {
                'success': False,
                'message': f'向量检索失败: {str(e)}',
                'results': [],
                'result_count': 0
            }
    


    
    def search_documents(self, query: str, k: int = 3, score_threshold: float = 0.7, search_type: str = "similarity", filter: dict = None, knowledge_base_name="default"):
        """搜索相关文档
        
        Args:
            query (str): 查询文本
            k (int): 返回结果数量
            score_threshold (float): 相似度分数阈值
            search_type (str): 搜索类型
            filter (dict): 过滤条件
            knowledge_base_name: 知识库名称
            
        Returns:
            list: 相关文档列表
        """
        try:
            self.log_info(f"🔍 开始搜索相关文档: 查询='{query}', 结果数量={k}, 知识库='{knowledge_base_name}'")
            
            # 通过 data_service 搜索文档
            results = self.data_service.search_documents(
                query=query,
                k=k,
                score_threshold=score_threshold,
                search_type=search_type,
                filter=filter,
                knowledge_base_name=knowledge_base_name
            )
            
            self.log_info(f"✅ 找到 {len(results)} 个相关文档片段, 知识库='{knowledge_base_name}'")
            
            return results
        except Exception as e:
            self.log_error(f"❌ 搜索文档失败: {str(e)}")
            return []
    

    def perform_rag_search(self, question, selected_folders=None, k=None):
        """执行RAG搜索，获取相关文档片段"""
        # 从配置中获取参数
        config_vector = self.config_manager.get('vector', {})
        if k is None:
            k = config_vector.get('top_k', 3)
        score_threshold = config_vector.get('score_threshold', 0.7)
        
        # 构建过滤器
        filter = None
        knowledge_base_name = "default"
        vector_db_path = None
        embedder_model = None
        
        if selected_folders:
            # 如果有选中的文件夹，构建filter条件
            filter = {'folder_id': {'$in': selected_folders}}
            
            # 尝试从第一个选中的文件夹获取知识库信息
            try:
                # 获取第一个选中的文件夹ID
                first_folder_id = selected_folders[0]
                # 直接使用data_service获取文件夹信息
                folder = self.data_service.get_folder_by_id(first_folder_id)
                
                if folder:
                    if hasattr(folder, 'name'):
                        knowledge_base_name = folder.name
                        self.log_info(f"从selected_folders获取知识库名称成功: {knowledge_base_name}")
                    if hasattr(folder, 'vector_db_path'):
                        vector_db_path = folder.vector_db_path
                        self.log_info(f"从selected_folders获取向量数据库路径成功: {vector_db_path}")
                    if hasattr(folder, 'embedding_model'):
                        embedder_model = folder.embedding_model
                        self.log_info(f"从selected_folders获取嵌入模型成功: {embedder_model}")
            except Exception as e:
                self.log_warning(f"获取folder信息失败，使用默认知识库: {e}")
        
        # 执行相似性搜索
        vector_results = self.search_vectors(
            query=question,
            k=k,
            score_threshold=score_threshold,
            knowledge_base_name=knowledge_base_name
        )
        
        # 转换向量结果为文档列表
        context_docs = []
        if vector_results['success']:
            for result in vector_results['results']:
                # 添加文档到上下文
                context_docs.append(result)
        
        return context_docs, vector_results
    


