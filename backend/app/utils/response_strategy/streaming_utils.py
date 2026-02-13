"""流式响应处理工具类"""
from app.utils.response_strategy.stream import StreamUtils


class StreamingUtils:
    """流式响应处理工具"""
    
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
        async for chunk in chat_service.chat_with_model_stream(model_name, model_messages, version_name, model_params, use_agent, model):
            yield chunk
    
    @staticmethod
    def format_stream_chunk(chunk, agent=False, **kwargs):
        """格式化流式响应块
        
        Args:
            chunk: 响应块
            agent: 是否为智能体响应
            **kwargs: 额外参数
            
        Returns:
            格式化后的响应块
        """
        return StreamUtils.format_stream_chunk(chunk, agent=agent)
    
    @staticmethod
    def format_stream_error(error_msg, agent=False):
        """格式化错误响应
        
        Args:
            error_msg: 错误消息
            agent: 是否为智能体响应
            
        Returns:
            格式化后的错误响应
        """
        return StreamUtils.format_stream_error(error_msg, agent=agent)
    
    @staticmethod
    def format_stream_done(agent=False, **kwargs):
        """格式化完成响应
        
        Args:
            agent: 是否为智能体响应
            **kwargs: 额外参数
            
        Returns:
            格式化后的完成响应
        """
        return StreamUtils.format_stream_done(agent=agent)
    
    @staticmethod
    def create_streaming_generator(process_func):
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
                yield StreamingUtils.format_stream_error(str(e))
        return generate
