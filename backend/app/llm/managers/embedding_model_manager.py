"""嵌入模型管理器 - 工厂模式实现"""
import threading
from typing import Any
from app.core.instance_manager import InstanceManager


class EmbeddingModelManager:
    """嵌入模型管理器，使用工厂模式管理不同供应商的嵌入模型"""
    
    # 模型驱动映射表
    _model_drivers = None
    
    @classmethod
    def _get_model_drivers(cls):
        """延迟加载模型驱动映射表"""
        if cls._model_drivers is None:
            from app.llm.vendors.huggingface_embedding_model import HuggingFaceEmbeddingModel
            from app.llm.vendors.openai_embedding_model import OpenAIEmbeddingModel
            from app.llm.vendors.ollama_embedding_model import OllamaEmbeddingModel
            
            cls._model_drivers = {
                'huggingface': HuggingFaceEmbeddingModel,
                'openai': OpenAIEmbeddingModel,
                'ollama': OllamaEmbeddingModel
            }
        return cls._model_drivers
    
    @classmethod
    def get_embedding_model(cls, model_type: str, model_name: str, **kwargs) -> Any:
        """获取嵌入模型实例（使用统一实例管理器）
        
        Args:
            model_type: 模型类型 (huggingface, openai, ollama)
            model_name: 模型名称
            **kwargs: 额外参数
            
        Returns:
            Any: 嵌入模型实例
        """
        # 生成缓存键
        cache_key = f"{model_type}:{model_name}:{hash(str(kwargs))}"
        
        # 使用统一实例管理器获取实例
        def create_model():
            return cls._load_model(model_type, model_name, **kwargs)
        
        return InstanceManager.get_instance('embedding', cache_key, create_model)
    
    @classmethod
    def _load_model(cls, model_type: str, model_name: str, **kwargs) -> Any:
        """加载指定类型的嵌入模型
        
        Args:
            model_type: 模型类型
            model_name: 模型名称
            **kwargs: 额外参数
            
        Returns:
            Any: 嵌入模型实例
        """
        drivers = cls._get_model_drivers()
        if model_type not in drivers:
            raise ValueError(f'未支持的模型类型: {model_type}')
        
        try:
            # 根据模型类型创建相应的模型实例
            if model_type == 'huggingface':
                # 提取 HuggingFace 特定参数
                model_kwargs = kwargs.get('model_kwargs', {'device': 'cpu'})
                encode_kwargs = kwargs.get('encode_kwargs', {'normalize_embeddings': True})
                return drivers[model_type](model_name, model_kwargs, encode_kwargs)
            elif model_type == 'openai':
                # 提取 OpenAI 特定参数
                api_key = kwargs.get('api_key')
                api_base_url = kwargs.get('api_base_url')
                return drivers[model_type](model_name, api_key, api_base_url)
            elif model_type == 'ollama':
                # 提取 Ollama 特定参数
                base_url = kwargs.get('base_url')
                return drivers[model_type](model_name, base_url)
            else:
                # 默认使用基本初始化
                return drivers[model_type](model_name)
        except Exception as e:
            print(f"加载 {model_type} 嵌入模型失败: {str(e)}")
            return None
    
    @classmethod
    def clear_model_cache(cls) -> int:
        """清空模型缓存
        
        Returns:
            int: 清空的缓存项数量
        """
        cache_size = InstanceManager.get_cache_size('embedding').get('embedding', 0)
        InstanceManager.clear_cache('embedding')
        print(f"模型缓存已清空，共 {cache_size} 个模型")
        return cache_size
    
    @classmethod
    def get_cache_size(cls) -> int:
        """获取当前缓存大小
        
        Returns:
            int: 当前缓存大小
        """
        return InstanceManager.get_cache_size('embedding').get('embedding', 0)
