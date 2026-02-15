"""OpenAI 嵌入模型实现"""
from app.llm.base.base_embedding_model import BaseEmbeddingModel
from typing import List, Dict, Any


class OpenAIEmbeddingModel(BaseEmbeddingModel):
    """OpenAI 嵌入模型实现"""
    
    def __init__(self, model_name: str, api_key: str = None, api_base_url: str = None):
        """初始化 OpenAI 嵌入模型
        
        Args:
            model_name (str): 模型名称
            api_key (str): API 密钥
            api_base_url (str): API 基础 URL
        """
        self._model_name = model_name
        self._api_key = api_key
        self._api_base_url = api_base_url
        self._embeddings = None
        self._dimension = None
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化模型"""
        try:
            from langchain_openai import OpenAIEmbeddings
            
            # 构建参数
            params = {
                'model': self._model_name
            }
            
            if self._api_key:
                params['api_key'] = self._api_key
            
            if self._api_base_url:
                params['base_url'] = self._api_base_url
            
            self._embeddings = OpenAIEmbeddings(**params)
            
            # 计算向量维度
            test_vector = self.embed_query("测试文本")
            self._dimension = len(test_vector)
        except ImportError:
            raise ValueError("未安装 langchain-openai 包")
        except Exception as e:
            raise ValueError(f"初始化 OpenAI 嵌入模型失败: {str(e)}")
    
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
