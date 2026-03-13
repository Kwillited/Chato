"""核心消息处理模块"""
from typing import List, Dict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
import uuid
from app.core.logging_config import logger


class MessageSystem:
    """核心消息处理系统，包含消息格式转换、输入提取、标签过滤、消息创建等功能"""
    
    # 消息格式转换相关方法
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
    
    @staticmethod
    def filter_think_tags(content: str) -> str:
        """过滤内容中的think标签
        
        Args:
            content: 原始内容
            
        Returns:
            过滤后的内容
        """
        # 定义可能的think标签格式
        think_tag_pairs = [
            ('<think>', '</think>'),  # 尖括号格式
            ('[think]', '[/think]'),  # 方括号格式
        ]
        
        # 对每种标签格式进行过滤
        for opening_tag, closing_tag in think_tag_pairs:
            while opening_tag in content:
                start = content.find(opening_tag)
                if start != -1:
                    # 从start + len(opening_tag)的位置开始查找结束标签
                    end = content.find(closing_tag, start + len(opening_tag))
                    if end != -1:
                        # 保留开始标签前的内容和结束标签后的内容
                        content = content[:start] + content[end + len(closing_tag):]
                    else:
                        break
        
        # 去除多余的空白字符
        return content.strip()
    
    # 消息创建相关方法
    @staticmethod
    def create_ai_message(now, content, model_display_name, files=None, 
                         reasoning_content=None, 
                         agent_node="", agent_step=0, agent_metadata=""):
        """创建统一格式的AI消息
        
        Args:
            now: 当前时间戳
            content: 回复内容
            model_display_name: 模型显示名称
            files: 相关文件列表
            reasoning_content: 推理内容
            agent_node: 智能体节点名称
            agent_step: 智能体步骤
            agent_metadata: 智能体元数据
            
        Returns:
            统一格式的AI消息
        """
        ai_message_id = str(uuid.uuid4())
        ai_message = {
            'id': ai_message_id,
            'role': 'assistant',
            'content': content,
            'reasoning_content': reasoning_content,
            'createdAt': now,
            'model': model_display_name,
            'files': files or [],
            'agent_node': agent_node,
            'agent_step': agent_step,
            'agent_metadata': agent_metadata
        }
        logger.debug(f"创建AI消息: id={ai_message_id}, model={model_display_name}, agent_step={agent_step}, content_length={len(content)}")
        return ai_message
