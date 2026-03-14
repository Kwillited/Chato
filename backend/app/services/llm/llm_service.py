"""统一的LLM调用服务"""
from typing import List, Dict, Any
from app.services.base_service import BaseService


class LLMService(BaseService):
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
        # 记录调用LLM时传入的消息
        LLMService.log_info(f"\n=== 调用LLM传入的消息 ===")
        LLMService.log_info(f"模型名称: {model_name}")
        LLMService.log_info(f"使用智能体: {use_agent}")
        LLMService.log_info("消息内容:")
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            LLMService.log_info(f"[{i}] {role}: {content[:200]}{'...' if len(content) > 200 else ''}")
        LLMService.log_info("====================\n")
        
        from app.llm.managers.model_manager import ModelManager
        
        if use_agent:
            # 智能体模式
            from app.llm.agent_manager import AgentManager
            
            base_driver = ModelManager.get_model_driver(model_name, model_config, version_config)
            agent_wrapper = AgentManager(base_driver)
            await agent_wrapper.initialize()
            
            if model_params.get('stream', False):
                return agent_wrapper.chat_stream(messages, model_params)
            else:
                return await agent_wrapper.chat(messages, model_params)
        else:
            # 普通模式（包括RAG）
            return ModelManager.chat(model_name, model_config, version_config, messages, model_params)
    

