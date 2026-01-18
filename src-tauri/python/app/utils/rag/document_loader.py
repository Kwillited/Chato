"""文档加载工具模块 - 提供统一的文档加载接口"""
import os
import time
from typing import List, Dict, Any
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, Docx2txtLoader, DirectoryLoader
)

class DocumentLoader:
    """文档加载器类 - 处理各种格式文档的加载"""
    
    # 支持的文件扩展名及其对应的加载器
    SUPPORTED_EXTENSIONS = {
        'txt': TextLoader,
        'pdf': PyPDFLoader,
        'doc': Docx2txtLoader,
        'docx': Docx2txtLoader
    }
    
    # 文档缓存，格式: {file_path: (mtime, document_info)}  
    _cache = {}
    # 缓存过期时间（秒）
    _CACHE_EXPIRY = 300  # 5分钟
    
    @staticmethod
    def load_document(file_path: str) -> Dict[str, Any]:
        """加载文档并返回文档信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 包含文档内容和元信息的字典
        """
        # 检查缓存
        current_mtime = os.path.getmtime(file_path)
        
        # 检查缓存中是否有该文件，且未过期，且文件未修改
        if file_path in DocumentLoader._cache:
            cached_mtime, cached_info, cached_timestamp = DocumentLoader._cache[file_path]
            if cached_mtime == current_mtime and (time.time() - cached_timestamp) < DocumentLoader._CACHE_EXPIRY:
                print(f"📦 使用缓存的文档: {os.path.basename(file_path)}")
                return cached_info
        
        documents = []
        file_extension = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
        
        try:
            # 根据文件类型选择合适的加载器
            if file_extension in DocumentLoader.SUPPORTED_EXTENSIONS:
                loader_class = DocumentLoader.SUPPORTED_EXTENSIONS[file_extension]
                
                # TextLoader需要指定编码
                if file_extension == 'txt':
                    loader = loader_class(file_path, encoding='utf-8')
                else:
                    loader = loader_class(file_path)
                
                documents = loader.load()
            
            # 记录文档信息
            document_info = {
                'total_docs': len(documents),
                'page_count': sum(1 for doc in documents) if documents else 0,
                'file_path': file_path,
                'file_extension': file_extension
            }
            
            # 如果有文档，添加一些基本信息
            if documents:
                first_doc = documents[0]
                document_info['first_page_content_length'] = len(first_doc.page_content)
                document_info['metadata'] = first_doc.metadata
                document_info['documents'] = documents
            
            # 缓存结果
            DocumentLoader._cache[file_path] = (current_mtime, document_info, time.time())
            print(f"📄 加载文档: {os.path.basename(file_path)}")
            
        except Exception as e:
            document_info = {
                'error': str(e),
                'total_docs': 0,
                'page_count': 0,
                'file_path': file_path,
                'file_extension': file_extension
            }
            # 错误信息也缓存
            DocumentLoader._cache[file_path] = (current_mtime, document_info, time.time())
        
        return document_info
    
    @staticmethod
    def load_directory(directory_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """使用LangChain DirectoryLoader加载整个目录的文档
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归加载子目录
            
        Returns:
            List[Dict]: 包含所有文档信息的字典列表
        """
        print(f"📁 开始加载目录: {directory_path}")
        
        # 创建目录加载器
        loader = DirectoryLoader(
            path=directory_path,
            glob="**/*.{txt,pdf,doc,docx}" if recursive else "*.{txt,pdf,doc,docx}",
            show_progress=True
        )
        
        # 加载所有文档
        documents = loader.load()
        print(f"✅ 目录加载完成，共加载 {len(documents)} 个文档")
        
        # 转换为统一的文档信息格式
        result = []
        for i, doc in enumerate(documents):
            file_path = doc.metadata.get('source', f"file_{i}")
            file_extension = os.path.splitext(file_path)[1].lower().lstrip('.') if '.' in file_path else ''
            
            document_info = {
                'total_docs': 1,
                'page_count': 1,
                'file_path': file_path,
                'file_extension': file_extension,
                'first_page_content_length': len(doc.page_content),
                'metadata': doc.metadata,
                'documents': [doc]
            }
            
            result.append(document_info)
        
        return result
    
    @staticmethod
    def clear_cache() -> None:
        """清除所有缓存的文档信息"""
        DocumentLoader._cache.clear()
        print(f"🗑️  已清除所有文档缓存")
    
    @staticmethod
    def remove_from_cache(file_path: str) -> None:
        """从缓存中移除指定文件
        
        Args:
            file_path: 文件路径
        """
        if file_path in DocumentLoader._cache:
            del DocumentLoader._cache[file_path]
            print(f"🗑️  已从缓存中移除文件: {os.path.basename(file_path)}")
    
    @staticmethod
    def get_supported_extensions() -> List[str]:
        """获取所有支持的文件扩展名
        
        Returns:
            List[str]: 支持的文件扩展名列表
        """
        return list(DocumentLoader.SUPPORTED_EXTENSIONS.keys())