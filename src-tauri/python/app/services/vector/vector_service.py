"""向量服务 - 负责文档的向量化、向量存储和向量检索"""
import os
import uuid
from app.core.config import config_manager
from app.services.base_service import BaseService
from app.services.vector.vector_store_service import VectorStoreService
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository

# 使用config_manager获取标准用户数据目录
user_data_dir = config_manager.get_user_data_dir()
VECTOR_DB_PATH = os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'vectorDb')

class VectorService(BaseService):
    """向量服务类 - 封装所有与向量数据库相关的操作"""
    
    def __init__(self, vector_store_service=None):
        """初始化向量服务
        
        Args:
            vector_store_service: 向量存储服务实例，用于依赖注入
        """
        self.vector_store_service = vector_store_service or VectorStoreService.get_instance(
            vector_db_path=VECTOR_DB_PATH,
            embedder_model=config_manager.get('rag.embedder_model', 'all-MiniLM-L6-v2')
        )
        # 初始化文档分块和文档Repository
        self.document_chunk_repo = DocumentChunkRepository()
        self.document_repo = DocumentRepository()
    
    def vectorize_documents(self, documents, document_id, source_file, folder_id=''):
        """将文档向量化并存储到向量数据库
        
        Args:
            documents: 文档列表
            document_id: 文档ID
            source_file: 源文件路径
            folder_id: 文件夹ID
            
        Returns:
            dict: 向量化结果信息
        """
        try:
            self.log_info(f"🔄 开始向量化: 文档ID='{document_id}', 源文件='{os.path.basename(source_file)}', 文档片段数={len(documents)}")
            
            # 验证文档是否适合向量化
            if not documents:
                self.log_warning("⚠️  没有可向量化的文档片段")
                return {
                    'vectorized': False,
                    'error': "没有可向量化的文档片段"
                }
            
            # 简单验证：检查文档片段内容长度
            warnings = []
            for i, doc in enumerate(documents):
                if hasattr(doc, 'page_content') and len(doc.page_content) < 10:
                    warnings.append(f"文档片段 {i+1} 内容过短，可能影响向量化质量")
                elif isinstance(doc, dict) and 'page_content' in doc and len(doc['page_content']) < 10:
                    warnings.append(f"文档片段 {i+1} 内容过短，可能影响向量化质量")
            
            if warnings:
                for warning in warnings:
                    self.log_warning(f"⚠️ {warning}")
            
            # 为每个文档片段添加folder_id到metadata中
            processed_documents = []
            for doc in documents:
                # 复制文档对象
                processed_doc = doc.copy() if isinstance(doc, dict) else doc
                
                # 确保文档有metadata属性
                if hasattr(processed_doc, 'metadata'):
                    # 将folder_id添加到metadata
                    processed_doc.metadata['folder_id'] = folder_id
                elif isinstance(processed_doc, dict) and 'metadata' in processed_doc:
                    # 处理字典类型的文档
                    processed_doc['metadata']['folder_id'] = folder_id
                else:
                    # 如果没有metadata，创建一个
                    if hasattr(processed_doc, 'page_content'):
                        processed_doc.metadata = {'folder_id': folder_id}
                    elif isinstance(processed_doc, dict) and 'page_content' in processed_doc:
                        processed_doc['metadata'] = {'folder_id': folder_id}
                
                processed_documents.append(processed_doc)
            
            # 执行向量化操作
            self.log_info(f"🚀 开始向量化 {len(processed_documents)} 个文档片段...")
            vectorized = self.vector_store_service.add_documents(processed_documents)
            
            if vectorized:
                self.log_info(f"✅ 成功向量化 {len(processed_documents)} 个文档片段")
                
                # 将文档分块信息保存到数据库
                for i, doc in enumerate(processed_documents):
                    # 生成分块ID
                    chunk_id = str(uuid.uuid4())[:16]
                    
                    # 获取分块内容
                    content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                    
                    # 获取分块元数据
                    extra_metadata = str(doc.metadata) if hasattr(doc, 'metadata') else '{}'
                    
                    # 保存分块信息到数据库
                    self.document_chunk_repo.create_chunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        chunk_index=i,
                        content=content,
                        extra_metadata=extra_metadata,
                        vector_collection=self.vector_store_service.knowledge_base_name
                    )
                    
                self.log_info(f"✅ 成功将 {len(documents)} 个文档分块信息保存到数据库")
            else:
                self.log_info(f"⚠️  向量化失败")
            
            # 准备返回信息
            vector_info = {
                'vectorized': vectorized,
                'vector_count': len(documents) if vectorized else 0,
                'embedding_model': config_manager.get('rag.embedder_model', 'all-MiniLM-L6-v2'),
                'vector_store_type': 'chroma',
                'document_id': document_id,
                'source_file': source_file
            }
            
            # 创建并添加向量化元数据
            vector_metadata = {
                'document_count': len(documents),
                'total_tokens_estimate': sum(len(doc.page_content) // 4 for doc in documents) if hasattr(documents[0], 'page_content') else 0,
                'source_file': source_file,
                'document_id': document_id
            }
            vector_info['vector_metadata'] = vector_metadata
            
            self.log_info(f"📊 向量化完成: 向量数={vector_info['vector_count']}, 模型={vector_info['embedding_model']}")
            
            return vector_info
        except Exception as e:
            self.log_error(f"❌ 向量化处理失败: {str(e)}")
            return {
                'vectorized': False,
                'error': str(e)
            }
    
    def search_documents(self, query, k=5, score_threshold=None, search_type="similarity", fetch_k=20, filter=None):
        """搜索相关文档
        
        Args:
            query: 查询文本
            k: 返回结果数量
            score_threshold: 相似度分数阈值，低于该阈值的结果将被过滤
            search_type: 搜索类型，可选值：similarity, mmr, similarity_score_threshold
            fetch_k: 用于MMR搜索的候选文档数量
            filter: 元数据过滤器，用于过滤特定条件的文档
            
        Returns:
            list: 相关文档列表
        """
        try:
            results = self.vector_store_service.search_documents(
                query=query,
                k=k,
                score_threshold=score_threshold,
                search_type=search_type,
                fetch_k=fetch_k,
                filter=filter
            )
            return results
        except Exception as e:
            self.log_error(f"搜索文档失败: {str(e)}")
            return []
    
    def get_vector_statistics(self):
        """获取向量库统计信息"""
        try:
            stats = self.vector_store_service.get_vector_statistics()
            return stats
        except Exception as e:
            self.log_error(f"获取向量库统计信息失败: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'total_vectors': 0
            }
    
    def clear_vector_store(self):
        """清空向量库"""
        try:
            result = self.vector_store_service.clear_vector_store()
            return result
        except Exception as e:
            self.log_error(f"清空向量库失败: {str(e)}")
            return False
    
    def get_vector_store(self):
        """获取向量存储实例"""
        try:
            return self.vector_store_service.vector_store
        except Exception as e:
            self.log_error(f"获取向量存储实例失败: {str(e)}")
            return None
    
    def get_retriever(self, search_type="similarity", top_k=3, score_threshold=0.7):
        """获取配置好的检索器"""
        try:
            retriever = self.vector_store_service.vector_store.as_retriever(
                search_type=search_type,
                search_kwargs={
                    'k': top_k,
                    'score_threshold': score_threshold
                }
            )
            return retriever
        except Exception as e:
            self.log_error(f"获取检索器失败: {str(e)}")
            return None
