"""统一的LLM调用服务"""
from typing import List, Dict, Any, AsyncIterator, Optional


class LLMService:
    """统一的LLM调用服务，封装所有LLM调用逻辑"""
    
    @staticmethod
    async def generate_response(messages: List[Dict[str, str]], model_name: str, 
                              model_config: Dict[str, Any], version_config: Dict[str, Any], 
                              model_params: Dict[str, Any], use_agent: bool = False):
        """统一生成响应
        
        Args:
            messages: 消息列表
            model_name: 模型名称
            model_config: 模型配置
            version_config: 版本配置
            model_params: 模型参数
            use_agent: 是否使用智能体模式
            
        Returns:
            生成的响应，流式返回AsyncIterator，非流式返回dict
        """
        if use_agent:
            # 智能体模式
            from app.llm.managers.model_manager import ModelManager
            from app.llm.agent_wrapper import AgentWrapper
            
            base_driver = ModelManager.get_model_driver(model_name, model_config, version_config)
            agent_wrapper = AgentWrapper(base_driver)
            await agent_wrapper.initialize()
            
            if model_params.get('stream', False):
                return agent_wrapper.chat_stream(messages, model_params)
            else:
                return await agent_wrapper.chat(messages, model_params)
        else:
            # 普通模式（包括RAG）
            from app.llm.managers.model_manager import ModelManager
            return ModelManager.chat(model_name, model_config, version_config, messages, model_params)
    

