"""RAG协调服务 - 协调文档管理、向量管理和生成服务，提供完整的RAG流程"""
import os
import uuid
from app.core.config import config_manager
from app.services.base_service import BaseService
from app.services.rag.document_service import DocumentService
from app.services.vector.vector_service import VectorService
from app.services.rag.generation_service import GenerationService

# 使用config_manager获取标准用户数据目录
user_data_dir = config_manager.get_user_data_dir()
DATA_DIR = os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'files')

class RagCoordinator(BaseService):
    """RAG协调服务类 - 协调各服务之间的交互，提供完整的RAG流程"""
    
    def __init__(self, document_service=None, vector_service=None, generation_service=None):
        """初始化RAG协调服务
        
        Args:
            document_service: 文档管理服务实例，用于依赖注入
            vector_service: 向量服务实例，用于依赖注入
            generation_service: 生成服务实例，用于依赖注入
        """
        self.document_service = document_service or DocumentService()
        self.vector_service = vector_service or VectorService()
        self.generation_service = generation_service or GenerationService()
        
        # 初始化配置
        self.chunk_size = config_manager.get('rag.chunk_size', 1000)
        self.chunk_overlap = config_manager.get('rag.chunk_overlap', 200)
        
        # 延迟初始化LangChain组件，在需要时加载
        self.loader_mapping = None
        self.text_splitter = None
    
    def _init_langchain_components(self):
        """延迟初始化LangChain组件"""
        if self.loader_mapping is None or self.text_splitter is None:
            from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            self.loader_mapping = {
                '.txt': TextLoader,
                '.pdf': PyPDFLoader,
                '.doc': Docx2txtLoader,
                '.docx': Docx2txtLoader
            }
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
    
    def process_document(self, file, folder_id=''):
        """处理文档的完整流程：保存文件 -> 加载文档 -> 分割文档 -> 向量化存储
        
        Args:
            file: 上传的文件对象
            folder_id: 文件夹ID
            
        Returns:
            dict: 处理结果信息
        """
        try:
            self.log_info(f"📋 开始处理文档: 文件名='{file.filename}', folder_id='{folder_id}'")
            
            # 1. 初始化LangChain组件
            self.log_info("🔧 初始化LangChain组件...")
            self._init_langchain_components()
            self.log_info("✅ LangChain组件初始化完成")
            
            # 2. 保存文档到文件系统
            self.log_info("💾 保存文档到文件系统...")
            save_result = self.document_service.save_document(file, folder_id)
            file_path = save_result['full_path']
            self.log_info(f"✅ 文档已保存到: {file_path}")
            
            # 3. 使用LangChain加载器加载文档
            file_ext = os.path.splitext(file_path)[1].lower()
            self.log_info(f"📄 加载文档，文件类型: {file_ext}")
            
            loader_class = self.loader_mapping.get(file_ext)
            
            if not loader_class:
                error_msg = f"不支持的文件类型: {file_ext}"
                self.log_error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # 处理TextLoader的编码问题
            try:
                # 获取TextLoader类的引用
                from langchain_community.document_loaders import TextLoader as TextLoaderClass
                
                if loader_class == TextLoaderClass:
                    # 尝试使用utf-8编码，如果失败则使用其他编码
                    loader = TextLoaderClass(file_path, encoding='utf-8')
                    self.log_info("📑 使用utf-8编码加载文本文件")
                    documents = loader.load()
                else:
                    loader = loader_class(file_path)
                    documents = loader.load()
                self.log_info(f"✅ 成功加载文档，共 {len(documents)} 个文档对象")
            except UnicodeDecodeError:
                # 如果utf-8失败，尝试使用gbk编码（常见中文编码）
                from langchain_community.document_loaders import TextLoader as TextLoaderClass
                
                if loader_class == TextLoaderClass:
                    loader = TextLoaderClass(file_path, encoding='gbk')
                    self.log_info("📑 utf-8编码失败，尝试使用gbk编码加载文本文件")
                    documents = loader.load()
                    self.log_info(f"✅ 使用gbk编码成功加载文档，共 {len(documents)} 个文档对象")
                else:
                    raise
            except Exception as e:
                # 捕获所有文档加载错误
                error_msg = f"文档加载失败: {str(e)}"
                self.log_error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'file_path': file_path
                }
            
            # 4. 使用LangChain文本分割器分割文档
            self.log_info("✂️  开始分割文档...")
            split_documents = self.text_splitter.split_documents(documents)
            self.log_info(f"✅ 文档分割完成，生成 {len(split_documents)} 个文本块")
            
            # 5. 向量化并存储到向量数据库
            self.log_info("🔢 开始向量化文档...")
            document_id = str(uuid.uuid4())
            vector_result = self.vector_service.vectorize_documents(
                split_documents,
                document_id,
                file_path
            )
            
            if vector_result['vectorized']:
                self.log_info(f"✅ 向量化成功，生成 {vector_result['vector_count']} 个向量")
            else:
                self.log_warning(f"⚠️  向量化部分失败: {vector_result.get('error', '未知错误')}")
            
            # 6. 准备返回信息
            document_info = {
                'document_id': document_id,
                'file_path': file_path,
                'filename': save_result['filename'],
                'split_documents_count': len(split_documents),
                'chunk_size': config_manager.get('rag.chunk_size', 1000),
                'chunk_overlap': config_manager.get('rag.chunk_overlap', 200),
                'sample_chunks': [doc.page_content for doc in split_documents[:2]]
            }
            
            chunk_info = {
                'total_chunks': len(split_documents),
                'chunk_size': config_manager.get('rag.chunk_size', 1000),
                'chunk_overlap': config_manager.get('rag.chunk_overlap', 200)
            }
            
            self.log_info(f"📊 文档处理完成: 文件='{file.filename}', 文本块={len(split_documents)}, 向量={vector_result['vector_count']}")
            
            return {
                'success': True,
                'document_info': document_info,
                'chunk_info': chunk_info,
                'vector_info': vector_result,
                'file_save_result': save_result
            }
        except Exception as e:
            error_msg = f"处理文档失败: {str(e)}"
            self.log_error(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def rag_pipeline(self, query, llm=None):
        """执行完整的RAG流程：搜索相关文档 -> 构建提示 -> 生成响应
        
        Args:
            query: 用户查询
            llm: LLM实例，用于依赖注入
            
        Returns:
            dict: RAG流程执行结果
        """
        try:
            self.log_info(f"🚀 开始RAG对话流程: 查询='{query[:50]}{'...' if len(query) > 50 else ''}'")
            
            # 1. 搜索相关文档
            self.log_info("🔍 正在搜索相关文档...")
            context_docs = self.vector_service.search_documents(
                query=query,
                k=config_manager.get('rag.top_k', 3),
                score_threshold=config_manager.get('rag.score_threshold', 0.7),
                search_type=config_manager.get('rag.search_type', 'similarity')
            )
            
            self.log_info(f"✅ 找到 {len(context_docs)} 个相关文档片段")
            
            # 2. 生成RAG响应
            self.log_info("📝 正在生成RAG响应...")
            rag_result = self.generation_service.generate_rag_response(
                query=query,
                context_docs=context_docs,
                llm=llm
            )
            
            return {
                'success': True,
                'rag_result': rag_result,
                'context_docs': context_docs,
                'context_count': len(context_docs)
            }
        except Exception as e:
            self.log_error(f"RAG流程执行失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def reload_documents(self):
        """重新加载所有文档到向量库
        
        Returns:
            bool: 重新加载是否成功
        """
        try:
            # 1. 初始化LangChain组件
            self._init_langchain_components()
            
            # 2. 清空向量库
            self.vector_service.clear_vector_store()
            
            # 3. 使用LangChain DirectoryLoader加载所有文档
            from langchain_community.document_loaders import DirectoryLoader
            loader = DirectoryLoader(
                path=DATA_DIR,
                glob="*.*",
                show_progress=True,
                use_multithreading=True
            )
            
            # 4. 加载所有文档
            documents = loader.load()
            processed_files = len(documents)
            
            if not documents:
                self.log_info("✅ 没有文档需要加载")
                return True
            
            # 5. 使用LangChain执行文本分割
            split_documents = self.text_splitter.split_documents(documents)
            
            # 5. 向量化并添加到向量库
            vector_result = self.vector_service.vectorize_documents(
                split_documents,
                "batch_reload",
                "batch_reload"
            )
            
            # 6. 输出统计信息
            loaded_chunks = len(split_documents) if vector_result['vectorized'] else 0
            failed_files = processed_files - loaded_chunks if vector_result['vectorized'] else processed_files
            
            self.log_info(f"✅ 重新加载文档完成:")
            self.log_info(f"   - 处理文件数: {processed_files}")
            self.log_info(f"   - 成功加载: {processed_files - failed_files}")
            self.log_info(f"   - 加载失败: {failed_files}")
            self.log_info(f"   - 总向量数: {loaded_chunks}")
            
            return vector_result['vectorized']
        except Exception as e:
            self.log_error(f"重新加载文档失败: {e}")
            return False
    
    def delete_document(self, filename, folder_name=''):
        """删除文档并更新向量库
        
        Args:
            filename: 文件名
            folder_name: 文件夹名称
            
        Returns:
            dict: 删除操作结果
        """
        try:
            # 1. 删除文档文件
            delete_result = self.document_service.delete_document(filename, folder_name)
            
            # 2. 重新加载向量库
            self.reload_documents()
            
            return delete_result
        except Exception as e:
            self.log_error(f"删除文档失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_all_documents(self):
        """删除所有文档并清空向量库
        
        Returns:
            dict: 删除操作结果
        """
        try:
            # 1. 删除所有文档文件
            delete_result = self.document_service.delete_all_documents()
            
            # 2. 清空向量库
            vector_result = self.vector_service.clear_vector_store()
            
            # 3. 更新返回消息
            if vector_result:
                delete_result['message'] = f"{delete_result['message']}，并清空了向量数据库"
            else:
                delete_result['message'] = f"{delete_result['message']}，但清空向量数据库失败"
            
            return delete_result
        except Exception as e:
            self.log_error(f"删除所有文档失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_folder(self, folder_name):
        """删除文件夹并更新向量库
        
        Args:
            folder_name: 文件夹名称
            
        Returns:
            dict: 删除操作结果
        """
        try:
            # 1. 删除文件夹
            delete_result = self.document_service.delete_folder(folder_name)
            
            # 2. 重新加载向量库
            if delete_result.get('success', True):
                self.reload_documents()
            
            return delete_result
        except Exception as e:
            self.log_error(f"删除文件夹失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
