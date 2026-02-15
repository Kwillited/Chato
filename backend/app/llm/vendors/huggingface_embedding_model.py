"""HuggingFace 嵌入模型实现"""
from app.llm.base.base_embedding_model import BaseEmbeddingModel
from typing import List, Dict, Any


class HuggingFaceEmbeddingModel(BaseEmbeddingModel):
    """HuggingFace 嵌入模型实现"""
    
    def __init__(self, model_name: str, model_kwargs: Dict[str, Any] = None, encode_kwargs: Dict[str, Any] = None):
        """初始化 HuggingFace 嵌入模型
        
        Args:
            model_name (str): 模型名称或路径
            model_kwargs (Dict[str, Any]): 模型参数
            encode_kwargs (Dict[str, Any]): 编码参数
        """
        self._model_name = model_name
        self._model_kwargs = model_kwargs or {'device': 'cpu'}
        self._encode_kwargs = encode_kwargs or {'normalize_embeddings': True}
        self._embeddings = None
        self._dimension = None
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化模型"""
        try:
            # 尝试导入 HuggingFaceEmbeddings
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                from langchain_community.embeddings import HuggingFaceEmbeddings
            
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self._model_name,
                model_kwargs=self._model_kwargs,
                encode_kwargs=self._encode_kwargs
            )
            
            # 计算向量维度
            test_vector = self.embed_query("测试文本")
            self._dimension = len(test_vector)
        except Exception as e:
            raise ValueError(f"初始化 HuggingFace 嵌入模型失败: {str(e)}")
    
    def embed_query(self, query: str) -> List[float]:
        """为查询文本生成嵌入向量
        
        Args:
            query (str): 查询文本
            
        Returns:
            List[float]: 嵌入向量
        """
        if not self._embeddings:
            raise ValueError("模型未初始化")
        return self._embeddings.embed_query(query)
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """为多个文档生成嵌入向量
        
        Args:
            documents (List[str]): 文档列表
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        if not self._embeddings:
            raise ValueError("模型未初始化")
        return self._embeddings.embed_documents(documents)
    
    @property
    def model_name(self) -> str:
        """模型名称"""
        return self._model_name
    
    @property
    def dimension(self) -> int:
        """嵌入向量维度"""
        return self._dimension
