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
            # 打印传入的默认参数
            print(f"[TextSplitter] 传入的默认参数: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
            
            # 从文档对象中获取分块参数，优先使用文档自身的参数
            # 如果文档没有参数，则使用传入的默认值
            doc_chunk_size = chunk_size
            doc_chunk_overlap = chunk_overlap
            
            # 检查第一个文档是否有分块参数
            if documents and hasattr(documents[0], 'chunk_size') and documents[0].chunk_size:
                doc_chunk_size = documents[0].chunk_size
                print(f"[TextSplitter] 从文档获取的参数: chunk_size={doc_chunk_size}")
            if documents and hasattr(documents[0], 'chunk_overlap') and documents[0].chunk_overlap:
                doc_chunk_overlap = documents[0].chunk_overlap
                print(f"[TextSplitter] 从文档获取的参数: chunk_overlap={doc_chunk_overlap}")
            
            # 如果文档没有参数，检查是否有folder_id并从文件夹获取
            if (not doc_chunk_size or not doc_chunk_overlap) and documents and hasattr(documents[0], 'folder_id') and documents[0].folder_id:
                from app.services.data_service import DataService
                data_service = DataService()
                folder = data_service.get_folder_by_id(documents[0].folder_id)
                if folder:
                    if hasattr(folder, 'chunk_size') and folder.chunk_size:
                        doc_chunk_size = folder.chunk_size
                        print(f"[TextSplitter] 从文件夹获取的参数: chunk_size={doc_chunk_size}")
                    if hasattr(folder, 'chunk_overlap') and folder.chunk_overlap:
                        doc_chunk_overlap = folder.chunk_overlap
                        print(f"[TextSplitter] 从文件夹获取的参数: chunk_overlap={doc_chunk_overlap}")
            
            # 打印最终使用的参数
            print(f"[TextSplitter] 最终使用的参数: chunk_size={doc_chunk_size}, chunk_overlap={doc_chunk_overlap}")
            
            # 更新结果中的分块参数
            result['chunk_size'] = doc_chunk_size
            result['chunk_overlap'] = doc_chunk_overlap
            
            # 创建文本分割器
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=doc_chunk_size,
                chunk_overlap=doc_chunk_overlap,
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