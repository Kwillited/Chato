# app/llm/vendors/github_model.py
from typing import Dict, Any
from app.llm.base.base_model import BaseModel


class GitHubModel(BaseModel):
    """GitHub模型驱动 (使用langchain)"""
    
    def _initialize_llm(self) -> None:
        """初始化langchain的OpenAI兼容LLM实例"""
        from langchain_openai import ChatOpenAI
        
        selected_version = self._get_selected_version('openai/gpt-4.1')
        # 处理模型名称转换
        if '/' in selected_version:
            # 模型名称包含前缀，例如 openai/o4-mini
            prefix, model_name = selected_version.split('/', 1)
            # 转换 o4-mini 为 gpt-4o-mini
            if model_name == 'o4-mini':
                model_name = 'gpt-4o-mini'
            selected_version = f'{prefix}/{model_name}'
        else:
            # 模型名称不包含前缀，例如 o4-mini
            model_name = selected_version
            # 转换 o4-mini 为 gpt-4o-mini
            if model_name == 'o4-mini':
                model_name = 'gpt-4o-mini'
            selected_version = f'openai/{model_name}'
        api_key = self.version_config.get('api_key')
        base_url = self.version_config.get('base_url', 'https://models.github.ai/inference')
        
        if not api_key:
            raise Exception('GitHub模型API密钥未配置')
        
        self.llm = ChatOpenAI(
            model=selected_version,
            api_key=api_key,
            base_url=base_url,
            timeout=180  # 超时设置
        )
    
    def _prepare_call_kwargs(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理调用参数，移除GitHub模型API不支持的参数
        """
        # GitHub模型API不支持top_k参数
        filtered_params = {}
        for key, value in model_params.items():
            if key != 'top_k':
                filtered_params[key] = value
        return filtered_params
