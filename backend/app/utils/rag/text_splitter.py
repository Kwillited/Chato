"""文本分割工具模块 - 提供文档内容分割功能"""
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:
    """文本分割器工具类 - 提供文档内容分割相关功能"""
    
    @staticmethod
    def split_documents(documents, chunk_size=1000, chunk_overlap=200):
        """分割文档为文本块
        
        Args:
            documents: Document对象列表
            chunk_size: 文本块大小
            chunk_overlap: 文本块重叠大小
            
        Returns:
            dict: 包含分割结果和元数据的字典
        """
        # 初始化返回结果
        result = {
            'success': True,
            'original_documents_count': len(documents) if documents else 0,
            'split_documents_count': 0,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap,
            'document_id': str(uuid.uuid4())[:8],
            'sample_chunks': [],
            'split_documents': [],  # 存储分割后的文档对象
            'error': None
        }
        
        if not documents:
            result['error'] = '没有可分割的文档'
            result['success'] = False
            return result
        
        try:
            # 创建文本分割器
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", " ", ".", ",", ";"]
            )
            
            # 执行文本分割
            split_documents = text_splitter.split_documents(documents)
            result['split_documents_count'] = len(split_documents)
            result['split_documents'] = split_documents
            
            # 生成样本块信息
            result['sample_chunks'] = TextSplitter._generate_sample_chunks(split_documents)
            
        except Exception as e:
            # 处理分割错误
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    @staticmethod
    def _generate_sample_chunks(split_documents, max_samples=3, preview_length=100):
        """生成样本块信息
        
        Args:
            split_documents: 分割后的文档列表
            max_samples: 最大样本数量
            preview_length: 预览内容长度
            
        Returns:
            list: 样本块信息列表
        """
        sample_chunks = []
        
        # 只取前几个文档作为样本
        for i, chunk in enumerate(split_documents[:max_samples]):
            content_preview = chunk.page_content[:preview_length]
            if len(chunk.page_content) > preview_length:
                content_preview += '...'
            
            # 收集元数据
            metadata = chunk.metadata.copy() if hasattr(chunk, 'metadata') else {}
            
            sample_chunks.append({
                'chunk_id': i + 1,
                'content_preview': content_preview,
                'metadata': metadata,
                'length': len(chunk.page_content)
            })
        
        return sample_chunks
    
    @staticmethod
    def split_text(text, chunk_size=1000, chunk_overlap=200):
        """直接分割文本字符串
        
        Args:
            text: 要分割的文本字符串
            chunk_size: 文本块大小
            chunk_overlap: 文本块重叠大小
            
        Returns:
            list: 文本块列表
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ".", ",", ";"]
        )
        
        chunks = text_splitter.split_text(text)
        return chunks