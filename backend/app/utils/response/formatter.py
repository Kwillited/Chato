"""回复格式化工具类"""
import json
import uuid
import re
from app.core.logging_config import logger
from app.services.base_service import BaseService


class ResponseFormatter:
    """回复格式化工具类，用于处理模型响应的格式化"""
    
    @staticmethod
    def create_ai_message(now, content, model_display_name, files=None):
        """创建标准格式的AI回复消息
        
        Args:
            now: 当前时间戳
            content: 回复内容
            model_display_name: 模型显示名称
            files: 相关文件列表
            
        Returns:
            标准格式的AI回复消息
        """
        ai_message_id = str(uuid.uuid4())
        ai_message = {
            'id': ai_message_id,
            'role': 'assistant',
            'content': content,
            'createdAt': now,
            'model': model_display_name,
            'files': files or []  # 添加files字段，默认空列表
        }
        logger.debug(f"创建AI消息: id={ai_message_id}, model={model_display_name}, content_length={len(content)}")
        return ai_message
    
    @staticmethod
    def process_think_tags(content):
        """处理内容中的Think标签，提取思考内容并移除标签
        
        Args:
            content: 包含思考标签的内容
            
        Returns:
            (thinking_content, actual_content): 思考内容和实际内容
        """
        think_pattern = re.compile(r'\s*<think>([\s\S]*?)</think>\s*', re.IGNORECASE)
        match = think_pattern.match(content)
        
        thinking_content = None
        actual_content = content
        
        if match:
            thinking_content = match.group(1)
            actual_content = think_pattern.sub('', content).strip()
        
        return thinking_content, actual_content
    
    @staticmethod
    def process_full_reply(full_reply, now, model_display_name):
        """处理完整回复，分离思考内容和实际内容
        
        Args:
            full_reply: 完整的回复内容
            now: 当前时间戳
            model_display_name: 模型显示名称
            
        Returns:
            标准格式的AI回复消息
        """
        thinking_content, actual_content = ResponseFormatter.process_think_tags(full_reply)
        
        # 创建AI回复，确保包含完整的模型和版本信息
        ai_message = ResponseFormatter.create_ai_message(now, actual_content, model_display_name)
        # 添加思考内容到AI消息
        ai_message['thinking'] = thinking_content
        
        return ai_message