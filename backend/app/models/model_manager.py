# app/models/model_manager.py
from app.models.base_model import BaseModel
from typing import Dict, Any, Generator, List, Optional

class ModelManager:
    _model_drivers = None
    
    @classmethod
    def _get_model_drivers(cls):
        """延迟加载模型驱动映射表"""
        if cls._model_drivers is None:
            from app.models.vendors import OllamaModel, OpenAIModel, AnthropicModel, GoogleAIModel, GitHubModel
            cls._model_drivers = {
                'Ollama': OllamaModel,
                'GitHubModel': GitHubModel,
                'OpenAI': OpenAIModel,        
                'Anthropic': AnthropicModel,   
                'GoogleAI': GoogleAIModel      
            }
        return cls._model_drivers
    
    @classmethod
    def get_model_driver(cls, model_name: str, model_config: Dict[str, Any], version_config: Dict[str, Any]) -> BaseModel:
        """获取模型驱动实例"""
        drivers = cls._get_model_drivers()
        if model_name not in drivers:
            raise ValueError(f'未实现注册的模型类型: {model_name}')
        
        return drivers[model_name](model_config, version_config)
    
    @classmethod
    def chat(cls, model_name: str, model_config: Dict[str, Any], version_config: Dict[str, Any], 
             messages: List[Dict[str, str]], temperature: float, stream: bool = False) -> Any:
        """统一的聊天接口"""
        driver = cls.get_model_driver(model_name, model_config, version_config)
        
        if stream:
            return driver.chat_stream(messages, temperature)
        else:
            return driver.chat(messages, temperature, stream)