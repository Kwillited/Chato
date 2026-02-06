# app/llm/vendors/ollama_model.py
from app.llm.base.base_model import BaseModel


class OllamaModel(BaseModel):
    def _initialize_llm(self) -> None:
        """初始化langchain的Ollama LLM实例"""
        from langchain_ollama import ChatOllama
        
        # 获取选中的版本，支持多种配置字段
        selected_version = self._get_selected_version('llama3')
        base_url = self.version_config.get('api_base_url', self.version_config.get('base_url', 'http://localhost:11434'))
        
        # 创建ChatOllama实例，只保留必要的固定参数
        self.llm = ChatOllama(
            model=selected_version,
            base_url=base_url,
            timeout=180,  # 超时设置
            think_thought=True
        )
