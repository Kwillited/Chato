"""对话相关业务逻辑服务"""
import sys
import uuid
import json
from datetime import datetime
from app.services.data_service import DataService
from app.services.base_service import BaseService
from app.utils.response_formatter import ResponseFormatter
from app.utils import FileUtils
from app.utils.model_utils import ModelUtils

class ChatService(BaseService):
    """对话服务类，封装所有对话相关的业务逻辑"""
    
    def __init__(self, chat_repo=None, message_repo=None, agent_session_repo=None):
        """初始化对话服务
        
        Args:
            chat_repo: 对话仓库实例（保持兼容性，实际不再使用）
            message_repo: 消息仓库实例（保持兼容性，实际不再使用）
            agent_session_repo: 智能体会话仓库实例（保持兼容性，实际不再使用）
        """
        # 保持兼容性，但不再使用这些参数
        pass
    
    def get_chats(self):
        """获取所有对话"""
        from app.core.logging_config import logger
        try:
            # 直接从内存数据库获取对话
            memory_chats = DataService.get_chats()
            return memory_chats
        except Exception as e:
            # 记录错误日志
            logger.error(f"获取对话列表失败: {str(e)}")
            # 失败时返回内存数据库中的对话
            return DataService.get_chats()

    def create_chat(self, title=None):
        """创建新对话"""
        from app.core.logging_config import logger
        try:
            chat_id = str(uuid.uuid4())  # 生成唯一对话ID
            now = datetime.now().isoformat()  # 时间戳（ISO格式）
            
            title = title or '新对话'
            
            # 创建对话对象
            new_chat = {
                'id': chat_id,
                'title': title,
                'preview': '',
                'createdAt': now,
                'updatedAt': now,
                'messages': []
            }
            
            # 保存到内存数据库
            DataService.add_chat(new_chat)
            
            return new_chat
        except Exception as e:
            # 记录错误日志
            logger.error(f"创建对话失败: {str(e)}")
            # 重新创建并只保存到内存
            chat_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            title = title or '新对话'
            new_chat = {
                'id': chat_id,
                'title': title,
                'preview': '',
                'createdAt': now,
                'updatedAt': now,
                'messages': []
            }
            DataService.add_chat(new_chat)
            return new_chat

    def get_chat(self, chat_id):
        """获取单个对话记录（按ID）"""
        # 从内存数据库获取
        return DataService.get_chat_by_id(chat_id)

    def delete_chat(self, chat_id):
        """删除单个对话记录（按ID）"""
        try:
            # 从内存数据库中删除
            DataService.remove_chat(chat_id)
            
            return True
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"删除对话失败: {str(e)}")
            return True

    def delete_all_chats(self):
        """删除所有对话记录"""
        try:
            # 清空内存中的对话数据
            DataService.clear_chats()
            
            return True
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"删除所有对话失败: {str(e)}")
            return True
    
    def update_chat_pin(self, chat_id, pinned):
        """更新对话置顶状态"""
        try:
            # 从内存获取对话信息
            chat = DataService.get_chat_by_id(chat_id)
            if not chat:
                return False
            
            # 更新内存中的对话
            updated_at = datetime.now().isoformat()
            chat['pinned'] = bool(pinned)
            chat['updatedAt'] = updated_at
            DataService.set_dirty_flag('chats', True)
            
            return True
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"更新对话置顶状态失败: {str(e)}")
            return False
    
    def get_chat_context(self, chat_id, max_messages=10, deep_thinking=False):
        """
        获取对话上下文历史
        
        参数:
            chat_id: 对话ID
            max_messages: 最大获取的消息数量，默认10条
            deep_thinking: 是否启用深度思考，启用时保留think标签
            
        返回:
            格式化的上下文消息列表，或者None（如果对话不存在）
        """
        # 查找匹配ID的对话
        chat = self.get_chat(chat_id)
        if not chat:
            return None
        
        # 获取对话历史消息
        messages = chat.get('messages', [])
        
        # 如果消息数量超过max_messages，只保留最近的max_messages条
        if len(messages) > max_messages:
            messages = messages[-max_messages:]
        
        # 转换为适合模型输入的格式
        from app.utils.message_processor import MessageProcessor
        formatted_messages = []
        for msg in messages:
            # 确保消息有必要的字段
            if 'role' in msg and 'content' in msg:
                # 原始内容
                original_content = msg['content']
                # 剔除content中的think标签内容，仅当未启用深度思考时
                content = original_content
                
                if not deep_thinking:
                    # 使用工具类过滤think标签
                    content = MessageProcessor.filter_think_tags(content)
                else:
                    # 启用深度思考时，只去除多余的空白字符
                    content = content.strip()
                
                formatted_messages.append({
                    'role': msg['role'],
                    'content': content
                })
        
        return formatted_messages

    def get_rag_enhanced_prompt(self, question, rag_config=None):
        """RAG增强提示 - 直接使用生成服务的build_prompt方法"""
        # 只使用前端传递的enabled状态，其余配置从系统获取
        enabled = False
        selected_folders = []
        if rag_config and isinstance(rag_config, dict):
            enabled = rag_config.get('enabled', False)
            # 从前端传递的rag_config中获取selectedFolders
            selected_folders = rag_config.get('selectedFolders', [])
        
        from app.core.logging_config import logger
        logger.debug(f"RAG功能状态: enabled={enabled}")
        
        if not enabled:
            logger.debug("RAG功能未启用，返回原始问题")
            return question
        
        try:
            logger.debug("RAG功能已启用，开始执行RAG增强")
            # 直接使用生成服务的build_prompt方法，避免通过LangChainRAGService间接调用
            from app.core.config import config_manager
            from app.services.chat.generation_service import GenerationService
            from app.services.vector.vector_service import VectorService
            
            generation_service = GenerationService()
            vector_service = VectorService()
            
            # 从配置中获取参数
            config_vector = config_manager.get('vector', {})
            k = config_vector.get('top_k', 3)
            score_threshold = config_vector.get('score_threshold', 0.7)
            
            # 构建过滤器
            filter = None
            if selected_folders:
                # 如果有选中的文件夹，构建filter条件
                filter = {'folder_id': {'$in': selected_folders}}
            
            # 执行相似性搜索
            logger.debug(f"正在搜索相关文档，参数: k={k}, score_threshold={score_threshold}, filter={filter}")
            vector_results = vector_service.search_vectors(
                query=question,
                k=k,
                filter=filter,
                score_threshold=score_threshold
            )
            
            # 转换向量结果为文档列表
            context_docs = []
            if vector_results['success']:
                for result in vector_results['results']:
                    # 添加文档到上下文
                    context_docs.append(result)
            
            logger.debug(f"找到 {len(context_docs)} 个相关文档片段")
            
            # 使用生成服务的build_prompt方法构建提示
            enhanced_prompt = generation_service.build_prompt(question, context_docs)
            logger.debug(f"RAG增强提示构建完成，长度: {len(enhanced_prompt)} 字符")
            
            return enhanced_prompt
        except Exception as e:
            # 使用logger记录错误
            logger.error(f"RAG调用失败: {str(e)}")
            # 确保即使RAG失败，原始问题也能正常返回
            return question
    
    def generate_rag_response(self, query: str, chat_history: list, k=5):
        """生成增强响应
        
        Args:
            query (str): 用户查询
            chat_history (list): 聊天历史
            k (int): 返回结果数量
            
        Returns:
            dict: 生成增强响应结果
        """
        from app.core.logging_config import logger
        try:
            logger.debug(f"开始生成增强响应: 查询='{query[:50]}{'...' if len(query) > 50 else ''}'")
            # 1. 调用向量服务获取相关文档
            from app.services.vector.vector_service import VectorService
            vector_service = VectorService()
            vector_results = vector_service.search_vectors(query, k=k)
            
            if not vector_results['success']:
                logger.error(f"向量检索失败: {vector_results['message']}")
                return {
                    'success': False,
                    'message': '向量检索失败',
                    'response': '抱歉，我无法获取相关信息。'
                }
            
            # 2. 直接使用生成服务的 RAG 功能
            from app.services.chat.generation_service import GenerationService
            generation_service = GenerationService()
            
            # 调用生成服务的 generate_rag_response 方法
            rag_result = generation_service.generate_rag_response(
                query=query,
                context_docs=vector_results['results'],
                chat_history=chat_history
            )
            
            if rag_result['success']:
                logger.debug("生成增强响应成功")
                return {
                    'success': True,
                    'message': '生成增强响应成功',
                    'response': rag_result['answer'],
                    'context': rag_result['context_docs']
                }
            else:
                logger.error(f"生成响应失败: {rag_result.get('error', '未知错误')}")
                return {
                    'success': False,
                    'message': f'生成响应失败: {rag_result.get('error', '未知错误')}',
                    'response': '抱歉，我无法生成响应。'
                }
        except Exception as e:
            logger.error(f"生成增强响应失败: {str(e)}")
            return {
                'success': False,
                'message': f'生成增强响应失败: {str(e)}',
                'response': '抱歉，我无法生成响应。'
            }
    


    def parse_model_info(self, model_name):
        """
        解析前端发送的模型格式 "Ollama-qwen3:0.6b"
        返回: (模型名称, 版本名称, 模型显示名称)
        """
        return ModelUtils.parse_model_info(model_name)

    def validate_model(self, model_name):
        """
        验证模型是否存在且已配置
        返回: (model_object, error_response, error_code)
        """
        return ModelUtils.validate_model(model_name, DataService)
    
    def update_chat_and_save(self, chat, message_text, user_message, ai_message, now):
        """更新对话并保存"""
        from app.core.logging_config import logger
        chat_id = chat['id']
        user_msg_id = user_message['id']
        
        logger.debug(f"开始保存对话: chat_id={chat_id}, user_msg_id={user_msg_id}")
        
        # 先设置脏标记，确保数据会被保存
        DataService.set_dirty_flag('chats', True)
        logger.debug(f"设置脏标记: chats=True")
        
        # 更新内存中的对话
        # 更新对话的更新时间
        chat['updatedAt'] = now
        
        # 更新对话预览（使用消息的前50个字符）
        preview_text = message_text[:50] + (message_text[50:] and '...')
        chat['preview'] = preview_text
        logger.debug(f"更新对话预览: chat_id={chat_id}, preview={preview_text}")
        
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
                logger.debug(f"自动更新对话标题: chat_id={chat_id}, old_title={chat['title']}, new_title={new_title}")
        
        # 保存AI消息到内存（如果存在）
        if ai_message:
            ai_msg_id = ai_message['id']
            # 添加AI回复到对话（内存）
            chat['messages'].append(ai_message)
            logger.info(f"添加AI消息到内存: chat_id={chat_id}, ai_msg_id={ai_msg_id}, agent_node={ai_message.get('agent_node')}")
        
        # 所有操作都在内存中完成，脏标记已设置，自动保存机制会处理持久化
        logger.info(f"对话更新成功，等待自动保存: chat_id={chat_id}")

    def _prepare_messages_for_model(self, chat_id, enhanced_question, deep_thinking=False):
        """
        准备发送给模型的消息格式
        
        参数:
            chat_id: 对话ID
            enhanced_question: 增强后的问题
            deep_thinking: 是否启用深度思考
        
        返回:
            格式化的消息列表
        """
        # 获取对话上下文历史
        context_messages = self.get_chat_context(chat_id, deep_thinking=deep_thinking)
        
        # 准备消息格式，如果有上下文则使用上下文，否则使用当前问题
        if context_messages and len(context_messages) > 0:
            # 替换最后一条消息（即当前消息）的内容为增强后的问题
            messages = context_messages.copy()
            if messages:
                messages[-1]['content'] = enhanced_question
        else:
            # 如果没有上下文历史，只发送当前问题
            messages = [{'role': 'user', 'content': enhanced_question}]
        
        return messages
    
    async def chat_with_model_stream(self, model_name, messages, parsed_version_name, model_params, use_agent=False):
            """
            重构后的异步流式模型回复函数
            """
            # 1. 验证模型 (假设 validate_model 也是异步的，如果不是，去掉 await)
            model, error_response, _ = self.validate_model(model_name)
            if error_response:
                yield f'data: {json.dumps(error_response, ensure_ascii=False)}\n\n'
                return
            
            # 2. 获取版本配置
            version_config = self.get_version_config(model, parsed_version_name)
            
            if use_agent:
                # --- 智能体模式：全异步处理 ---
                try:
                    from app.llm.managers.model_manager import ModelManager
                    from app.llm.agent_wrapper import AgentWrapper
                    
                    # 获取基础模型驱动
                    base_driver = ModelManager.get_model_driver(model_name, model, version_config)
                    
                    # 创建并【异步】初始化智能体
                    agent_wrapper = AgentWrapper(base_driver)
                    
                    # ！！！核心改进 1：使用 await 而不是 asyncio.run
                    await agent_wrapper.initialize()
                    
                    # ！！！核心改进 2：直接异步遍历生成器
                    # 不要再手动去写 while __anext__，那是 asyncio.run 的死穴
                    print(f"[chat_with_model_stream] 开始接收智能体流式响应")
                    async for chunk in agent_wrapper.chat_stream(messages, model_params, use_agent=True):
                        # 这里的 chunk 已经是 AgentWrapper 处理好的 dict 或 str
                        print(f"[chat_with_model_stream] 接收到智能体响应块: {type(chunk).__name__}, content={str(chunk)[:100]}...")
                        yield chunk
                    
                except Exception as e:
                    self.log_error(f'调用智能体失败: {str(e)}')
                    yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
            else:
                # --- 普通模式 ---
                streaming_config = version_config.get('streaming_config', False)
                if not streaming_config:
                    yield f'data: {json.dumps({"error": "该模型未启用流式传输"}, ensure_ascii=False)}\n\n'
                    return

                try:
                    from app.llm.managers.model_manager import ModelManager
                    # ！！！核心改进 3：假设 ModelManager 支持异步流 (astream)
                    # 如果 ModelManager.chat 是同步的，建议也改为异步版本
                    stream = ModelManager.chat(model_name, model, version_config, messages, model_params)

                    # 如果 stream 是同步迭代器
                    if hasattr(stream, '__next__'):
                        for chunk in stream:
                            yield chunk
                    # 如果 stream 是异步迭代器 (推荐)
                    else:
                        async for chunk in stream:
                            yield chunk

                except Exception as e:
                    self.log_error(f'调用模型失败: {str(e)}')
                    yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'

    def process_uploaded_files(self, files):
        """处理上传的文件，保存到临时目录并提取内容
        
        参数:
            files: 文件列表
        
        返回:
            提取的文件内容列表
        """
        return FileUtils.process_uploaded_files(files)
    
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
        try:
            # 导入验证工具类
            from app.utils.validators import ValidationUtils
            
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
            now = datetime.now().isoformat()
            
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
        except ValueError as e:
            BaseService.log_error(f"创建智能体会话参数验证失败: {str(e)}")
            return None
        except Exception as e:
            BaseService.log_error(f"创建智能体会话失败: {str(e)}")
            return None
    
    def get_agent_session(self, session_id):
        """
        获取智能体会话
        
        参数:
            session_id: 智能体会话ID
        
        返回:
            智能体会话
        """
        try:
            # 导入验证工具类
            from app.utils.validators import ValidationUtils
            
            # 验证会话ID格式
            ValidationUtils.validate_uuid(session_id, param_name='智能体会话ID')
            
            # 从内存数据库获取
            session = DataService.get_agent_session_by_id(session_id)
            return session
        except ValueError as e:
            BaseService.log_error(f"获取智能体会话参数验证失败: {str(e)}")
            return None
        except Exception as e:
            BaseService.log_error(f"获取智能体会话失败: {str(e)}")
            return None
    
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
        try:
            # 导入验证工具类
            from app.utils.validators import ValidationUtils
            
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
            
            now = datetime.now().isoformat()
            
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
        except ValueError as e:
            BaseService.log_error(f"更新智能体会话参数验证失败: {str(e)}")
            return None
        except Exception as e:
            BaseService.log_error(f"更新智能体会话失败: {str(e)}")
            return None
    
    def delete_agent_session(self, session_id):
        """
        删除智能体会话
        
        参数:
            session_id: 智能体会话ID
        
        返回:
            是否删除成功
        """
        try:
            # 导入验证工具类
            from app.utils.validators import ValidationUtils
            
            # 验证会话ID格式
            ValidationUtils.validate_uuid(session_id, param_name='智能体会话ID')
            
            # 从内存数据库删除
            DataService.remove_agent_session(session_id)
            
            return True
        except ValueError as e:
            BaseService.log_error(f"删除智能体会话参数验证失败: {str(e)}")
            return False
        except Exception as e:
            BaseService.log_error(f"删除智能体会话失败: {str(e)}")
            return False
    
    def get_agent_sessions_by_chat_id(self, chat_id):
        """
        获取对话的所有智能体会话
        
        参数:
            chat_id: 对话ID
        
        返回:
            智能体会话列表
        """
        try:
            # 导入验证工具类
            from app.utils.validators import ValidationUtils
            
            # 验证对话ID格式
            ValidationUtils.validate_uuid(chat_id, param_name='对话ID')
            
            # 从内存数据库获取
            sessions = DataService.get_agent_sessions_by_chat_id(chat_id)
            return sessions
        except ValueError as e:
            BaseService.log_error(f"获取对话的智能体会话参数验证失败: {str(e)}")
            return []
        except Exception as e:
            BaseService.log_error(f"获取对话的智能体会话失败: {str(e)}")
            return []
    
    def get_latest_agent_session(self, chat_id):
        """
        获取对话的最新智能体会话
        
        参数:
            chat_id: 对话ID
        
        返回:
            最新的智能体会话
        """
        try:
            # 导入验证工具类
            from app.utils.validators import ValidationUtils
            
            # 验证对话ID格式
            ValidationUtils.validate_uuid(chat_id, param_name='对话ID')
            
            # 从内存数据库获取
            session = DataService.get_latest_agent_session(chat_id)
            return session
        except ValueError as e:
            BaseService.log_error(f"获取最新智能体会话参数验证失败: {str(e)}")
            return None
        except Exception as e:
            BaseService.log_error(f"获取最新智能体会话失败: {str(e)}")
            return None
    
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
        files = data.get('files', [])
        
        # 添加调试日志，显示后端接收的参数
        from app.core.logging_config import logger
        logger.debug(f"后端接收参数: message={message_text[:50]}{'...' if len(message_text) > 50 else ''}, model={model_name}, files={len(files)} 个文件")
        
        return {
            'message_text': message_text,
            'model_name': model_name,
            'user_model_params': user_model_params,
            'rag_enabled': rag_enabled,
            'rag_config': rag_config,  # 添加完整的ragConfig
            'stream': stream,
            'deep_thinking': deep_thinking,
            'use_agent': use_agent,
            'files': files
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
                return False, {'error': '对话不存在'}, 404, None
            
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
        files = parsed_data['files']
        
        now = datetime.now().isoformat()
        
        # 创建用户消息
        user_message = {
            'id': str(uuid.uuid4()),
            'role': 'user',
            'content': message_text,
            'createdAt': now,
            'files': files  # 保存原始文件信息
        }
        chat['messages'].append(user_message)
        
        # 获取模型默认参数
        model_params = {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 1,
            'top_k': 50,
            'frequency_penalty': 0,
            'stream': stream  # 将 stream 参数添加到 model_params 中
        }
        # 合并用户自定义参数
        model_params.update(user_model_params)
        
        # 处理上传的文件
        file_contents = self.process_uploaded_files(files)
        
        # 合并文件内容到消息文本
        full_message_text = message_text
        if file_contents:
            full_message_text += "\n\n" + "\n\n".join(file_contents)
        
        # 调试RAG调用
        logger.debug(f"RAG: rag_enabled={rag_enabled}, message={full_message_text[:20]}{'...' if len(full_message_text) > 20 else ''}")
        
        # 调用RAG系统构造增强提示，传递完整的ragConfig
        if rag_enabled:
            logger.debug("准备调用get_rag_enhanced_prompt方法")
            # 传递完整的ragConfig给RAG增强方法
            enhanced_question = self.get_rag_enhanced_prompt(full_message_text, rag_config)
            logger.debug(f"RAG增强完成，原始长度: {len(full_message_text)}, 增强后长度: {len(enhanced_question)}")
        else:
            logger.debug("RAG未启用，使用原始问题")
            enhanced_question = full_message_text
        
        # 保存用户消息到数据库，即使模型调用失败也要保存
        self.update_chat_and_save(chat, full_message_text, user_message, None, now)
        
        # 导入响应处理器
        from app.utils.response_handler import ResponseHandler
        
        # 根据stream和agent的值决定返回类型
        if stream and use_agent:
            # 调用异步方法
            return await ResponseHandler.handle_astream_events_response( # <--- 关键修改
                chat, full_message_text, user_message, now,
                enhanced_question, parsed_model_name, parsed_version_name, 
                model_params, model_display_name, deep_thinking, use_agent,
                chat_service=self
            )
        elif not stream and use_agent:
            return await ResponseHandler.handle_astream_response( # <--- 关键修改
                chat, full_message_text, user_message, now,
                enhanced_question, parsed_model_name, parsed_version_name, 
                model_params, model_display_name, deep_thinking, use_agent,
                chat_service=self
            )
        elif stream and not use_agent:
            return await ResponseHandler.handle_streaming_response( # <--- 关键修改
                chat, full_message_text, user_message, now,
                enhanced_question, parsed_model_name, parsed_version_name, 
                model_params, model_display_name, deep_thinking, use_agent,
                chat_service=self
            )
        else:
            return await ResponseHandler.handle_regular_response( # <--- 关键修改
                chat, full_message_text, user_message, now,
                enhanced_question, parsed_model_name, parsed_version_name, 
                model_params, model_display_name, deep_thinking, use_agent,
                chat_service=self
            )
    
    async def send_message(self, chat_id, data): # <--- 改为 async def
            """发送消息（应用层）
            
            参数:
                chat_id: 对话ID
                data: 包含所有必要信息的请求数据对象
            """
            # 解析请求数据
            parsed_data = self._parse_request_data(data)
            
            # 使用辅助函数解析模型信息
            parsed_model_name, parsed_version_name, model_display_name = self.parse_model_info(parsed_data['model_name'])
            
            # 获取模型配置
            model = DataService.get_model_by_name(parsed_model_name)
            
            # 验证请求参数并获取对话对象
            is_valid, error_response, error_code, chat = self._validate_request(chat_id, parsed_model_name, model)
            if not is_valid:
                return error_response, error_code
            
            # 处理消息发送逻辑
            return await self._process_message(chat, parsed_data, parsed_model_name, parsed_version_name, model_display_name, model)