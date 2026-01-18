"""向量服务模块 - 封装文档向量化相关的功能"""
import logging
from typing import List, Dict, Optional, Any
from langchain_core.documents import Document
from app.services.vector.vector_store_service import VectorStoreService

class VectorService:
    """向量服务类 - 封装文档向量化、向量检索等功能"""
    
    @staticmethod
    def get_vector_statistics() -> Dict:
        """获取向量库统计信息
        
        Returns:
            Dict: 向量库统计信息
        """
        stats = {
            'total_vectors': 0,
            'total_documents': 0,
            'embedding_model': None,
            'vector_store_type': None,
            'vector_store_path': None,
            'status': 'unavailable'
        }
        
        try:
            # 使用VectorStoreService获取统计信息
            vector_service = VectorStoreService.get_instance()
            if not vector_service:
                return stats
            
            # 从VectorStoreService获取信息
            stats['embedding_model'] = vector_service.embedding_model_name
            stats['vector_store_type'] = vector_service.vector_store_type
            stats['vector_store_path'] = vector_service.vector_store_path
            
            # 尝试获取向量计数
            try:
                stats['total_vectors'] = len(vector_service.vector_store.get()['ids'])
            except:
                stats['total_vectors'] = 0
            
            stats['status'] = 'available'
            
        except Exception as e:
            logging.error(f"获取向量库统计信息失败: {str(e)}")
        
        return stats
    
    @staticmethod
    def create_vector_metadata(documents: List[Document], 
                             source_file: str = None,
                             document_id: str = None) -> Dict:
        """为向量化文档创建元数据
        
        Args:
            documents: 文档列表
            source_file: 源文件路径
            document_id: 文档ID
            
        Returns:
            Dict: 向量化元数据
        """
        metadata = {
            'document_count': len(documents),
            'total_tokens_estimate': sum(len(doc.page_content) // 4 for doc in documents),  # 粗略估计tokens
            'source_file': source_file,
            'document_id': document_id
        }
        
        # 收集文档类型统计
        document_types = {}
        for doc in documents:
            doc_type = doc.metadata.get('type', 'unknown')
            document_types[doc_type] = document_types.get(doc_type, 0) + 1
        metadata['document_types'] = document_types
        
        return metadata
    
    @staticmethod
    def validate_vectors(documents: List[Document]) -> Dict[str, Any]:
        """验证文档是否适合向量化
        
        Args:
            documents: 文档列表
            
        Returns:
            Dict: 验证结果，包含是否有效和可能的警告
        """
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        if not documents:
            validation['is_valid'] = False
            validation['errors'].append('文档列表为空')
            return validation
        
        # 检查每个文档
        for i, doc in enumerate(documents):
            if not hasattr(doc, 'page_content') or not doc.page_content:
                validation['is_valid'] = False
                validation['errors'].append(f'文档 {i} 没有内容')
            elif len(doc.page_content) < 10:  # 内容过短的警告
                validation['warnings'].append(f'文档 {i} 内容过短，可能影响向量化质量')
            
            # 检查元数据
            if not hasattr(doc, 'metadata'):
                validation['warnings'].append(f'文档 {i} 没有元数据')
        
        return validation