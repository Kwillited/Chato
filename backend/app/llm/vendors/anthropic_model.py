# app/llm/vendors/anthropic_model.py
from typing import Dict, Any
from app.llm.base.base_model import BaseModel

class AnthropicModel(BaseModel):
    """Anthropic模型驱动 (使用langchain)"""
    
    def _initialize_llm(self) -> None:
        """初始化langchain的Anthropic LLM实例"""
        from langchain_anthropic import ChatAnthropic
        
        selected_version = self._get_selected_version('claude-3-opus-20240229')
        api_key = self.version_config.get('api_key')
        
        if not api_key:
            raise Exception('Anthropic API密钥未配置')
        
        self.llm = ChatAnthropic(
            model=selected_version,
            api_key=api_key,
            timeout=180
        )
    
    def _prepare_call_kwargs(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理调用参数，移除Anthropic API不支持的参数
        """
        # Anthropic API不支持top_k参数
        filtered_params = {}
        for key, value in model_params.items():
            if key != 'top_k':
                filtered_params[key] = value
        return filtered_params
