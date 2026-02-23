"""嵌入模型管理器 - 工厂模式实现"""
import threading
from typing import Dict, Any, Optional
from collections import OrderedDict


class EmbeddingModelManager:
    """嵌入模型管理器，使用工厂模式管理不同供应商的嵌入模型"""
    
    # 模型驱动映射表
    _model_drivers = None
    
    # 模型缓存，使用OrderedDict实现LRU缓存
    _model_cache = OrderedDict()
    _cache_size = 3  # 缓存大小限制
    _cache_lock = threading.Lock()  # 缓存操作锁
    
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
        """获取嵌入模型实例（支持缓存和即用即加载）
        
        Args:
            model_type: 模型类型 (huggingface, openai, ollama)
            model_name: 模型名称
            **kwargs: 额外参数
            
        Returns:
            Any: 嵌入模型实例
        """
        # 生成缓存键
        cache_key = f"{model_type}:{model_name}:{hash(str(kwargs))}"
        
        # 检查缓存中是否存在模型
        with cls._cache_lock:
            if cache_key in cls._model_cache:
                # 命中缓存，将模型移到缓存末尾（LRU策略）
                model = cls._model_cache.pop(cache_key)
                cls._model_cache[cache_key] = model
                print(f"从缓存加载嵌入模型: {model_name} (类型: {model_type})")
                return model
        
        # 缓存未命中，加载新模型
        print(f"加载新的嵌入模型: {model_name} (类型: {model_type})")
        
        model = cls._load_model(model_type, model_name, **kwargs)
        
        # 将模型添加到缓存
        if model:
            with cls._cache_lock:
                # 如果缓存已满，移除最旧的模型
                if len(cls._model_cache) >= cls._cache_size:
                    cls._model_cache.popitem(last=False)
                # 添加新模型到缓存末尾
                cls._model_cache[cache_key] = model
                print(f"嵌入模型已缓存: {model_name} (类型: {model_type})")
        
        return model
    
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
        with cls._cache_lock:
            cache_size = len(cls._model_cache)
            cls._model_cache.clear()
            print(f"模型缓存已清空，共 {cache_size} 个模型")
            return cache_size
    
    @classmethod
    def get_cache_size(cls) -> int:
        """获取当前缓存大小
        
        Returns:
            int: 当前缓存大小
        """
        with cls._cache_lock:
            return len(cls._model_cache)
