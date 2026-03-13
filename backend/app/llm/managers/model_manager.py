# app/llm/managers/model_manager.py
from app.llm.base.base_model import BaseModel
from typing import Dict, Any, List
import json
from app.core.instance_manager import InstanceManager

class ModelManager:
    _model_drivers = None
    
    @classmethod
    def _get_model_drivers(cls):
        """延迟加载模型驱动映射表"""
        if cls._model_drivers is None:
            from app.llm.vendors import OllamaModel, OpenAIModel, AnthropicModel, GoogleAIModel, GitHubModel, DeepSeekModel
            cls._model_drivers = {
                'Ollama': OllamaModel,
                'GitHubModel': GitHubModel,
                'OpenAI': OpenAIModel,        
                'Anthropic': AnthropicModel,   
                'GoogleAI': GoogleAIModel,     
                'DeepSeek': DeepSeekModel      
            }
        return cls._model_drivers
    
    @classmethod
    def _generate_cache_key(cls, model_name: str, model_config: Dict[str, Any], version_config: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 提取关键配置参数用于生成缓存键
        key_data = {
            'model_name': model_name,
            'model_config': {
                'name': model_config.get('name'),
                'configured': model_config.get('configured'),
                'enabled': model_config.get('enabled')
            },
            'version_config': {
                'version_name': version_config.get('version_name'),
                'custom_name': version_config.get('custom_name'),
                'api_key': version_config.get('api_key'),
                'api_base_url': version_config.get('api_base_url'),
                'streaming_config': version_config.get('streaming_config')
            }
        }
        return json.dumps(key_data, sort_keys=True)
    
    @classmethod
    def get_model_driver(cls, model_name: str, model_config: Dict[str, Any], version_config: Dict[str, Any]) -> BaseModel:
        """获取模型驱动实例（使用统一实例管理器）"""
        drivers = cls._get_model_drivers()
        if model_name not in drivers:
            raise ValueError(f'未实现注册的模型类型: {model_name}')
        
        # 生成缓存键
        cache_key = cls._generate_cache_key(model_name, model_config, version_config)
        
        # 使用统一实例管理器获取实例
        def create_model():
            return drivers[model_name](model_config, version_config)
        
        return InstanceManager.get_instance('llm', cache_key, create_model)
    
    @classmethod
    def chat(cls, model_name: str, model_config: Dict[str, Any], version_config: Dict[str, Any], 
             messages: List[Dict[str, str]], model_params: Dict[str, Any]) -> Any:
        """统一的聊天接口"""
        # 从 model_params 中获取 stream 参数
        stream = model_params.get('stream', False)
        
        driver = cls.get_model_driver(model_name, model_config, version_config)
        
        if stream:
            return driver.chat_stream(messages, model_params)
        else:
            return driver.chat(messages, model_params)
    
    @classmethod
    def clear_cache(cls):
        """清空模型实例缓存"""
        InstanceManager.clear_cache('llm')
    
    @classmethod
    def get_cache_size(cls) -> int:
        """获取缓存大小"""
        return InstanceManager.get_cache_size('llm').get('llm', 0)
