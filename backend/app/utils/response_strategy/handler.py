"""响应处理器工具类"""
import json
import asyncio
from typing import Dict, Any, Generator, Callable

from app.services.base_service import BaseService
from app.utils.response_strategy.strategy.base import ResponseStrategy


class ResponseStrategyContext:
    """响应策略上下文"""
    
    def __init__(self, strategy: ResponseStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: ResponseStrategy):
        self._strategy = strategy
    
    async def handle_response(self, chat, message_text, user_message, now, model_messages, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, use_agent=False, 
                       model=None, chat_service=None):
        # 必须 await 策略的异步方法
        return await self._strategy.handle_response(chat, message_text, user_message, now, 
                                             model_messages, parsed_model_name, 
                                             parsed_version_name, model_params, 
                                             model_display_name, use_agent, 
                                             model, chat_service)


class ResponseHandler:
    """响应处理器，处理不同类型的响应"""
    
    @staticmethod
    def _get_strategy(use_agent, is_streaming):
        """获取响应策略
        
        Args:
            use_agent: 是否使用智能体
            is_streaming: 是否为流式响应
            
        Returns:
            ResponseStrategy: 响应策略实例
        """
        if use_agent:
            from app.utils.response_strategy.strategy.agent import AgentResponseStrategy
            return AgentResponseStrategy()
        else:
            if is_streaming:
                from app.utils.response_strategy.strategy.streaming import StreamingResponseStrategy
                return StreamingResponseStrategy()
            else:
                from app.utils.response_strategy.strategy.regular import RegularResponseStrategy
                return RegularResponseStrategy()
    
    @staticmethod
    async def handle_regular_response(chat, message_text, user_message, now,
                               model_messages, parsed_model_name, parsed_version_name, 
                               model_params, model_display_name, use_agent=False,
                               model=None, chat_service=None):
        """处理普通响应（非流式）"""
        strategy = ResponseHandler._get_strategy(use_agent, False)
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      model_messages, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, use_agent, 
                                      model, chat_service)
    
    
    @staticmethod
    async def handle_streaming_response(chat, message_text, user_message, now,
                                 model_messages, parsed_model_name, parsed_version_name, 
                                 model_params, model_display_name, use_agent=False,
                                 model=None, chat_service=None):
        """处理流式响应（包括智能体的流式模式）"""
        strategy = ResponseHandler._get_strategy(use_agent, True)
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      model_messages, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, use_agent, 
                                      model, chat_service)