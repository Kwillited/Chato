"""响应消息处理模块"""
from app.utils.message.base import MessageSystem
from app.utils.message.agent import AgentSystem


class ResponseMessageSystem:
    """响应消息处理系统，包含消息创建和格式化功能"""
    
    @staticmethod
    def create_ai_message(content, now, model_display_name, reasoning_content=None, **kwargs):
        """创建AI消息
        
        Args:
            content: 消息内容
            now: 当前时间戳
            model_display_name: 模型显示名称
            reasoning_content: 推理内容
            **kwargs: 额外参数
            
        Returns:
            格式化后的AI消息
        """
        ai_message = MessageSystem.process_full_reply(content, now, model_display_name, reasoning_content)
        # 添加额外参数
        for key, value in kwargs.items():
            ai_message[key] = value
        return ai_message
    
    @staticmethod
    def create_agent_message(content, now, model_display_name, session_id=None, node=None, step=None, reasoning_content=None):
        """创建智能体消息
        
        Args:
            content: 消息内容
            now: 当前时间戳
            model_display_name: 模型显示名称
            session_id: 智能体会话ID
            node: 智能体节点名称
            step: 智能体步骤
            reasoning_content: 推理内容
            
        Returns:
            格式化后的智能体消息
        """
        return AgentSystem.format_agent_message(content, now, model_display_name, 
                                             session_id=session_id, 
                                             node=node, 
                                             step=step,
                                             full_reasoning=reasoning_content)
