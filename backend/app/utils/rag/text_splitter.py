"""文本分割工具模块 - 提供文档内容分割功能"""
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
            list: 分割后的文档对象列表
        """
        if not documents:
            return []
        
        # 从文档对象的metadata中获取folder_id，然后从数据库获取分块参数
        doc_chunk_size = chunk_size
        doc_chunk_overlap = chunk_overlap
        
        if documents:
            # 检查文档的metadata中是否有folder_id
            folder_id = None
            if hasattr(documents[0], 'metadata') and documents[0].metadata:
                folder_id = documents[0].metadata.get('folder_id')
            
            # 如果有folder_id，从数据库获取文件夹信息
            if folder_id:
                from app.services.data_service import DataService
                data_service = DataService()
                folder = data_service.get_folder_by_id(folder_id)
                if folder:
                    if hasattr(folder, 'chunk_size') and folder.chunk_size:
                        doc_chunk_size = folder.chunk_size
                    if hasattr(folder, 'chunk_overlap') and folder.chunk_overlap:
                        doc_chunk_overlap = folder.chunk_overlap
        
        # 创建文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=doc_chunk_size,
            chunk_overlap=doc_chunk_overlap
        )
        
        # 执行文本分割
        return text_splitter.split_documents(documents)
    
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
            chunk_overlap=chunk_overlap
        )
        
        return text_splitter.split_text(text)