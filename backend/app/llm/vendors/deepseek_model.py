# app/llm/vendors/deepseek_model.py
from typing import Dict, Any
from app.llm.base.base_model import BaseModel

class DeepSeekModel(BaseModel):
    """DeepSeek模型驱动 (使用langchain-deepseek)"""
    
    def _initialize_llm(self) -> None:
        """初始化langchain的DeepSeek LLM实例"""
        from langchain_deepseek import ChatDeepSeek
        
        selected_version = self._get_selected_version('deepseek-chat')
        api_key = self.version_config.get('api_key')
        base_url = self.version_config.get('base_url', 'https://api.deepseek.com/v1')
        
        if not api_key:
            raise Exception('DeepSeek API密钥未配置')
        
        self.llm = ChatDeepSeek(
            model=selected_version,
            api_key=api_key,
            base_url=base_url,
            timeout=180
        )
    
    def _prepare_call_kwargs(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理调用参数，移除DeepSeek API不支持的参数
        """
        # DeepSeek API不支持top_k参数
        filtered_params = {}
        for key, value in model_params.items():
            if key != 'top_k':
                filtered_params[key] = value
        return filtered_params
