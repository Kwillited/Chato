# app/llm/vendors/github_model.py
from app.llm.base.base_model import BaseModel


class GitHubModel(BaseModel):
    """GitHub模型驱动 (使用langchain)"""
    
    def _initialize_llm(self) -> None:
        """初始化langchain的OpenAI兼容LLM实例"""
        from langchain_openai import ChatOpenAI
        
        selected_version = self._get_selected_version('openai/gpt-4.1')
        api_key = self.version_config.get('api_key')
        base_url = self.version_config.get('base_url', 'https://models.github.ai/inference/chat/completions')
        
        if not api_key:
            raise Exception('GitHub模型API密钥未配置')
        
        self.llm = ChatOpenAI(
            model=selected_version,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,  # 默认温度，会在调用时被覆盖
            timeout=180  # 超时设置
        )
