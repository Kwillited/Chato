# stream.py
from typing import Generator, Dict, Any, AsyncGenerator  # 确保导入 AsyncGenerator
import json
import asyncio


class StreamUtils:
    """流式输出工具类"""
    
    @staticmethod
    def format_stream_chunk(chunk: str, agent: bool = False) -> str:
        """格式化流式输出的单个块"""
        response_data = {
            'chunk': chunk
        }
        # 添加agent标记
        if agent:
            response_data['agent'] = True
        return f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
    
    @staticmethod
    def format_stream_done(agent: bool = False) -> str:
        """格式化流式输出的结束标志"""
        response_data = {'done': True}
        # 添加agent标记
        if agent:
            response_data['agent'] = True
        return f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
    
    @staticmethod
    def format_stream_error(error_msg: str, agent: bool = False) -> str:
        """格式化错误信息"""
        response_data = {'error': error_msg}
        # 添加agent标记
        if agent:
            response_data['agent'] = True
        return f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
    
    @staticmethod
    async def simulate_stream(content: str, chunk_size: int = 5, delay: float = 0.05, agent: bool = False) -> AsyncGenerator[str, None]:
        """模拟流式输出 - 分块返回"""
        # 将内容分成多个小块
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if chunk:  # 确保不是空字符串
                yield StreamUtils.format_stream_chunk(chunk, agent=agent)
                await asyncio.sleep(delay)  # 添加延迟，模拟真实流式
        
        # 发送完成信号
        yield StreamUtils.format_stream_done(agent=agent)