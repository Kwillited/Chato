"""对话相关业务逻辑服务"""
import sys
import uuid
import json
from datetime import datetime
from app.services.data_service import DataService
from app.services.base_service import BaseService
from app.utils.response_strategy.handler import ResponseHandler
from app.utils import FileUtils
from app.utils.model import ModelUtils
from app.utils.message_builder import MessageBuilder
from app.utils import ValidationUtils, handle_errors, handle_db_errors
from app.utils.logging_utils import LoggingUtils

class ChatService(BaseService):
    """对话服务类，封装所有对话相关的业务逻辑"""
    
    def __init__(self):
        """初始化对话服务"""
        super().__init__()
    
    def _get_current_timestamp(self):
        """获取当前时间戳（ISO格式）"""
        return datetime.now().isoformat()
    
    @handle_errors(default_return=[])
    def get_chats(self):
        """获取所有对话"""
        # 直接从内存数据库获取对话
        return DataService.get_chats()

    def get_chat(self, chat_id):
        """获取单个对话记录（按ID）"""
        # 从内存数据库获取
        return DataService.get_chat_by_id(chat_id)

    @handle_db_errors(default_return=False)
    def delete_chat(self, chat_id):
        """删除单个对话记录（按ID）"""
        # 从内存数据库中删除
        DataService.remove_chat(chat_id)
        
        return True

    @handle_db_errors(default_return=False)
    def delete_all_chats(self):
        """删除所有对话记录"""
        # 清空内存中的对话数据
        DataService.clear_chats()
        
        return True
    
    @handle_db_errors(default_return=False)
    def update_chat_pin(self, chat_id, pinned):
        """更新对话置顶状态"""
        # 从内存获取对话信息
        chat = DataService.get_chat_by_id(chat_id)
        if not chat:
            return False
        
        # 更新内存中的对话
        updated_at = self._get_current_timestamp()
        chat['pinned'] = bool(pinned)
        chat['updatedAt'] = updated_at
        DataService.set_dirty_flag('chats', True)
        
        return True
    
    def update_chat_and_save(self, chat, message_text, user_message, ai_message, now):
        """更新对话并保存"""
        from app.core.logging_config import logger
        from app.core.cache import cache_manager
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
        cache_manager.set_chat(chat_id, chat)
        logger.info(f"更新缓存并标记对话为脏: chat_id={chat_id}")
        
        # 所有操作都在内存中完成，脏标记已设置，自动保存机制会处理持久化
        logger.info(f"对话更新成功，消息已保存: chat_id={chat_id}, 消息总数: {len(chat.get('messages', []))}")

    def process_uploaded_files(self, files):
        """处理上传的文件，保存到临时目录并提取内容
        
        参数:
            files: 文件列表
        
        返回:
            提取的文件内容列表
        """
        return FileUtils.process_uploaded_files(files)
    
    @handle_errors(default_return=None)
    def create_agent_session(self, chat_id, graph_state=None, current_node="", step_count=0):
        """
        创建新的智能体会话
        
        参数:
            chat_id: 对话ID
            graph_state: 图状态（JSON格式）
            current_node: 当前节点
            step_count: 步骤计数
        
        返回:
            创建的智能体会话
        """
        # 验证对话ID格式
        ValidationUtils.validate_uuid(chat_id, param_name='对话ID')
        
        # 验证当前节点
        ValidationUtils.validate_string_parameter(
            '当前节点', current_node, allow_empty=True
        )
        
        # 验证步骤计数
        ValidationUtils.validate_number(
            step_count, param_name='步骤计数', min_value=0, allow_zero=True
        )
        
        # 验证图状态
        if graph_state is not None:
            ValidationUtils.validate_dict_parameter(
                '图状态', graph_state, optional_keys=['messages', 'loop_count', 'current_node']
            )
        
        session_id = str(uuid.uuid4())
        now = self._get_current_timestamp()
        
        # 创建智能体会话字典
        session_dict = {
            'id': session_id,
            'chat_id': chat_id,
            'created_at': now,
            'updated_at': now,
            'graph_state': graph_state,
            'current_node': current_node,
            'step_count': step_count
        }
        
        # 添加到内存数据库
        DataService.add_agent_session(session_dict)
        
        return session_dict
    
    @handle_errors(default_return=None)
    def get_agent_session(self, session_id):
        """
        获取智能体会话
        
        参数:
            session_id: 智能体会话ID
        
        返回:
            智能体会话
        """
        # 验证会话ID格式
        ValidationUtils.validate_uuid(session_id, param_name='智能体会话ID')
        
        # 从内存数据库获取
        session = DataService.get_agent_session_by_id(session_id)
        return session
    
    @handle_errors(default_return=None)
    def update_agent_session(self, session_id, graph_state=None, current_node=None, step_count=None):
        """
        更新智能体会话
        
        参数:
            session_id: 智能体会话ID
            graph_state: 图状态（JSON格式）
            current_node: 当前节点
            step_count: 步骤计数
        
        返回:
            更新后的智能体会话
        """
        # 验证会话ID格式
        ValidationUtils.validate_uuid(session_id, param_name='智能体会话ID')
        
        # 验证当前节点（如果提供）
        if current_node is not None:
            ValidationUtils.validate_string_parameter(
                '当前节点', current_node, allow_empty=True
            )
        
        # 验证步骤计数（如果提供）
        if step_count is not None:
            ValidationUtils.validate_number(
                step_count, param_name='步骤计数', min_value=0, allow_zero=True
            )
        
        # 验证图状态（如果提供）
        if graph_state is not None:
            ValidationUtils.validate_dict_parameter(
                '图状态', graph_state, optional_keys=['messages', 'loop_count', 'current_node', 'steps']
            )
        
        now = self._get_current_timestamp()
        
        # 更新内存数据库
        session = DataService.get_agent_session_by_id(session_id)
        if session:
            updated_session = session.copy()
            updated_session['updated_at'] = now
            if graph_state is not None:
                updated_session['graph_state'] = graph_state
            if current_node is not None:
                updated_session['current_node'] = current_node
            if step_count is not None:
                updated_session['step_count'] = step_count
            
            DataService.update_agent_session(session_id, updated_session)
            return updated_session
        
        return None
    
    @handle_errors(default_return=False)
    def delete_agent_session(self, session_id):
        """
        删除智能体会话
        
        参数:
            session_id: 智能体会话ID
        
        返回:
            是否删除成功
        """
        # 验证会话ID格式
        ValidationUtils.validate_uuid(session_id, param_name='智能体会话ID')
        
        # 从内存数据库删除
        DataService.remove_agent_session(session_id)
        
        return True
    
    @handle_errors(default_return=[])
    def get_agent_sessions_by_chat_id(self, chat_id):
        """
        获取对话的所有智能体会话
        
        参数:
            chat_id: 对话ID
        
        返回:
            智能体会话列表
        """
        # 验证对话ID格式
        ValidationUtils.validate_uuid(chat_id, param_name='对话ID')
        
        # 从内存数据库获取
        sessions = DataService.get_agent_sessions_by_chat_id(chat_id)
        return sessions
    
    @handle_errors(default_return=None)
    def get_latest_agent_session(self, chat_id):
        """
        获取对话的最新智能体会话
        
        参数:
            chat_id: 对话ID
        
        返回:
            最新的智能体会话
        """
        # 验证对话ID格式
        ValidationUtils.validate_uuid(chat_id, param_name='对话ID')
        
        # 从内存数据库获取
        session = DataService.get_latest_agent_session(chat_id)
        return session
    
    def _parse_request_data(self, data):
        """解析请求数据
        
        参数:
            data: 包含所有必要信息的请求数据对象
        
        返回:
            解析后的请求参数
        """
        # 从数据中提取所需参数
        message_text = data.get('message')
        model_name = data.get('model', '')
        user_model_params = data.get('modelParams', {})
        rag_config = data.get('ragConfig', {})
        rag_enabled = rag_config.get('enabled', False)
        stream = data.get('stream', False)
        deep_thinking = data.get('deepThinking', False)
        use_agent = data.get('agent', False)
        web_search_enabled = data.get('webSearchEnabled', False)
        files = data.get('files', [])
        # 新增：获取用户选择的消息ID列表
        selected_message_ids = data.get('selectedMessageIds', None)
        
        # 添加调试日志，显示后端接收的参数
        from app.core.logging_config import logger
        logger.debug(f"完整请求数据: {data}")
        logger.debug(f"后端接收参数: message={message_text[:50]}{'...' if len(message_text) > 50 else ''}, model={model_name}, files={len(files)} 个文件, selectedMessageIds={selected_message_ids}, webSearchEnabled={web_search_enabled}")
        
        return {
            'message_text': message_text,
            'model_name': model_name,
            'user_model_params': user_model_params,
            'rag_enabled': rag_enabled,
            'rag_config': rag_config,  # 添加完整的ragConfig
            'stream': stream,
            'deep_thinking': deep_thinking,
            'use_agent': use_agent,
            'web_search_enabled': web_search_enabled,
            'files': files,
            # 新增：返回用户选择的消息ID列表
            'selected_message_ids': selected_message_ids
        }
    
    def _validate_request(self, chat_id, parsed_model_name, model):
        """
        验证请求参数
        
        参数:
            chat_id: 对话ID
            parsed_model_name: 解析后的模型名称
            model: 模型配置
        
        返回:
            (is_valid, error_response, error_code, chat)
        """
        try:
            # 导入验证工具类
            from app.utils.validators import ValidationUtils
            
            # 验证对话ID格式
            ValidationUtils.validate_uuid(chat_id, param_name='对话ID')
            
            # 验证模型名称
            ValidationUtils.validate_string_parameter(
                '模型名称', parsed_model_name, min_length=1
            )
            
            # 验证对话是否存在
            chat = self.get_chat(chat_id)
            if not chat:
                # 对话不存在，自动创建新对话（使用前端传递的UUID）
                from app.core.logging_config import logger
                logger.info(f'对话不存在，自动创建新对话: {chat_id}')
                
                # 创建新对话对象
                now = datetime.now().isoformat()
                new_chat = {
                    'id': chat_id,
                    'title': '新对话',
                    'preview': '',
                    'createdAt': now,
                    'updatedAt': now,
                    'messages': []
                }
                
                # 保存到内存数据库
                DataService.add_chat(new_chat)
                chat = new_chat
            
            # 验证模型配置
            if not model:
                return False, {'error': f'模型 {parsed_model_name} 不存在'}, 400, None
            
            return True, None, None, chat
        except ValueError as e:
            return False, {'error': str(e)}, 400, None
    
    async def _process_message(self, chat, parsed_data, parsed_model_name, parsed_version_name, model_display_name, model):
        """处理消息发送逻辑
        
        参数:
            chat: 对话对象
            parsed_data: 解析后的请求参数
            parsed_model_name: 解析后的模型名称
            parsed_version_name: 解析后的模型版本
            model_display_name: 模型显示名称
            model: 模型配置
        
        返回:
            响应结果
        """
        from app.core.logging_config import logger
        message_text = parsed_data['message_text']
        user_model_params = parsed_data['user_model_params']
        rag_enabled = parsed_data['rag_enabled']
        rag_config = parsed_data['rag_config']
        stream = parsed_data['stream']
        deep_thinking = parsed_data['deep_thinking']
        use_agent = parsed_data['use_agent']
        web_search_enabled = parsed_data['web_search_enabled']
        files = parsed_data['files']
        # 新增：获取用户选择的消息ID列表
        selected_message_ids = parsed_data.get('selected_message_ids', None)
        
        now = datetime.now().isoformat()
        
        # 获取模型默认参数
        model_params = {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 1,
            'top_k': 50,
            'frequency_penalty': 1,  # 固定默认值为 1
            # 注意：frequency_penalty 会被映射为 Ollama 的 repeat_penalty 参数
            # 设置为 1 可以有效减少模型生成重复内容的可能性
            # 重要：当设置为 0 时，会导致 Ollama 的 qwen2.5 模型出现断言错误
            # 但 qwen3 模型不受此影响
            'stream': stream,  # 将 stream 参数添加到 model_params 中
            'deepThinking': deep_thinking  # 添加深度思考参数
        }
        # 合并用户自定义参数，但强制保留 frequency_penalty 的默认值
        # 这样做是为了确保所有对话都使用一致的重复惩罚值，避免前端缓存旧设置导致的问题
        temp_params = {**user_model_params}
        if 'frequency_penalty' in temp_params:
            # 删除用户参数中的 frequency_penalty，确保使用后端的默认值
            del temp_params['frequency_penalty']
        model_params.update(temp_params)
        
        # 处理上传的文件
        file_contents = self.process_uploaded_files(files)
        
        # 合并文件内容到消息文本
        full_message_text = message_text
        if file_contents:
            full_message_text += "\n\n" + "\n\n".join(file_contents)
        
        # 调试RAG调用
        logger.debug(f"RAG: rag_enabled={rag_enabled}, message={full_message_text[:20]}{'...' if len(full_message_text) > 20 else ''}")
        
        # 调用RAG系统构造增强提示，传递完整的ragConfig
        context_docs = None
        if rag_enabled:
            logger.debug("准备执行RAG搜索")
            # 执行RAG搜索获取上下文文档
            from app.services.vector.vector_service import VectorService
            vector_service = VectorService()
            context_docs, _ = vector_service.perform_rag_search(full_message_text, rag_config.get('selectedFolders', []))
            logger.debug(f"找到 {len(context_docs)} 个相关文档片段")
        else:
            logger.debug("RAG未启用")
        
        # 处理网络搜索
        web_search_results = None
        if web_search_enabled:
            logger.debug("准备执行网络搜索")
            from app.services.web.web_search_service import WebSearchService
            web_search_service = WebSearchService()
            web_search_results = await web_search_service.perform_web_search(full_message_text)
            logger.debug(f"网络搜索结果: {web_search_results}")
        else:
            logger.debug("网络搜索未启用")
        
        # 使用原始消息文本，RAG上下文会在构建消息列表时添加到SystemMessage中
        enhanced_question = full_message_text
        
        # 创建用户消息，使用增强后的问题作为内容
        user_message = {
            'id': str(uuid.uuid4()),
            'role': 'user',
            'content': enhanced_question,
            'createdAt': now,
            'files': files  # 保存原始文件信息
        }
        chat['messages'].append(user_message)
        
        # 构建模型输入
        model_messages = MessageBuilder.build_messages_from_chat(
            chat_id=chat['id'],
            query=enhanced_question,
            rag_enabled=rag_enabled,
            agent_enabled=use_agent,
            context_docs=context_docs,
            selected_message_ids=selected_message_ids,
            web_search_enabled=web_search_enabled,
            web_search_results=web_search_results
        )
        
        # 根据stream和agent的值决定返回类型
        if stream:
            # 所有流式对话（包括智能体的流式模式）都使用 handle_streaming_response
            # 内部会根据 use_agent 参数选择对应的策略
            return await ResponseHandler.handle_streaming_response(
                chat, full_message_text, user_message, now,
                model_messages, parsed_model_name, parsed_version_name, 
                model_params, model_display_name, use_agent,
                model=model,  # 传递模型配置
                chat_service=self
            )
        else:
            # 所有非流式对话都使用 handle_regular_response
            return await ResponseHandler.handle_regular_response(
                chat, full_message_text, user_message, now,
                model_messages, parsed_model_name, parsed_version_name, 
                model_params, model_display_name, use_agent,
                model=model,  # 传递模型配置
                chat_service=self
            )
    
    async def send_message(self, chat_id, data):
            """发送消息（应用层）
            
            参数:
                chat_id: 对话ID
                data: 包含所有必要信息的请求数据对象
            """
            # 解析请求数据
            parsed_data = self._parse_request_data(data)
            
            # 使用辅助函数解析模型信息
            parsed_model_name, parsed_version_name, model_display_name = ModelUtils.parse_model_info(parsed_data['model_name'])
            
            # 获取模型配置
            model = DataService.get_model_by_name(parsed_model_name)
            
            # 验证请求参数并获取对话对象
            is_valid, error_response, error_code, chat = self._validate_request(chat_id, parsed_model_name, model)
            if not is_valid:
                return error_response, error_code
            
            # 处理消息发送逻辑
            return await self._process_message(chat, parsed_data, parsed_model_name, parsed_version_name, model_display_name, model)