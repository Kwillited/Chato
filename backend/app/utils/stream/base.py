"""流式处理模块"""
from typing import Generator, Dict, Any, AsyncGenerator, Callable
import json
import asyncio


class StreamSystem:
    """流式处理系统，包含流式输出和响应处理功能"""
    
    # 流式输出格式化相关方法
    @staticmethod
    def format_stream_chunk(chunk: str, agent: bool = False) -> str:
        """格式化流式输出的单个块
        
        Args:
            chunk: 响应块
            agent: 是否为智能体响应
            
        Returns:
            格式化后的响应块
        """
        response_data = {
            'chunk': chunk
        }
        # 添加agent标记
        if agent:
            response_data['agent'] = True
        return f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
    
    @staticmethod
    def format_stream_done(agent: bool = False) -> str:
        """格式化流式输出的结束标志
        
        Args:
            agent: 是否为智能体响应
            
        Returns:
            格式化后的完成响应
        """
        response_data = {'done': True}
        # 添加agent标记
        if agent:
            response_data['agent'] = True
        return f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
    
    @staticmethod
    def format_stream_error(error_msg: str, agent: bool = False) -> str:
        """格式化错误信息
        
        Args:
            error_msg: 错误消息
            agent: 是否为智能体响应
            
        Returns:
            格式化后的错误响应
        """
        response_data = {'error': error_msg}
        # 添加agent标记
        if agent:
            response_data['agent'] = True
        return f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
    
    @staticmethod
    async def simulate_stream(content: str, chunk_size: int = 5, delay: float = 0.05, agent: bool = False) -> AsyncGenerator[str, None]:
        """模拟流式输出 - 分块返回
        
        Args:
            content: 要模拟流式输出的内容
            chunk_size: 每块的大小
            delay: 每块之间的延迟
            agent: 是否为智能体响应
            
        Yields:
            流式响应块
        """
        # 将内容分成多个小块
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if chunk:  # 确保不是空字符串
                yield StreamSystem.format_stream_chunk(chunk, agent=agent)
                await asyncio.sleep(delay)  # 添加延迟，模拟真实流式
        
        # 发送完成信号
        yield StreamSystem.format_stream_done(agent=agent)
    
    # 流式响应处理相关方法
    @staticmethod
    async def handle_streaming_response(chat_service, model_name, model_messages, version_name, model_params, use_agent, model):
        """处理流式响应的通用逻辑
        
        Args:
            chat_service: 聊天服务实例
            model_name: 模型名称
            model_messages: 模型消息
            version_name: 版本名称
            model_params: 模型参数
            use_agent: 是否使用智能体
            model: 模型实例
            
        Yields:
            流式响应块
        """
        from app.services.llm.llm_service import LLMService
        version_config = chat_service.get_version_config(model, version_name)
        async for chunk in await LLMService.generate_response(
            messages=model_messages,
            model_name=model_name,
            model_config=model,
            version_config=version_config,
            model_params=model_params,
            use_agent=use_agent
        ):
            yield chunk
    
    @staticmethod
    def create_streaming_generator(process_func: Callable) -> Callable:
        """创建流式响应生成器
        
        Args:
            process_func: 处理函数，接收流式响应块并返回格式化后的响应
            
        Returns:
            流式响应生成器函数
        """
        async def generate():
            try:
                async for chunk in process_func():
                    yield chunk
            except Exception as e:
                yield StreamSystem.format_stream_error(str(e))
        return generate
