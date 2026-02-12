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
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       selected_message_ids=None, chat_service=None):
        # 必须 await 策略的异步方法
        return await self._strategy.handle_response(chat, message_text, user_message, now, 
                                             enhanced_question, parsed_model_name, 
                                             parsed_version_name, model_params, 
                                             model_display_name, deep_thinking, 
                                             use_agent, selected_message_ids, chat_service)


class ResponseHandler:
    """响应处理器，处理不同类型的响应"""
    
    @staticmethod
    async def handle_regular_response(chat, message_text, user_message, now,
                               enhanced_question, parsed_model_name, parsed_version_name, 
                               model_params, model_display_name, deep_thinking=False, use_agent=False,
                               selected_message_ids=None, chat_service=None):
        """处理普通响应（非流式）"""
        if use_agent:
            from app.utils.response_strategy.strategy.agent import AgentResponseStrategy
            strategy = AgentResponseStrategy()
        else:
            from app.utils.response_strategy.strategy.regular import RegularResponseStrategy
            strategy = RegularResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      selected_message_ids, chat_service)
    
    @staticmethod
    async def handle_streaming_response(chat, message_text, user_message, now,
                                 enhanced_question, parsed_model_name, parsed_version_name, 
                                 model_params, model_display_name, deep_thinking=False, use_agent=False,
                                 selected_message_ids=None, chat_service=None):
        """处理流式响应（包括智能体的流式模式）"""
        if use_agent:
            from app.utils.response_strategy.strategy.agent import AgentResponseStrategy
            strategy = AgentResponseStrategy()
        else:
            from app.utils.response_strategy.strategy.streaming import StreamingResponseStrategy
            strategy = StreamingResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      selected_message_ids, chat_service)