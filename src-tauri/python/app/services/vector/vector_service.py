"""向量服务模块 - 封装文档向量化、向量存储和检索功能"""
import threading
from app.services.base_service import BaseService
from app.repositories.vector_repository import VectorRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.vector.vector_store_service import VectorStoreService
from app.services.chat.generation_service import GenerationService

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
        self.chunk_repo = DocumentChunkRepository()
        
        # 直接使用VectorStoreService，它已经包含了向量存储的初始化和缓存功能
        self.vector_store_service = VectorStoreService()
        
        self.log_info("向量服务初始化成功，使用VectorStoreService")
        self._initialized = True
    
    def embed_document(self, doc_content: str, metadata: dict):
        """将文档内容转换为向量表示并存储
        
        Args:
            doc_content (str): 文档内容
            metadata (dict): 文档元数据
            
        Returns:
            dict: 向量化结果
        """
        try:
            self.log_info(f"📊 开始文档向量化处理: 内容长度={len(doc_content)} 字符")
            
            # 从vector_store_service获取向量仓库实例
            vector_repo = self.vector_store_service.vector_db_service.vector_repository
            # 执行文档向量化
            result = vector_repo.embed_document(doc_content, metadata)
            
            self.log_info(f"✅ 文档向量化成功: 生成 {result.get('chunk_count', 0)} 个向量")
            
            return {
                'success': True,
                'message': '文档向量化成功',
                'chunk_count': result.get('chunk_count', 0),
                'vector_result': result
            }
        except Exception as e:
            self.log_error(f"❌ 文档向量化失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'文档向量化失败: {str(e)}',
                'chunk_count': 0
            }
    
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
            self.log_info(f"🔍 开始向量检索: 查询='{query}', 结果数量={k}, 分数阈值={score_threshold}")
            
            # 从vector_store_service获取向量仓库实例
            vector_repo = self.vector_store_service.vector_db_service.vector_repository
            # 执行向量检索
            results = vector_repo.search_vectors(query, k=k, filter=filter, score_threshold=score_threshold)
            
            self.log_info(f"✅ 向量检索成功: 找到 {len(results.get('results', []))} 个相关结果")
            
            # 格式化结果
            formatted_results = []
            for result in results.get('results', []):
                formatted_results.append({
                    'content': result.page_content,
                    'metadata': result.metadata
                })
            
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
    
    def manage_vector_store(self, action: str, params: dict = None):
        """向量数据库管理
        
        Args:
            action (str): 操作类型 (clear, stats)
            params (dict): 操作参数
            
        Returns:
            dict: 管理操作结果
        """
        try:
            self.log_info(f"🗄️  开始向量数据库管理操作: action='{action}'")
            
            # 从vector_store_service获取向量仓库实例
            vector_repo = self.vector_store_service.vector_db_service.vector_repository
            
            if action == 'clear':
                # 清空向量数据库
                vector_repo.clear_vector_store()
                self.log_info("✅ 向量数据库已清空")
                return {'success': True, 'message': '向量数据库已清空'}
            elif action == 'stats':
                # 获取向量数据库统计信息
                stats = vector_repo.get_vector_store_stats()
                self.log_info(f"✅ 获取向量数据库统计信息成功")
                return {
                    'success': True,
                    'message': '获取统计信息成功',
                    'stats': stats
                }
            else:
                self.log_warning(f"⚠️  不支持的向量数据库管理操作: {action}")
                return {'success': False, 'message': f'不支持的操作: {action}'}
        except Exception as e:
            self.log_error(f"❌ 向量数据库管理操作失败: {str(e)}")
            return {
                'success': False,
                'message': f'向量数据库管理失败: {str(e)}'
            }
    
    def delete_vectors_by_document_id(self, document_id: str):
        """根据文档ID删除相关向量
        
        Args:
            document_id (str): 文档ID
            
        Returns:
            dict: 删除结果
        """
        try:
            self.log_info(f"🗑️  开始删除文档相关向量: document_id='{document_id}'")
            
            # 从vector_store_service获取向量仓库实例
            vector_repo = self.vector_store_service.vector_db_service.vector_repository
            # 删除相关向量
            result = vector_repo.delete_vectors_by_document_id(document_id)
            
            self.log_info(f"✅ 删除文档相关向量成功: 删除 {result.get('deleted_count', 0)} 个向量")
            
            return {
                'success': True,
                'message': '文档向量删除成功',
                'deleted_count': result.get('deleted_count', 0)
            }
        except Exception as e:
            self.log_error(f"❌ 删除文档相关向量失败: {str(e)}")
            return {
                'success': False,
                'message': f'文档向量删除失败: {str(e)}',
                'deleted_count': 0
            }
    
    def delete_vectors_by_folder_id(self, folder_id: str):
        """根据文件夹ID删除相关向量
        
        Args:
            folder_id (str): 文件夹ID
            
        Returns:
            dict: 删除结果
        """
        try:
            self.log_info(f"🗑️  开始删除文件夹相关向量: folder_id='{folder_id}'")
            
            # 从vector_store_service获取向量仓库实例
            vector_repo = self.vector_store_service.vector_db_service.vector_repository
            # 删除相关向量
            result = vector_repo.delete_vectors_by_folder_id(folder_id)
            
            self.log_info(f"✅ 删除文件夹相关向量成功: 删除 {result.get('deleted_count', 0)} 个向量")
            
            return {
                'success': True,
                'message': '文件夹向量删除成功',
                'deleted_count': result.get('deleted_count', 0)
            }
        except Exception as e:
            self.log_error(f"❌ 删除文件夹相关向量失败: {str(e)}")
            return {
                'success': False,
                'message': f'文件夹向量删除失败: {str(e)}',
                'deleted_count': 0
            }
    
    def vectorize_documents(self, split_documents, document_id, file_path, folder_id=''):
        """向量化并存储分割后的文档
        
        Args:
            split_documents: 分割后的文档列表
            document_id: 文档ID
            file_path: 文件路径
            folder_id: 文件夹ID
            
        Returns:
            dict: 向量化结果
        """
        try:
            self.log_info(f"🔢 开始向量化文档: document_id='{document_id}', 文本块数量={len(split_documents)}")
            
            # 为每个分块添加元数据
            for chunk in split_documents:
                chunk.metadata.update({
                    'document_id': document_id,
                    'file_path': file_path,
                    'folder_id': folder_id
                })
            
            # 直接使用vector_store_service的add_documents方法
            success, message = self.vector_store_service.add_documents(split_documents)
            
            if success:
                self.log_info(f"✅ 文档向量化成功: 生成 {len(split_documents)} 个向量")
                return {
                    'vectorized': True,
                    'vector_count': len(split_documents),
                    'message': '文档向量化成功'
                }
            else:
                self.log_error(f"❌ 文档向量化失败: {message}")
                return {
                    'vectorized': False,
                    'vector_count': 0,
                    'message': f'文档向量化失败: {message}',
                    'error': message
                }
        except Exception as e:
            self.log_error(f"❌ 文档向量化失败: {str(e)}")
            return {
                'vectorized': False,
                'vector_count': 0,
                'message': f'文档向量化失败: {str(e)}',
                'error': str(e)
            }
    
    def search_documents(self, query: str, k: int = 3, score_threshold: float = 0.7, search_type: str = "similarity", filter: dict = None):
        """搜索相关文档
        
        Args:
            query (str): 查询文本
            k (int): 返回结果数量
            score_threshold (float): 相似度分数阈值
            search_type (str): 搜索类型
            filter (dict): 过滤条件
            
        Returns:
            list: 相关文档列表
        """
        try:
            self.log_info(f"🔍 开始搜索相关文档: 查询='{query}', 结果数量={k}")
            
            # 直接使用vector_store_service的search_documents方法，利用其缓存功能
            results = self.vector_store_service.search_documents(
                query=query,
                k=k,
                score_threshold=score_threshold,
                search_type=search_type,
                filter=filter
            )
            
            self.log_info(f"✅ 找到 {len(results)} 个相关文档片段")
            
            return results
        except Exception as e:
            self.log_error(f"❌ 搜索文档失败: {str(e)}")
            return []
    
    def clear_vector_store(self):
        """清空向量存储
        
        Returns:
            bool: 是否成功清空
        """
        try:
            self.log_info("🗑️  开始清空向量存储...")
            success, message = self.vector_store_service.clear_vector_store()
            self.log_info(f"✅ 向量存储已清空: {message}")
            return success
        except Exception as e:
            self.log_error(f"❌ 清空向量存储失败: {str(e)}")
            return False
    
    def get_enhanced_prompt(self, question, rag_config=None):
        """获取增强提示，将查询和检索到的上下文结合
        
        Args:
            question: 用户查询
            rag_config: RAG配置
            
        Returns:
            增强后的提示
        """
        if not rag_config or not rag_config.get('enabled', False):
            return question
        
        try:
            # 导入配置管理器
            from app.core.config import config_manager
            
            # 更新配置
            config = config_manager.get('rag', {})
            if rag_config:
                config.update(rag_config)
            
            # 获取向量存储
            if not self.vector_store_service.vector_store:
                self.log_error("向量存储未初始化")
                return question
            
            # 执行相似性搜索
            k = config.get('top_k', 3)
            score_threshold = config.get('score_threshold', 0.7)
            
            results = self.search_documents(
                query=question,
                k=k,
                score_threshold=score_threshold
            )
            
            if results:
                # 使用生成服务的build_prompt方法构建提示
                generation_service = GenerationService()
                return generation_service.build_prompt(question, results)
            
            return question
        except Exception as e:
            self.log_error(f"生成增强提示失败: {str(e)}")
            return question
