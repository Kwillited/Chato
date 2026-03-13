"""向量服务模块 - 封装文档向量化、向量存储和检索功能"""
import threading
from app.services.base_service import BaseService
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.vector.vector_store_service import VectorStoreService

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
        from app.repositories.document_chunk_repository import DocumentChunkRepository
        self.chunk_repo = service_container.get_service('document_chunk_repository')
        
        # 导入配置管理器和路径管理器
        from app.core.config import config_manager
        from app.utils.path_manager import PathManager
        self.config_manager = config_manager
        self.path_manager = PathManager()
        
        # 向量存储服务实例字典，按知识库名称区分
        self.vector_store_services = {}
        
        self.log_info("向量服务初始化成功，支持多知识库向量存储")
        self._initialized = True
    
    def get_vector_store_service(self, knowledge_base_name="default", vector_db_path=None, embedder_model=None):
        """获取指定知识库的向量存储服务实例
        
        Args:
            knowledge_base_name: 知识库名称
            vector_db_path: 向量数据库路径
            embedder_model: 嵌入模型名称
            
        Returns:
            VectorStoreService: 向量存储服务实例
        """
        if knowledge_base_name not in self.vector_store_services:
            if not vector_db_path or not embedder_model:
                # 如果没有提供路径和模型，尝试从配置或默认值获取
                vector_db_path = vector_db_path or self.config_manager.get('vector.vector_db_path', '')
                embedder_model = embedder_model or self.config_manager.get('vector.embedder_model', 'qwen3-embedding-0.6b')
                
                # 如果仍然没有路径，构建默认路径
                if not vector_db_path:
                    vector_db_path = self.path_manager.get_vector_db_path(knowledge_base_name)
            
            # 创建新的向量存储服务实例
            self.vector_store_services[knowledge_base_name] = VectorStoreService(
                vector_db_path=vector_db_path,
                embedder_model=embedder_model,
                knowledge_base_name=knowledge_base_name
            )
            self.log_info(f"创建向量存储服务实例: 知识库='{knowledge_base_name}', 模型='{embedder_model}'")
        return self.vector_store_services[knowledge_base_name]
    
    def embed_document(self, doc_content: str, metadata: dict, knowledge_base_name="default"):
        """将文档内容转换为向量表示并存储
        
        Args:
            doc_content (str): 文档内容
            metadata (dict): 文档元数据
            knowledge_base_name: 知识库名称
            
        Returns:
            dict: 向量化结果
        """
        try:
            self.log_info(f"📊 开始文档向量化处理: 内容长度={len(doc_content)} 字符, 知识库='{knowledge_base_name}'")
            
            # 获取指定知识库的向量存储服务实例
            vector_store_service = self.get_vector_store_service(knowledge_base_name)
            # 从vector_store_service获取向量仓库实例
            vector_repo = vector_store_service.vector_db_service.vector_repository
            # 执行文档向量化
            result = vector_repo.embed_document(doc_content, metadata)
            
            self.log_info(f"✅ 文档向量化成功: 生成 {result.get('chunk_count', 0)} 个向量, 知识库='{knowledge_base_name}'")
            
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
    
    def search_vectors(self, query: str, k: int = 5, filter: dict = None, score_threshold: float = None, knowledge_base_name="default", vector_db_path=None, embedder_model=None):
        """根据查询向量检索相关文档
        
        Args:
            query (str): 查询文本
            k (int): 返回结果数量
            filter (dict): 过滤条件
            score_threshold (float): 相似度分数阈值，低于该阈值的结果将被过滤
            knowledge_base_name: 知识库名称
            vector_db_path: 向量数据库路径
            embedder_model: 嵌入模型名称
            
        Returns:
            dict: 向量检索结果
        """
        try:
            self.log_info(f"🔍 开始向量检索: 查询='{query}', 结果数量={k}, 分数阈值={score_threshold}, 知识库='{knowledge_base_name}'")
            
            # 获取指定知识库的向量存储服务实例
            vector_store_service = self.get_vector_store_service(
                knowledge_base_name=knowledge_base_name,
                vector_db_path=vector_db_path,
                embedder_model=embedder_model
            )
            
            # 触发向量存储初始化（懒加载）
            try:
                # 访问vector_store属性，触发初始化
                if vector_store_service.vector_store:
                    self.log_info(f"向量存储已初始化: 知识库='{knowledge_base_name}'")
                else:
                    self.log_warning(f"向量存储初始化失败: 知识库='{knowledge_base_name}'")
            except Exception as e:
                self.log_error(f"初始化向量存储时出错: {e}")
            
            # 从vector_store_service获取向量仓库实例
            vector_repo = vector_store_service.vector_db_service.vector_repository
            # 执行向量检索
            results = vector_repo.search_vectors(query, k=k, filter=filter, score_threshold=score_threshold)
            
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
    
    def manage_vector_store(self, action: str, params: dict = None, knowledge_base_name="default"):
        """向量数据库管理
        
        Args:
            action (str): 操作类型 (clear, stats, reload)
            params (dict): 操作参数
            knowledge_base_name: 知识库名称
            
        Returns:
            dict: 管理操作结果
        """
        try:
            self.log_info(f"🗄️  开始向量数据库管理操作: action='{action}', 知识库='{knowledge_base_name}'")
            
            # 获取指定知识库的向量存储服务实例
            vector_store_service = self.get_vector_store_service(knowledge_base_name)
            # 从vector_store_service获取向量仓库实例
            vector_repo = vector_store_service.vector_db_service.vector_repository
            
            if action == 'clear':
                # 清空向量数据库
                vector_repo.clear_vector_store()
                self.log_info(f"✅ 向量数据库已清空: 知识库='{knowledge_base_name}'")
                return {'success': True, 'message': '向量数据库已清空'}
            elif action == 'stats':
                # 获取向量数据库统计信息
                stats = vector_repo.get_vector_store_stats()
                self.log_info(f"✅ 获取向量数据库统计信息成功: 知识库='{knowledge_base_name}'")
                return {
                    'success': True,
                    'message': '获取统计信息成功',
                    'stats': stats
                }
            elif action == 'reload':
                # 重新加载向量数据库
                self.log_info(f"🔄 开始重新加载向量数据库: 知识库='{knowledge_base_name}'...")
                # 调用vector_store_service的重新加载方法
                success, message = vector_store_service.reload_vector_store()
                if success:
                    self.log_info(f"✅ 向量数据库重新加载成功: 知识库='{knowledge_base_name}'")
                    return {'success': True, 'message': message}
                else:
                    self.log_error(f"❌ 向量数据库重新加载失败: {message}, 知识库='{knowledge_base_name}'")
                    return {'success': False, 'message': f'向量数据库重新加载失败: {message}'}
            else:
                self.log_warning(f"⚠️  不支持的向量数据库管理操作: {action}")
                return {'success': False, 'message': f'不支持的操作: {action}'}
        except Exception as e:
            self.log_error(f"❌ 向量数据库管理操作失败: {str(e)}")
            return {
                'success': False,
                'message': f'向量数据库管理失败: {str(e)}'
            }
    
    def delete_vectors_by_document_id(self, document_id: str, knowledge_base_name="default"):
        """根据文档ID删除相关向量
        
        Args:
            document_id (str): 文档ID
            knowledge_base_name: 知识库名称
            
        Returns:
            dict: 删除结果
        """
        try:
            self.log_info(f"🗑️  开始删除文档相关向量: document_id='{document_id}', 知识库='{knowledge_base_name}'")
            
            # 获取指定知识库的向量存储服务实例
            vector_store_service = self.get_vector_store_service(knowledge_base_name)
            # 从vector_store_service获取向量仓库实例
            vector_repo = vector_store_service.vector_db_service.vector_repository
            # 删除相关向量
            result = vector_repo.delete_vectors_by_document_id(document_id)
            
            self.log_info(f"✅ 删除文档相关向量成功: 删除 {result.get('deleted_count', 0)} 个向量, 知识库='{knowledge_base_name}'")
            
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
    
    def delete_vectors_by_folder_id(self, folder_id: str, knowledge_base_name="default"):
        """根据文件夹ID删除相关向量
        
        Args:
            folder_id (str): 文件夹ID
            knowledge_base_name: 知识库名称
            
        Returns:
            dict: 删除结果
        """
        try:
            self.log_info(f"🗑️  开始删除文件夹相关向量: folder_id='{folder_id}', 知识库='{knowledge_base_name}'")
            
            # 获取指定知识库的向量存储服务实例
            vector_store_service = self.get_vector_store_service(knowledge_base_name)
            # 从vector_store_service获取向量仓库实例
            vector_repo = vector_store_service.vector_db_service.vector_repository
            # 删除相关向量
            result = vector_repo.delete_vectors_by_folder_id(folder_id)
            
            self.log_info(f"✅ 删除文件夹相关向量成功: 删除 {result.get('deleted_count', 0)} 个向量, 知识库='{knowledge_base_name}'")
            
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
            knowledge_base_name = "default"
            vector_db_path = None
            embedder_model = None
            
            if folder_id:
                try:
                    from app.core.service_container import service_container
                    from app.services.file.document_service import DocumentService
                    doc_service = service_container.get_service('document_service')
                    # 获取folder信息
                    folder = doc_service.data_service.get_folder_by_id(folder_id)
                    if folder:
                        if hasattr(folder, 'name'):
                            knowledge_base_name = folder.name
                            self.log_info(f"从folder_id获取知识库名称成功: {knowledge_base_name}")
                        if hasattr(folder, 'vector_db_path'):
                            vector_db_path = folder.vector_db_path
                            self.log_info(f"从folder_id获取向量数据库路径成功: {vector_db_path}")
                        if hasattr(folder, 'embedding_model'):
                            embedder_model = folder.embedding_model
                            self.log_info(f"从folder_id获取嵌入模型成功: {embedder_model}")
                except Exception as e:
                    self.log_warning(f"获取folder信息失败，使用默认知识库: {e}")
            
            self.log_info(f"🔢 开始向量化文档: document_id='{document_id}', 文本块数量={len(split_documents)}, 知识库='{knowledge_base_name}'")
            
            # 为每个分块添加元数据
            for chunk in split_documents:
                chunk.metadata.update(VectorUtils.prepare_document_metadata(
                    document_id=document_id,
                    file_path=file_path,
                    folder_id=folder_id
                ))
            
            # 获取指定知识库的向量存储服务实例
            vector_store_service = self.get_vector_store_service(
                knowledge_base_name=knowledge_base_name,
                vector_db_path=vector_db_path,
                embedder_model=embedder_model
            )
            # 使用vector_store_service的add_documents方法
            success, message = vector_store_service.add_documents(split_documents)
            
            if success:
                self.log_info(f"✅ 文档向量化成功: 生成 {len(split_documents)} 个向量, 知识库='{knowledge_base_name}'")
                return {
                    'vectorized': True,
                    'vector_count': len(split_documents),
                    'message': '文档向量化成功'
                }
            else:
                self.log_error(f"❌ 文档向量化失败: {message}, 知识库='{knowledge_base_name}'")
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
            
            # 获取指定知识库的向量存储服务实例
            vector_store_service = self.get_vector_store_service(knowledge_base_name)
            # 使用vector_store_service的search_documents方法，利用其缓存功能
            results = vector_store_service.search_documents(
                query=query,
                k=k,
                score_threshold=score_threshold,
                search_type=search_type,
                filter=filter
            )
            
            self.log_info(f"✅ 找到 {len(results)} 个相关文档片段, 知识库='{knowledge_base_name}'")
            
            return results
        except Exception as e:
            self.log_error(f"❌ 搜索文档失败: {str(e)}")
            return []
    
    def clear_vector_store(self, knowledge_base_name="default"):
        """清空向量存储
        
        Args:
            knowledge_base_name: 知识库名称
            
        Returns:
            bool: 是否成功清空
        """
        try:
            self.log_info(f"🗑️  开始清空向量存储: 知识库='{knowledge_base_name}'...")
            # 获取指定知识库的向量存储服务实例
            vector_store_service = self.get_vector_store_service(knowledge_base_name)
            success, message = vector_store_service.clear_vector_store()
            self.log_info(f"✅ 向量存储已清空: {message}, 知识库='{knowledge_base_name}'")
            return success
        except Exception as e:
            self.log_error(f"❌ 清空向量存储失败: {str(e)}")
            return False
    
    def get_enhanced_prompt(self, question, rag_config=None, knowledge_base_name="default"):
        """获取增强提示，将查询和检索到的上下文结合
        
        Args:
            question: 用户查询
            rag_config: RAG配置
            knowledge_base_name: 知识库名称
            
        Returns:
            增强后的提示
        """
        if not rag_config or not rag_config.get('enabled', False):
            return question
        
        try:
            # 更新配置
            config = self.config_manager.get('rag', {})
            if rag_config:
                config.update(rag_config)
            
            # 获取指定知识库的向量存储服务实例
            vector_store_service = self.get_vector_store_service(knowledge_base_name)
            # 检查向量存储是否初始化
            if not vector_store_service.vector_store:
                self.log_error(f"向量存储未初始化: 知识库='{knowledge_base_name}'")
                return question
            
            # 执行相似性搜索
            k = config.get('top_k', 3)
            score_threshold = config.get('score_threshold', 0.7)
            
            results = self.search_documents(
                query=question,
                k=k,
                score_threshold=score_threshold,
                knowledge_base_name=knowledge_base_name
            )
            
            if results:
                # 使用PromptManager构建提示
                from app.utils.prompt_manager import prompt_manager
                messages = prompt_manager.build_messages(
                    query=question,
                    context_docs=results,
                    mode='rag'
                )
                prompt = "\n\n".join([msg['content'] for msg in messages])
                return prompt
            
            return question
        except Exception as e:
            self.log_error(f"生成增强提示失败: {str(e)}")
            return question
    
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
                from app.core.service_container import service_container
                from app.services.file.document_service import DocumentService
                doc_service = service_container.get_service('document_service')
                
                # 获取第一个选中的文件夹ID
                first_folder_id = selected_folders[0]
                # 获取文件夹信息
                folder = doc_service.data_service.get_folder_by_id(first_folder_id)
                
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
            filter=filter,
            score_threshold=score_threshold,
            knowledge_base_name=knowledge_base_name,
            vector_db_path=vector_db_path,
            embedder_model=embedder_model
        )
        
        # 转换向量结果为文档列表
        context_docs = []
        if vector_results['success']:
            for result in vector_results['results']:
                # 添加文档到上下文
                context_docs.append(result)
        
        return context_docs, vector_results
