"""基础嵌入模型类"""
from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingModel(ABC):
    """基础嵌入模型抽象类"""
    
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """为查询文本生成嵌入向量
        
        Args:
            query (str): 查询文本
            
        Returns:
            List[float]: 嵌入向量
        """
        pass
    
    @abstractmethod
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """为多个文档生成嵌入向量
        
        Args:
            documents (List[str]): 文档列表
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """模型名称"""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """嵌入向量维度"""
        pass
