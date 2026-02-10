# llm/base/base_model.py
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseLanguageModel
from typing import List, Dict, Any, Optional, AsyncIterator 
from app.utils.message_utils import MessageUtils
from app.utils.response_strategy.stream import StreamUtils

class BaseModel(ABC):
    def __init__(self, model_config: Dict[str, Any], version_config: Dict[str, Any]):
        self.model_config = model_config
        self.version_config = version_config
        self.llm: Optional[BaseLanguageModel] = None
        self._initialize_llm()

    def _get_selected_version(self, default_version: str) -> str:
        """获取选中的模型版本，支持多种配置字段"""
        return self.version_config.get('name') or \
               self.version_config.get('version_name') or \
               self.version_config.get('custom_name') or \
               default_version

    @abstractmethod
    def _initialize_llm(self) -> None:
        """初始化 LangChain 的 LLM 实例（由子类实现）"""
        pass

    def _prepare_call_kwargs(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理调用参数的钩子函数。
        默认直接返回原始参数。子类（如 Ollama）可以重写此方法以符合其 API 要求。
        
        例如在 Ollama 中重写为：return {"options": {...}}
        """
        return model_params

    def chat(self, messages: List[Dict[str, str]], model_params: Dict[str, Any]) -> Dict[str, Any]:
        """非流式对话 - 返回统一的回复格式"""
        from app.utils.logging_utils import LoggingUtils
        LoggingUtils.log_info(f"🔧 LLM参数传递: Original params: {model_params}")
        
        try:
            # 1. 消息格式转换
            langchain_messages = MessageUtils.convert_to_langchain_messages(messages)
            
            # 2. 调用钩子处理参数（如适配 Ollama 的 options）
            call_kwargs = self._prepare_call_kwargs(model_params)
            LoggingUtils.log_info(f"🔧 LLM调用: Invoking with processed kwargs: {list(call_kwargs.keys())}")
            
            # 3. 调用模型
            if not self.llm:
                raise RuntimeError("LLM instance is not initialized")
                
            response = self.llm.invoke(langchain_messages, **call_kwargs)
            
            # 打印模型原始响应
            print(f"[BaseModel.chat] 原始响应: type={type(response).__name__}, content={str(response)[:200]}...")
            
            # 提取reasoning_content
            reasoning_content = None
            if hasattr(response, 'additional_kwargs') and isinstance(response.additional_kwargs, dict):
                reasoning_content = response.additional_kwargs.get('reasoning_content')
            
            LoggingUtils.log_info("🔧 LLM调用: Model invoked successfully")
            return self._format_response(response.content, reasoning_content=reasoning_content)
            
        except Exception as e:
            LoggingUtils.log_error(f"🔧 LLM错误: Chat error: {e}")
            return self._format_response(f"Error: {str(e)}")

    async def chat_stream(self, messages: List[Dict[str, str]], model_params: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """流式对话"""
        from app.utils.logging_utils import LoggingUtils
        LoggingUtils.log_info(f"🔧 LLM参数传递: Original stream params: {model_params}")
        
        try:
            # 1. 消息格式转换
            langchain_messages = MessageUtils.convert_to_langchain_messages(messages)
            
            # 2. 调用钩子处理参数
            call_kwargs = self._prepare_call_kwargs(model_params)
            LoggingUtils.log_info(f"🔧 LLM调用: Starting stream with processed kwargs: {list(call_kwargs.keys())}")
            
            if not self.llm:
                raise RuntimeError("LLM instance is not initialized")

            # 3. 异步流式调用
            async for chunk in self.llm.astream(langchain_messages, **call_kwargs):
                # 打印原始数据块
                print(f"[BaseModel.chat_stream] 原始数据块: type={type(chunk).__name__}, content={str(chunk)[:200]}...")
                
                content = None
                # 兼容不同厂商返回的 chunk 格式
                if hasattr(chunk, 'content'):
                    content = chunk.content
                elif isinstance(chunk, dict):
                    content = chunk.get('content')
                elif isinstance(chunk, str):
                    content = chunk
                
                if content:
                    yield {'chunk': content}
                    
        except Exception as e:
            LoggingUtils.log_error(f"🔧 LLM错误: Streaming error: {e}")
            yield {'error': str(e)}
        
        LoggingUtils.log_info("🔧 LLM调用: Stream invocation completed")
        yield {'done': True}

    def _format_response(self, content: str, reasoning_content: Optional[str] = None) -> Dict[str, Any]:
        """统一响应格式"""
        response = {
            'content': content,
            'reasoning_content': reasoning_content
        }
        return response