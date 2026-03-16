"""文档加载工具模块 - 提供统一的文档加载接口"""
import os
from typing import List, Any

class DocumentLoader:
    """文档加载器类 - 处理各种格式文档的加载"""
    
    def __init__(self):
        """初始化文档加载器"""
        # 动态导入加载器
        from langchain_community.document_loaders import (
            PyPDFLoader, TextLoader, Docx2txtLoader,
            UnstructuredExcelLoader, UnstructuredMarkdownLoader
        )
        
        # 加载器映射
        self.loader_map = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.doc': Docx2txtLoader,
            '.docx': Docx2txtLoader,
            '.xlsx': UnstructuredExcelLoader,
            '.md': UnstructuredMarkdownLoader,
        }
    
    def load_document(self, file_path: str) -> List[Any]:
        """加载文档并返回文档对象列表
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Any]: 文档对象列表
        """
        # 确定文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.loader_map:
            raise ValueError(f"不支持的文件类型: {ext}")
        
        try:
            # 动态创建加载器实例
            loader_class = self.loader_map[ext]
            
            # 特殊处理
            if ext == '.txt':
                loader = loader_class(file_path, encoding='utf-8')
            else:
                loader = loader_class(file_path)
            
            # 加载文档
            documents = loader.load()
            print(f"📄 加载文档: {os.path.basename(file_path)}")
            
            return documents
        
        except Exception as e:
            print(f"❌ 加载文档失败: {str(e)}")
            raise
    
    def load_directory(self, directory_path: str, recursive: bool = True) -> List[Any]:
        """加载目录中的所有文档
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归加载子目录
            
        Returns:
            List[Any]: 文档对象列表
        """
        print(f"📁 开始加载目录: {directory_path}")
        
        # 动态导入DirectoryLoader
        from langchain_community.document_loaders import DirectoryLoader
        
        # 构建glob模式
        extensions = '|'.join(ext.lstrip('.') for ext in self.loader_map.keys())
        glob_pattern = f"**/*.{{{extensions}}}" if recursive else f"*.{{{extensions}}}"
        
        # 创建目录加载器
        loader = DirectoryLoader(
            path=directory_path,
            glob=glob_pattern,
            show_progress=True
        )
        
        # 加载所有文档
        documents = loader.load()
        print(f"✅ 目录加载完成，共加载 {len(documents)} 个文档")
        
        return documents
    
    def get_supported_extensions(self) -> List[str]:
        """获取所有支持的文件扩展名
        
        Returns:
            List[str]: 支持的文件扩展名列表
        """
        return [ext.lstrip('.') for ext in self.loader_map.keys()]
