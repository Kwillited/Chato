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
        # 参数映射：将通用参数名映射为 Ollama 特定的参数名
        mapping = {
            'temperature': 'temperature',
            'max_tokens': 'num_predict',
            'top_p': 'top_p',
            'top_k': 'top_k',
            'frequency_penalty': 'repeat_penalty',  # 频率惩罚映射为 Ollama 的重复惩罚
            # 注意：frequency_penalty 的默认值在 chat_service.py 中被固定为 1
            # 这样可以有效减少模型生成重复内容的可能性
            # 重要：当设置为 0 时，会导致 Ollama 的 qwen2.5 模型出现断言错误
            # 但 qwen3 模型不受此影响
        }
        
        ollama_options = {}
        reasoning = None
        
        for key, value in model_params.items():
            if key == 'deepThinking':
                reasoning = value
            elif key in mapping:
                ollama_options[mapping[key]] = value
            else:
                ollama_options[key] = value
        
        # 构建返回字典
        result = {"options": ollama_options}
        if reasoning is not None:
            result["reasoning"] = reasoning
        
        # 返回一个符合 Ollama astream/invoke 要求的字典
        # 这样在基类中 **{"options": ..., "reasoning": ...} 就会变成 options=... reasoning=...
        return result