from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage


class MessageUtils:
    """消息处理工具类"""
    
    @staticmethod
    def convert_to_langchain_messages(messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """将内部消息格式转换为langchain消息格式
        
        Args:
            messages: 内部消息格式列表
            
        Returns:
            List[BaseMessage]: langchain消息格式列表
        """
        langchain_messages = []
        for msg in messages:
            role = msg['role'].lower()
            content = msg['content']
            
            if role == 'system':
                langchain_messages.append(SystemMessage(content=content))
            elif role == 'user':
                langchain_messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                langchain_messages.append(AIMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))
        
        return langchain_messages
    
    @staticmethod
    def extract_latest_input(messages: List[Dict[str, str]]) -> tuple:
        """从消息列表中提取最新输入和历史消息
        
        Args:
            messages: 消息列表
            
        Returns:
            tuple: (latest_input, chat_history)
        """
        if messages and isinstance(messages[-1], dict) and "content" in messages[-1]:
            latest_input = messages[-1]["content"]
            chat_history = messages[:-1]
            return latest_input, chat_history
        return "", []