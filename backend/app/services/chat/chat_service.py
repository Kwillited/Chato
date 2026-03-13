"""对话相关业务逻辑服务"""
import uuid
from datetime import datetime
from app.services.data_service import DataService
from app.services.base_service import BaseService
from app.utils import ValidationUtils, handle_errors, handle_db_errors

class ChatService(BaseService):
    """对话服务类，封装所有对话相关的业务逻辑"""
    
    def __init__(self):
        """初始化对话服务"""
        super().__init__()
        self.data_service = DataService()
    
    def _get_current_timestamp(self):
        """获取当前时间戳（ISO格式）"""
        return datetime.now().isoformat()
    
    @handle_errors(default_return=[])
    def get_chats(self):
        """获取所有对话"""
        # 直接从内存数据库获取对话
        return self.data_service.get_chats()

    def get_chat(self, chat_id):
        """获取单个对话记录（按ID）"""
        # 从内存数据库获取
        return self.data_service.get_chat_by_id(chat_id)

    @handle_db_errors(default_return=False)
    def delete_chat(self, chat_id):
        """删除单个对话记录（按ID）"""
        # 从内存数据库中删除
        self.data_service.remove_chat(chat_id)
        
        return True

    @handle_db_errors(default_return=False)
    def delete_all_chats(self):
        """删除所有对话记录"""
        # 清空内存中的对话数据
        self.data_service.clear_chats()
        
        return True
    
    @handle_db_errors(default_return=False)
    def update_chat_pin(self, chat_id, pinned):
        """更新对话置顶状态"""
        # 从内存获取对话信息
        chat = self.data_service.get_chat_by_id(chat_id)
        if not chat:
            return False
        
        # 更新内存中的对话
        updated_at = self._get_current_timestamp()
        chat['pinned'] = bool(pinned)
        chat['updatedAt'] = updated_at
        self.data_service.set_dirty_flag('chats', True)
        
        return True
    
    def update_chat_and_save(self, chat, message_text, user_message, ai_message, now):
        """更新对话并保存"""
        from app.core.logging_config import logger
        chat_id = chat['id']
        user_msg_id = user_message['id']
        
        logger.info(f"开始保存对话: chat_id={chat_id}, user_msg_id={user_msg_id}")
        logger.info(f"对话当前消息数: {len(chat.get('messages', []))}")
        logger.info(f"用户消息内容: {user_message['content'][:50]}{'...' if len(user_message['content']) > 50 else ''}")
        
        # 更新内存中的对话
        # 更新对话的更新时间
        chat['updatedAt'] = now
        logger.info(f"更新对话时间: chat_id={chat_id}, updatedAt={now}")
        
        # 更新对话预览（使用消息的前50个字符）
        preview_text = message_text[:50] + (message_text[50:] and '...')
        chat['preview'] = preview_text
        logger.info(f"更新对话预览: chat_id={chat_id}, preview={preview_text}")
        
        # 自动更新对话标题（如果是首次消息且标题还是默认的"新对话"）
        new_title = chat['title']
        if chat['title'] == '新对话':
            # 检查是否是首次添加消息到对话（用户消息+AI消息）
            has_user_message = any(msg['role'] == 'user' for msg in chat['messages'])
            
            # 当有用户消息时更新标题
            if has_user_message:
                # 使用用户的第一条消息作为标题（截取前30个字符）
                new_title = message_text[:30] + (message_text[30:] and '...')
                chat['title'] = new_title
                logger.info(f"自动更新对话标题: chat_id={chat_id}, old_title={chat['title']}, new_title={new_title}")
        
        # 保存AI消息到内存（如果存在）
        if ai_message:
            ai_msg_id = ai_message['id']
            # 添加AI回复到对话（内存）
            chat['messages'].append(ai_message)
            logger.info(f"添加AI消息到内存: chat_id={chat_id}, ai_msg_id={ai_msg_id}, agent_node={ai_message.get('agent_node')}")
        
        # 更新缓存并只标记当前对话为脏
        self.data_service.add_chat(chat)
        logger.info(f"更新缓存并标记对话为脏: chat_id={chat_id}")
        
        # 所有操作都在内存中完成，脏标记已设置，自动保存机制会处理持久化
        logger.info(f"对话更新成功，消息已保存: chat_id={chat_id}, 消息总数: {len(chat.get('messages', []))}")