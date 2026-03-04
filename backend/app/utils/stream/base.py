"""流式处理模块"""
import json


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
    

