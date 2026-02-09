# app/llm/vendors/ollama_model.py
from typing import Dict, Any
from app.llm.base.base_model import BaseModel

class OllamaModel(BaseModel):
    def _initialize_llm(self) -> None:
        """初始化 langchain 的 Ollama LLM 实例"""
        from langchain_ollama import ChatOllama
        
        selected_version = self._get_selected_version('llama3')
        base_url = self.version_config.get('api_base_url', self.version_config.get('base_url', 'http://localhost:11434'))
        
        self.llm = ChatOllama(
            model=selected_version,
            base_url=base_url,
            timeout=180
        )

    def _prepare_call_kwargs(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        重写：专门为 Ollama 封装 options 字典
        """
        mapping = {
            'temperature': 'temperature',
            'max_tokens': 'num_predict',
            'top_p': 'top_p',
            'top_k': 'top_k',
            'frequency_penalty': 'repeat_penalty',
            'deepThinking': 'reasoning',
        }
        
        ollama_options = {}
        for key, value in model_params.items():
            if key in mapping:
                ollama_options[mapping[key]] = value
            else:
                ollama_options[key] = value
        
        # 返回一个符合 Ollama astream/invoke 要求的字典
        # 这样在基类中 **{"options": ...} 就会变成 options=...
        return {"options": ollama_options}