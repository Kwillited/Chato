# app/llm/vendors/openai_model.py
from app.llm.base.base_model import BaseModel

class OpenAIModel(BaseModel):
    """OpenAI模型驱动 (使用langchain)"""
    
    def _initialize_llm(self) -> None:
        """初始化langchain的OpenAI LLM实例"""
        from langchain_openai import ChatOpenAI
        
        selected_version = self._get_selected_version('gpt-3.5-turbo')
        api_key = self.version_config.get('api_key')
        base_url = self.version_config.get('base_url', None)
        
        if not api_key:
            raise Exception('OpenAI API密钥未配置')
        
        self.llm = ChatOpenAI(
            model=selected_version,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            timeout=180
        )
