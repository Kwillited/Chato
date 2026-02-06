# app/llm/vendors/google_ai_model.py
from app.llm.base.base_model import BaseModel

class GoogleAIModel(BaseModel):
    """Google AI模型驱动 (使用langchain)"""
    
    def _initialize_llm(self) -> None:
        """初始化langchain的Google AI LLM实例"""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        selected_version = self._get_selected_version('gemini-pro')
        api_key = self.version_config.get('api_key')
        
        if not api_key:
            raise Exception('Google AI API密钥未配置')
        
        self.llm = ChatGoogleGenerativeAI(
            model=selected_version,
            api_key=api_key,
            temperature=0.7,
            timeout=180
        )
