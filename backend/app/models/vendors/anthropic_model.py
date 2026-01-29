# app/models/anthropic_model.py
from app.models.base_model import BaseModel

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
            temperature=0.7,
            timeout=180
        )