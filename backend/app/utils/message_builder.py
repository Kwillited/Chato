"""消息构建模块，负责构建完整的消息列表"""
from typing import List, Dict, Optional, Any
from app.utils.prompt_manager import prompt_manager


class MessageBuilder:
    """消息构建器，负责构建各种类型的消息列表"""
    
    @staticmethod
    def build_normal_messages(query: str, chat_history: List[Dict[str, str]] = None, prompt_template: str = None):
        """构建普通模式的消息列表
        
        Args:
            query: 用户查询
            chat_history: 聊天历史记录
            prompt_template: 自定义提示模板
            
        Returns:
            List[dict]: 消息列表
        """
        return prompt_manager.build_messages(
            query=query,
            context_docs=None,
            chat_history=chat_history,
            mode='normal',
            prompt_template=prompt_template
        )
    
    @staticmethod
    def build_rag_messages(query: str, context_docs: List[Any], chat_history: List[Dict[str, str]] = None, prompt_template: str = None):
        """构建RAG模式的消息列表
        
        Args:
            query: 用户查询
            context_docs: 检索到的上下文文档列表
            chat_history: 聊天历史记录
            prompt_template: 自定义提示模板
            
        Returns:
            List[dict]: 消息列表
        """
        return prompt_manager.build_messages(
            query=query,
            context_docs=context_docs,
            chat_history=chat_history,
            mode='rag',
            prompt_template=prompt_template
        )
    
    @staticmethod
    def build_agent_messages(query: str, chat_history: List[Dict[str, str]] = None, prompt_template: str = None):
        """构建智能体模式的消息列表
        
        Args:
            query: 用户查询
            chat_history: 聊天历史记录
            prompt_template: 自定义提示模板
            
        Returns:
            List[dict]: 消息列表
        """
        return prompt_manager.build_messages(
            query=query,
            context_docs=None,
            chat_history=chat_history,
            mode='agent',
            prompt_template=prompt_template
        )
    
    @staticmethod
    def build_messages_from_chat(chat_id: str, query: str, rag_enabled: bool = False, agent_enabled: bool = False, context_docs: List[Any] = None, selected_message_ids: List[str] = None):
        """从对话构建消息列表
        
        Args:
            chat_id: 对话ID
            query: 用户查询
            rag_enabled: 是否启用RAG模式
            agent_enabled: 是否启用智能体模式
            context_docs: RAG上下文文档列表
            selected_message_ids: 用户选择的消息ID列表
            
        Returns:
            List[dict]: 消息列表
        """
        from app.services.data_service import DataService
        
        # 获取对话上下文历史
        chat = DataService.get_chat_by_id(chat_id)
        chat_history = []
        
        if chat and 'messages' in chat:
            messages = chat['messages']
            
            # 如果提供了选中的消息ID列表，只包含这些消息
            if selected_message_ids:
                selected_messages = [msg for msg in messages if msg.get('id') in selected_message_ids]
                # 保持消息的原始顺序
                selected_messages.sort(key=lambda x: messages.index(x))
                chat_history = selected_messages
            else:
                # 只包含最近的10条消息，并且排除最后一条（如果是用户消息）
                # 因为最后一条用户消息会在build_messages中被重新添加
                if len(messages) > 0:
                    # 检查最后一条消息是否是用户消息
                    last_msg = messages[-1]
                    if last_msg.get('role') == 'user':
                        # 排除最后一条用户消息
                        if len(messages) > 1:
                            if len(messages) > 10:
                                chat_history = messages[-11:-1]  # 取倒数第11到倒数第2条
                            else:
                                chat_history = messages[:-1]  # 取除了最后一条以外的所有消息
                    else:
                        # 最后一条不是用户消息，正常取最近10条
                        if len(messages) > 10:
                            chat_history = messages[-10:]
                        else:
                            chat_history = messages
        
        # 根据模式构建消息列表
        if rag_enabled:
            return MessageBuilder.build_rag_messages(
                query=query,
                context_docs=context_docs,
                chat_history=chat_history
            )
        elif agent_enabled:
            return MessageBuilder.build_agent_messages(
                query=query,
                chat_history=chat_history
            )
        else:
            return MessageBuilder.build_normal_messages(
                query=query,
                chat_history=chat_history
            )
