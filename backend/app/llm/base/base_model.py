# llm/base/base_model.py
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseLanguageModel
from typing import List, Dict, Any, Optional, Generator,  AsyncIterator 
from app.utils.message_utils import MessageUtils
from app.utils.stream_utils import StreamUtils


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

    def chat(self, messages: List[Dict[str, str]], model_params: Dict[str, Any], stream: bool = False) -> Dict[str, Any]:
        """非流式对话 - 返回统一的回复格式
        
        Args:
            messages: 消息列表
            model_params: 模型参数字典
            stream: 是否流式返回
            
        Returns:
            Dict: 统一格式的回复
        """
        from app.utils.logging_utils import LoggingUtils
        LoggingUtils.log_info(f"🔧 LLM参数传递: Received model params: {model_params}")
        
        langchain_messages = MessageUtils.convert_to_langchain_messages(messages)
        
        # 设置模型参数
        if hasattr(self.llm, 'temperature'):
            self.llm.temperature = model_params.get('temperature', 0.7)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set temperature to: {self.llm.temperature}")
        if hasattr(self.llm, 'max_tokens'):
            self.llm.max_tokens = model_params.get('max_tokens', 2000)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set max_tokens to: {self.llm.max_tokens}")
        if hasattr(self.llm, 'top_p'):
            self.llm.top_p = model_params.get('top_p', 1.0)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set top_p to: {self.llm.top_p}")
        if hasattr(self.llm, 'top_k'):
            self.llm.top_k = model_params.get('top_k', 50)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set top_k to: {self.llm.top_k}")
        if hasattr(self.llm, 'frequency_penalty'):
            self.llm.frequency_penalty = model_params.get('frequency_penalty', 0.0)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set frequency_penalty to: {self.llm.frequency_penalty}")
        
        # 调用模型
        response = self.llm.invoke(langchain_messages)
        LoggingUtils.log_info("🔧 LLM调用: Model invoked successfully")
        return self._format_response(response.content)

    async def chat_stream(self, messages: List[Dict[str, str]], model_params: Dict[str, Any]) -> AsyncIterator[str]:
        from app.utils.logging_utils import LoggingUtils
        LoggingUtils.log_info(f"🔧 LLM参数传递: Received stream model params: {model_params}")
        
        langchain_messages = MessageUtils.convert_to_langchain_messages(messages)
        
        # 设置模型参数
        if hasattr(self.llm, 'temperature'):
            self.llm.temperature = model_params.get('temperature', 0.7)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set stream temperature to: {self.llm.temperature}")
        if hasattr(self.llm, 'max_tokens'):
            self.llm.max_tokens = model_params.get('max_tokens', 2000)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set stream max_tokens to: {self.llm.max_tokens}")
        if hasattr(self.llm, 'top_p'):
            self.llm.top_p = model_params.get('top_p', 1.0)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set stream top_p to: {self.llm.top_p}")
        if hasattr(self.llm, 'top_k'):
            self.llm.top_k = model_params.get('top_k', 50)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set stream top_k to: {self.llm.top_k}")
        if hasattr(self.llm, 'frequency_penalty'):
            self.llm.frequency_penalty = model_params.get('frequency_penalty', 0.0)
            LoggingUtils.log_info(f"🔧 LLM参数设置: Set stream frequency_penalty to: {self.llm.frequency_penalty}")
        
        LoggingUtils.log_info("🔧 LLM调用: Starting stream invocation")
        
        try:
            # 使用 astream 处理异步流
            async for chunk in self.llm.astream(langchain_messages):
                content = None
                if hasattr(chunk, 'content'):
                    content = chunk.content
                elif isinstance(chunk, dict):
                    content = chunk.get('content')
                elif isinstance(chunk, str):
                    content = chunk
                
                if content:
                    yield StreamUtils.format_stream_chunk(content)
        except Exception as e:
            LoggingUtils.log_error(f"🔧 LLM错误: Streaming error: {e}")
            yield StreamUtils.format_stream_error(str(e))
        
        LoggingUtils.log_info("🔧 LLM调用: Stream invocation completed")
        yield StreamUtils.format_stream_done()

    def _format_response(self, content: str, content_struct: Optional[Any] = None) -> Dict[str, Any]:
        """统一响应格式"""
        return {
            'content': content,
            'content_struct': content_struct
        }
