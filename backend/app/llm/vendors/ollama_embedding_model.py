"""Ollama 嵌入模型实现"""
from app.llm.base.base_embedding_model import BaseEmbeddingModel
from typing import List


class OllamaEmbeddingModel(BaseEmbeddingModel):
    """Ollama 嵌入模型实现"""
    
    def __init__(self, model_name: str, base_url: str = None):
        """初始化 Ollama 嵌入模型
        
        Args:
            model_name (str): 模型名称
            base_url (str): Ollama API 基础 URL
        """
        self._model_name = model_name
        self._base_url = base_url
        self._embeddings = None
        self._dimension = None
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化模型"""
        try:
            # 尝试使用推荐的 langchain-ollama 包
            try:
                from langchain_ollama import OllamaEmbeddings
            except ImportError:
                # 兼容旧版本
                from langchain_community.embeddings import OllamaEmbeddings
            
            # 构建参数
            params = {
                'model': self._model_name
            }
            
            if self._base_url:
                params['base_url'] = self._base_url
            
            self._embeddings = OllamaEmbeddings(**params)
            
            # 计算向量维度
            test_vector = self.embed_query("测试文本")
            self._dimension = len(test_vector)
        except ImportError as e:
            raise ValueError(f"未安装必要的包: {str(e)}")
        except Exception as e:
            raise ValueError(f"初始化 Ollama 嵌入模型失败: {str(e)}")
    
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
