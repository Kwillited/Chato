"""向量处理工具类，提供统一的向量管理功能"""
from app.core.logger import logger

class VectorUtils:
    """向量处理工具类，封装所有向量相关方法"""
    
    @staticmethod
    def format_vector_results(results):
        """
        格式化向量检索结果
        
        参数:
            results: 原始向量检索结果
            
        返回:
            格式化后的结果列表
        """
        formatted_results = []
        for result in results:
            # 提取score属性（如果存在）
            score = getattr(result, 'score', None)
            formatted_results.append({
                'content': result.page_content,
                'metadata': result.metadata,
                'score': score
            })
        return formatted_results
    
    @staticmethod
    def build_vector_filter(folder_ids=None, document_ids=None):
        """
        构建向量检索过滤器
        
        参数:
            folder_ids: 文件夹ID列表
            document_ids: 文档ID列表
            
        返回:
            过滤器字典
        """
        filter_conditions = {}
        
        if folder_ids:
            filter_conditions['folder_id'] = {'$in': folder_ids}
        
        if document_ids:
            filter_conditions['document_id'] = {'$in': document_ids}
        
        return filter_conditions if filter_conditions else None
    
    @staticmethod
    def validate_vector_config(config):
        """
        验证向量配置
        
        参数:
            config: 向量配置字典
            
        返回:
            tuple: (是否验证通过, 错误信息)
        """
        required_fields = ['embedding_model', 'vector_store']
        
        for field in required_fields:
            if field not in config:
                return False, f'缺少向量配置字段: {field}'
            if not config[field]:
                return False, f'向量配置字段 {field} 不能为空'
        
        return True, None
    
    @staticmethod
    def calculate_vector_statistics(vectors):
        """
        计算向量统计信息
        
        参数:
            vectors: 向量列表
            
        返回:
            统计信息字典
        """
        if not vectors:
            return {
                'total_vectors': 0,
                'average_dimension': 0,
                'total_size': 0
            }
        
        total_vectors = len(vectors)
        average_dimension = 0
        total_size = 0
        
        if vectors:
            # 假设每个向量都有维度属性
            dimensions = [len(vector) if hasattr(vector, '__len__') else 0 for vector in vectors]
            average_dimension = sum(dimensions) / total_vectors
            # 假设每个向量的大小为维度 * 4字节（float32）
            total_size = sum(dim * 4 for dim in dimensions)
        
        return {
            'total_vectors': total_vectors,
            'average_dimension': average_dimension,
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024)
        }
    
    @staticmethod
    def get_vector_store_info(vector_store):
        """
        获取向量存储信息
        
        参数:
            vector_store: 向量存储实例
            
        返回:
            向量存储信息字典
        """
        try:
            info = {
                'type': type(vector_store).__name__,
                'initialized': True
            }
            
            # 尝试获取向量存储的统计信息
            if hasattr(vector_store, 'get_stats'):
                info['stats'] = vector_store.get_stats()
            elif hasattr(vector_store, 'count'):
                info['vector_count'] = vector_store.count()
            
            return info
        except Exception as e:
            logger.error(f"获取向量存储信息失败: {str(e)}")
            return {
                'type': 'Unknown',
                'initialized': False,
                'error': str(e)
            }
    
    @staticmethod
    def prepare_document_metadata(document_id, file_path, folder_id='', **kwargs):
        """
        准备文档元数据
        
        参数:
            document_id: 文档ID
            file_path: 文件路径
            folder_id: 文件夹ID
            **kwargs: 其他元数据
            
        返回:
            元数据字典
        """
        metadata = {
            'document_id': document_id,
            'file_path': file_path,
            'folder_id': folder_id
        }
        
        # 添加额外的元数据
        metadata.update(kwargs)
        
        return metadata
