"""消息相关业务逻辑服务"""
import uuid
from datetime import datetime
from app.services.base_service import BaseService
from app.utils.response_strategy.handler import ResponseHandler
from app.utils import FileUtils
from app.utils.model import ModelUtils
from app.utils.message_builder import MessageBuilder
from app.utils import ValidationUtils

class MessageService(BaseService):
    """消息服务类，封装所有消息相关的业务逻辑"""
    
    def __init__(self, chat_service, vector_service, web_search_service):
        """初始化消息服务
        
        Args:
            chat_service: 对话服务实例，用于依赖注入
            vector_service: 向量服务实例，用于依赖注入
            web_search_service: 网络搜索服务实例，用于依赖注入
        """
        super().__init__()
        from app.core.service_container import service_container
        self.chat_service = chat_service
        self.vector_service = vector_service
        self.web_search_service = web_search_service
        self.data_service = service_container.get_service('data_service')
    
    def process_uploaded_files(self, files):
        """处理上传的文件，保存到临时目录并提取内容
        
        参数:
            files: 文件列表
        
        返回:
            提取的文件内容列表
        """
        return FileUtils.process_uploaded_files(files)
    
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
        self.log_debug(f"完整请求数据: {data}")
        self.log_debug(f"后端接收参数: message={message_text[:50]}{'...' if len(message_text) > 50 else ''}, model={model_name}, files={len(files)} 个文件, selectedMessageIds={selected_message_ids}, webSearchEnabled={web_search_enabled}")
        
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
            # 验证对话ID格式
            ValidationUtils.validate_uuid(chat_id, param_name='对话ID')
            
            # 验证模型名称
            ValidationUtils.validate_string_parameter(
                '模型名称', parsed_model_name, min_length=1
            )
            
            # 验证对话是否存在
            chat = self.chat_service.get_chat(chat_id)
            if not chat:
                # 对话不存在，自动创建新对话（使用前端传递的UUID）
                self.log_info(f'对话不存在，自动创建新对话: {chat_id}')
                
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
                self.data_service.add_chat(new_chat)
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
        
        now = self.get_current_timestamp()
        
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
        model_params = ModelUtils.merge_model_params(model_params, user_model_params)
        
        # 处理上传的文件
        file_contents = self.process_uploaded_files(files)
        
        # 合并文件内容到消息文本
        full_message_text = message_text
        if file_contents:
            full_message_text += "\n\n" + "\n\n".join(file_contents)
        
        # 调试RAG调用
        self.log_debug(f"RAG: rag_enabled={rag_enabled}, message={full_message_text[:20]}{'...' if len(full_message_text) > 20 else ''}")
        
        # 调用RAG系统构造增强提示，传递完整的ragConfig
        context_docs = None
        if rag_enabled:
            self.log_debug("准备执行RAG搜索")
            # 执行RAG搜索获取上下文文档
            context_docs, _ = self.vector_service.perform_rag_search(full_message_text, rag_config.get('selectedFolders', []))
            self.log_debug(f"找到 {len(context_docs)} 个相关文档片段")
        else:
            self.log_debug("RAG未启用")
        
        # 处理网络搜索
        web_search_results = None
        if web_search_enabled:
            self.log_debug("准备执行网络搜索")
            web_search_results = await self.web_search_service.perform_web_search(full_message_text)
            self.log_debug(f"网络搜索结果: {web_search_results}")
        else:
            self.log_debug("网络搜索未启用")
        
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
                chat_service=self.chat_service
            )
        else:
            # 所有非流式对话都使用 handle_regular_response
            return await ResponseHandler.handle_regular_response(
                chat, full_message_text, user_message, now,
                model_messages, parsed_model_name, parsed_version_name, 
                model_params, model_display_name, use_agent,
                model=model,  # 传递模型配置
                chat_service=self.chat_service
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
            model = self.data_service.get_model_by_name(parsed_model_name)
            
            # 验证请求参数并获取对话对象
            is_valid, error_response, error_code, chat = self._validate_request(chat_id, parsed_model_name, model)
            if not is_valid:
                return error_response, error_code
            
            # 处理消息发送逻辑
            return await self._process_message(chat, parsed_data, parsed_model_name, parsed_version_name, model_display_name, model)
