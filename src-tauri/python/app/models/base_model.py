# models/base_model.py
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import BaseMessage
from typing import List, Dict, Any, Optional, Generator
import json


class BaseModel(ABC):
    def __init__(self, model_config: Dict[str, Any], version_config: Dict[str, Any]):
        self.model_config = model_config
        self.version_config = version_config
        self.llm: Optional[BaseLanguageModel] = None
        self._initialize_llm()

    def _get_selected_version(self, default_version: str) -> str:
        """获取选中的模型版本，支持多种配置字段
        
        Args:
            default_version: 默认版本名称
            
        Returns:
            str: 选中的版本名称
        """
        return self.version_config.get('name') or \
               self.version_config.get('version_name') or \
               self.version_config.get('custom_name') or \
               default_version

    @abstractmethod
    def _initialize_llm(self) -> None:
        """初始化langchain的LLM实例"""
        pass

    def chat(self, messages: List[Dict[str, str]], temperature: float, stream: bool = False) -> Dict[str, Any]:
        """非流式对话 - 返回统一的回复格式
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            stream: 是否流式返回
            
        Returns:
            Dict: 统一格式的回复
        """
        langchain_messages = self._convert_to_langchain_messages(messages)
        self.llm.temperature = temperature
        
        response = self.llm.invoke(langchain_messages)
        return self._format_response(response.content)

    def chat_stream(self, messages: List[Dict[str, str]], temperature: float) -> Generator[str, None, None]:
        """流式对话 - 返回统一的生成器
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            
        Yields:
            str: 流式响应数据
        """
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

    def _format_response(self, content: str, content_struct: Optional[Any] = None) -> Dict[str, Any]:
        """统一响应格式"""
        return {
            'content': content,
            'content_struct': content_struct
        }

    def _convert_to_langchain_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """将内部消息格式转换为langchain消息格式"""
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        
        langchain_messages = []
        for msg in messages:
            role = msg['role'].lower()
            content = msg['content']
            
            if role == 'system':
                langchain_messages.append(SystemMessage(content=content))
            elif role == 'user':
                langchain_messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                langchain_messages.append(AIMessage(content=content))
            # 其他角色暂时保留为HumanMessage
            else:
                langchain_messages.append(HumanMessage(content=content))
        
        return langchain_messages