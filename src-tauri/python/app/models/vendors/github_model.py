# app/models/vendors/github_model.py
from app.models.base_model import BaseModel
import json
from typing import Dict, Any, Generator, List


class GitHubModel(BaseModel):
    """GitHub模型驱动 (使用langchain)"""
    
    def _initialize_llm(self) -> None:
        """初始化langchain的OpenAI兼容LLM实例"""
        from langchain_openai import ChatOpenAI
        
        # 检查多个可能的版本名称字段，确保兼容性
        selected_version = self.version_config.get('name') or \
                          self.version_config.get('version_name') or \
                          self.version_config.get('custom_name') or \
                          'openai/gpt-4.1'  # 默认值
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
    
    def chat(self, messages: List[Dict[str, str]], temperature: float, stream: bool = False) -> Dict[str, Any]:
        """非流式调用GitHub模型API"""
        langchain_messages = self._convert_to_langchain_messages(messages)
        self.llm.temperature = temperature
        
        response = self.llm.invoke(langchain_messages)
        return self._format_response(response.content)
    
    def chat_stream(self, messages: List[Dict[str, str]], temperature: float) -> Generator[str, None, None]:
        """流式调用GitHub模型API"""
        langchain_messages = self._convert_to_langchain_messages(messages)
        self.llm.temperature = temperature
        
        for chunk in self.llm.stream(langchain_messages):
            if hasattr(chunk, 'content') and chunk.content:
                response_data = {
                    'chunk': chunk.content,
                    'content_struct': None
                }
                yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
        
        response_data = {'done': True}
        yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'