"""对话相关业务逻辑服务"""
import sys
import uuid
import json
from datetime import datetime
from app.services.data_service import DataService
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.services.base_service import BaseService
from app.utils.data_utils import build_message_list, build_chat_dict
from app.utils.response_formatter import ResponseFormatter
from app.utils.file_processor import FileProcessor
from app.utils.model_utils import ModelUtils

class ChatService(BaseService):
    """对话服务类，封装所有对话相关的业务逻辑"""
    
    def __init__(self, chat_repo=None, message_repo=None):
        """初始化对话服务
        
        Args:
            chat_repo: 对话仓库实例，用于依赖注入
            message_repo: 消息仓库实例，用于依赖注入
        """
        self.chat_repo = chat_repo or ChatRepository()
        self.message_repo = message_repo or MessageRepository()
    
    def get_chats(self):
        """获取所有对话"""
        try:
            # 先从内存数据库获取对话
            memory_chats = DataService.get_chats()
            
            # 如果内存中有对话数据，直接返回
            if memory_chats:
                return memory_chats
            
            # 内存中没有对话数据，从SQLite数据库加载
            chats = self.chat_repo.get_all_chats()
            
            chat_list = []
            for chat in chats:
                # 直接访问对象属性，而不是使用下标访问
                chat_id = chat.id
                
                # 获取对话的所有消息
                messages = self.message_repo.get_messages_by_chat_id(chat_id)
                
                # 使用公共函数构建消息列表
                formatted_messages = build_message_list(messages)
                
                # 使用公共函数构建对话字典
                chat_dict = build_chat_dict(chat, formatted_messages)
                
                # 添加对话到列表
                chat_list.append(chat_dict)
            
            # 更新内存数据库
            DataService.get_chats().clear()
            DataService.get_chats().extend(chat_list)
            return chat_list
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"获取对话列表失败: {str(e)}")
            # 失败时返回内存数据库中的对话
            return DataService.get_chats()

    def create_chat(self, title=None):
        """创建新对话"""
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
            
            # 先更新内存数据库
            DataService.add_chat(new_chat)
            
            # 再保存到SQLite数据库
            self.chat_repo.create_chat(chat_id, title, '', now, now)
            
            return new_chat
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"创建对话失败: {str(e)}")
            # 尝试从内存中移除（如果已添加）
            try:
                DataService.remove_chat(chat_id)
            except:
                pass
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
        # 先尝试从内存获取
        chat = DataService.get_chat_by_id(chat_id)
        if chat:
            return chat
        
        try:
            # 从数据库获取
            chat_row = self.chat_repo.get_chat_by_id(chat_id)
            if not chat_row:
                return None
            
            # 获取对话的所有消息
            messages = self.message_repo.get_messages_by_chat_id(chat_id)
            
            # 使用公共函数构建消息列表
            formatted_messages = build_message_list(messages)
            
            # 使用公共函数构建对话字典
            chat = build_chat_dict(chat_row, formatted_messages)
            
            # 更新内存数据库
            existing_chat = DataService.get_chat_by_id(chat_id)
            if not existing_chat:
                DataService.get_chats().append(chat)
            return chat
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"获取对话失败: {str(e)}")
            return None

    def delete_chat(self, chat_id):
        """删除单个对话记录（按ID）"""
        try:
            # 先从内存数据库中删除
            DataService.remove_chat(chat_id)
            
            # 再从SQLite数据库中删除对话（级联删除消息）
            self.chat_repo.delete_chat(chat_id)
            
            return True
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"删除对话失败: {str(e)}")
            # 尝试重新添加到内存（如果删除SQLite失败）
            try:
                # 从SQLite重新加载该对话
                chat = self.get_chat(chat_id)
                if chat:
                    DataService.add_chat(chat)
            except:
                pass
            return True

    def delete_all_chats(self):
        """删除所有对话记录"""
        try:
            # 先清空内存中的对话数据
            DataService.clear_chats()
            
            # 再从数据库中删除所有对话和消息
            self.message_repo.delete_all_messages()
            self.chat_repo.delete_all_chats()
            
            return True
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"删除所有对话失败: {str(e)}")
            # 尝试从SQLite重新加载数据（如果删除SQLite失败）
            try:
                # 重新加载所有对话到内存
                self.get_chats()
            except:
                pass
            return True
    
    def update_chat_pin(self, chat_id, pinned):
        """更新对话置顶状态"""
        try:
            # 先从内存获取对话信息
            chat = DataService.get_chat_by_id(chat_id)
            if not chat:
                # 如果内存中没有，从SQLite加载
                chat_row = self.chat_repo.get_chat_by_id(chat_id)
                if not chat_row:
                    return False
                # 获取对话的所有消息
                messages = self.message_repo.get_messages_by_chat_id(chat_id)
                # 构建对话字典并添加到内存
                formatted_messages = build_message_list(messages)
                chat_dict = build_chat_dict(chat_row, formatted_messages)
                DataService.get_chats().append(chat_dict)
                chat = chat_dict
            
            # 更新内存中的对话
            updated_at = datetime.now().isoformat()
            chat['pinned'] = bool(pinned)
            chat['updatedAt'] = updated_at
            
            # 再更新SQLite数据库
            self.chat_repo.update_chat(
                chat_id=chat['id'],
                title=chat['title'] or '未命名对话',
                preview=chat.get('preview', ''),
                updated_at=updated_at,
                pinned=int(pinned)
            )
            
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
        formatted_messages = []
        for msg in messages:
            # 确保消息有必要的字段
            if 'role' in msg and 'content' in msg:
                # 原始内容
                original_content = msg['content']
                # 剔除content中的think标签内容，仅当未启用深度思考时
                content = original_content
                
                if not deep_thinking:
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
        
        self.log_info(f"📌 RAG功能状态: enabled={enabled}")
        
        if not enabled:
            self.log_info("❌ RAG功能未启用，返回原始问题")
            return question
        
        try:
            self.log_info("✅ RAG功能已启用，开始执行RAG增强")
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
            self.log_info(f"🔍 正在搜索相关文档，参数: k={k}, score_threshold={score_threshold}, filter={filter}")
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
            
            self.log_info(f"✅ 找到 {len(context_docs)} 个相关文档片段")
            
            # 使用生成服务的build_prompt方法构建提示
            enhanced_prompt = generation_service.build_prompt(question, context_docs)
            self.log_info(f"📝 RAG增强提示构建完成，长度: {len(enhanced_prompt)} 字符")
            self.log_info(f"📋 RAG增强提示内容: {enhanced_prompt}")
            
            return enhanced_prompt
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"RAG调用失败: {str(e)}")
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
        try:
            self.log_info(f"🚀 开始生成增强响应: 查询='{query[:50]}{'...' if len(query) > 50 else ''}'")
            # 1. 调用向量服务获取相关文档
            from app.services.vector.vector_service import VectorService
            vector_service = VectorService()
            vector_results = vector_service.search_vectors(query, k=k)
            
            if not vector_results['success']:
                self.log_error(f"❌ 向量检索失败: {vector_results['message']}")
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
                self.log_info(f"✅ 生成增强响应成功")
                return {
                    'success': True,
                    'message': '生成增强响应成功',
                    'response': rag_result['answer'],
                    'context': rag_result['context_docs']
                }
            else:
                self.log_error(f"❌ 生成响应失败: {rag_result.get('error', '未知错误')}")
                return {
                    'success': False,
                    'message': f'生成响应失败: {rag_result.get('error', '未知错误')}',
                    'response': '抱歉，我无法生成响应。'
                }
        except Exception as e:
            self.log_error(f"❌ 生成增强响应失败: {str(e)}")
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
        
        # 先更新内存中的对话
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
            # 或者是否是首次调用update_chat_and_save且已有用户消息
            has_user_message = any(msg['role'] == 'user' for msg in chat['messages'])
            has_ai_message = any(msg['role'] == 'assistant' for msg in chat['messages'])
            
            # 当有用户消息且（有AI消息或没有AI消息但不是首次保存）时更新标题
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
            logger.info(f"添加AI消息到内存: chat_id={chat_id}, ai_msg_id={ai_msg_id}")
        
        try:
            # 开始事务
            from app.core.database import get_db
            db_session = next(get_db())
            logger.debug(f"开始事务: chat_id={chat_id}")
            
            # 再保存到SQLite数据库
            # 检查用户消息是否已经存在于数据库中，避免重复保存
            existing_user_message = self.message_repo.get_message_by_id(user_message['id'])
            if not existing_user_message:
                # 保存用户消息到数据库
                logger.debug(f"保存用户消息: chat_id={chat_id}, user_msg_id={user_msg_id}")
                self.message_repo.create_message(
                    message_id=user_message['id'],
                    chat_id=chat['id'],
                    role=user_message['role'],
                    actual_content=user_message['content'],
                    thinking=None,
                    created_at=user_message['createdAt'],
                    model=user_message.get('model'),
                    files=json.dumps(user_message.get('files', []))
                )
                logger.info(f"用户消息保存成功: chat_id={chat_id}, user_msg_id={user_msg_id}")
            else:
                logger.debug(f"用户消息已存在，跳过保存: chat_id={chat_id}, user_msg_id={user_msg_id}")
            
            # 保存AI消息到数据库（如果存在）
            if ai_message:
                ai_msg_id = ai_message['id']
                # 检查AI消息是否已经存在于数据库中，避免重复保存
                existing_ai_message = self.message_repo.get_message_by_id(ai_msg_id)
                if not existing_ai_message:
                    logger.info(f"开始保存AI消息: chat_id={chat_id}, ai_msg_id={ai_msg_id}")
                    try:
                        self.message_repo.create_message(
                            message_id=ai_msg_id,
                            chat_id=chat['id'],
                            role=ai_message['role'],
                            actual_content=ai_message['content'],
                            thinking=ai_message.get('thinking'),
                            created_at=ai_message['createdAt'],
                            model=ai_message.get('model'),
                            files=json.dumps(ai_message.get('files', []))
                        )
                        logger.info(f"✅ AI消息保存成功: chat_id={chat_id}, ai_msg_id={ai_msg_id}")
                    except Exception as e:
                        logger.error(f"❌ AI消息保存失败: chat_id={chat_id}, ai_msg_id={ai_msg_id}, error={str(e)}")
                else:
                    logger.info(f"⚠️ AI消息已存在，跳过保存: chat_id={chat_id}, ai_msg_id={ai_msg_id}")
            
            # 更新对话信息到数据库
            logger.debug(f"更新对话信息: chat_id={chat_id}, title={new_title}")
            self.chat_repo.update_chat(
                chat_id=chat['id'],
                title=new_title,
                preview=preview_text,
                updated_at=now,
                pinned=chat.get('pinned', 0)
            )
            
            # 提交事务
            db_session.commit()
            logger.debug(f"事务提交成功: chat_id={chat_id}")
            
            # 添加直接保存成功日志
            if ai_message:
                logger.info(f"Direct save succeeded: chat_id={chat_id}, user_msg_id={user_msg_id}, ai_msg_id={ai_message['id']}")
            else:
                logger.info(f"Direct save succeeded: chat_id={chat_id}, user_msg_id={user_msg_id}")
        except Exception as e:
            # 回滚事务
            logger.error(f"保存对话失败，开始回滚: chat_id={chat_id}, error={str(e)}")
            from app.core.database import get_db
            db_session = next(get_db())
            db_session.rollback()
            logger.debug(f"事务回滚成功: chat_id={chat_id}")
            
            # 使用BaseService的日志方法
            BaseService.log_error(f"Failed to update chat: {str(e)}")
            # 脏标记已经设置，自动保存机制会处理剩余工作
            logger.info(f"Direct save failed, relying on auto-save: chat_id={chat_id}, error={str(e)}")

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
    
    def chat_with_model_stream(self, model_name, messages, parsed_version_name, temperature=0.7, use_agent=False):
        """
        直接调用的流式模型回复函数
        
        参数:
            model_name: 模型名称
            messages: 消息列表
            temperature: 随机性参数，默认0.7
            parsed_version_name: 解析后的模型版本名称（可选）
            use_agent: 是否使用智能体模式
        
        返回:
            生成器，产生流式响应块
        """
        # 使用通用验证函数验证模型
        model, error_response, _ = self.validate_model(model_name)
        if error_response:
            error_data = error_response
            yield f'data: {json.dumps(error_data, ensure_ascii=False)}\n\n'
            return
        
        # 获取版本配置
        version_id = parsed_version_name
        version_config = self.get_version_config(model, version_id)
        
        if use_agent:
            # 智能体模式
            try:
                from app.models.model_manager import ModelManager
                from app.models.agent_wrapper import AgentWrapper
                import asyncio
                
                # 获取基础模型驱动
                base_driver = ModelManager.get_model_driver(model_name, model, version_config)
                
                # 创建智能体包装器
                agent_wrapper = AgentWrapper(base_driver)
                
                # 初始化智能体
                asyncio.run(agent_wrapper.initialize())
                
                # 调用智能体流式方法
                # 注意：agent_wrapper.chat_stream 是异步生成器，需要在同步函数中使用 asyncio.run 处理
                import asyncio
                
                async def stream_agent_response():
                    async for chunk in agent_wrapper.chat_stream(messages, temperature, use_agent=True):
                        yield chunk
                
                # 将异步生成器转换为同步迭代
                async_gen = stream_agent_response()
                while True:
                    try:
                        chunk = asyncio.run(async_gen.__anext__())
                        yield chunk
                    except StopAsyncIteration:
                        break
                
            except Exception as e:
                # 捕获所有异常并返回错误信息
                BaseService.log_error(f'调用智能体失败: {str(e)}')
                response_data = {'error': str(e)}
                yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
        else:
            # 普通模式
            # 检查是否启用了流式传输
            streaming_config = version_config.get('streaming_config', False)
            if not streaming_config:
                error_data = {'error': '该模型未启用流式传输'}
                yield f'data: {json.dumps(error_data, ensure_ascii=False)}\n\n'
                return

            try:
                from app.models.model_manager import ModelManager
                stream = ModelManager.chat(model_name, model, version_config, messages, temperature, stream=True)

                # 直接迭代并返回流式响应
                for chunk in stream:
                    yield chunk

            except Exception as e:
                # 捕获所有异常并返回错误信息
                BaseService.log_error(f'调用模型失败: {str(e)}')
                response_data = {'error': str(e)}
                yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'

    def process_uploaded_files(self, files):
        """处理上传的文件，保存到临时目录并提取内容
        
        参数:
            files: 文件列表
        
        返回:
            提取的文件内容列表
        """
        return FileProcessor.process_uploaded_files(files)
    
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
        
        # 添加详细日志，显示后端接收的所有参数
        self.log_info(f"🔧 后端接收参数调试:")
        self.log_info(f"   message: {message_text[:50]}{'...' if len(message_text) > 50 else ''}")
        self.log_info(f"   model: {model_name}")
        self.log_info(f"   modelParams: {user_model_params}")
        self.log_info(f"   ragConfig: {rag_config}")
        self.log_info(f"   rag_enabled: {rag_enabled}")
        self.log_info(f"   stream: {stream}")
        self.log_info(f"   deepThinking: {deep_thinking}")
        self.log_info(f"   agent: {use_agent}")
        self.log_info(f"   files: {len(files)} 个文件")
        
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
        """验证请求参数
        
        参数:
            chat_id: 对话ID
            parsed_model_name: 解析后的模型名称
            model: 模型配置
        
        返回:
            (is_valid, error_response, error_code)
        """
        # 查找匹配ID的对话
        chat = self.get_chat(chat_id)
        if not chat:
            return False, {'error': '对话不存在'}, 404
        
        # 如果没有传递模型，返回错误
        if not parsed_model_name:
            return False, {'error': '请指定模型'}, 400
        
        # 获取模型配置
        if not model:
            return False, {'error': f'模型 {parsed_model_name} 不存在'}, 400
        
        return True, None, None
    
    def _process_message(self, chat_id, parsed_data):
        """处理消息发送逻辑
        
        参数:
            chat_id: 对话ID
            parsed_data: 解析后的请求参数
        
        返回:
            响应结果
        """
        message_text = parsed_data['message_text']
        model_name = parsed_data['model_name']
        user_model_params = parsed_data['user_model_params']
        rag_enabled = parsed_data['rag_enabled']
        rag_config = parsed_data['rag_config']
        stream = parsed_data['stream']
        deep_thinking = parsed_data['deep_thinking']
        use_agent = parsed_data['use_agent']
        files = parsed_data['files']
        
        # 查找匹配ID的对话
        chat = self.get_chat(chat_id)
        
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
        
        # 使用辅助函数解析模型信息
        parsed_model_name, parsed_version_name, model_display_name = self.parse_model_info(model_name)
        
        # 获取模型配置
        model = DataService.get_model_by_name(parsed_model_name)
        
        # 获取模型默认参数
        model_params = {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 1,
            'frequency_penalty': 0
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
        self.log_info(f"🔧 调试RAG: rag_enabled={rag_enabled}, message={full_message_text[:20]}{'...' if len(full_message_text) > 20 else ''}")
        
        # 调用RAG系统构造增强提示，传递完整的ragConfig
        if rag_enabled:
            self.log_info("📞 准备调用get_rag_enhanced_prompt方法")
            # 传递完整的ragConfig给RAG增强方法
            enhanced_question = self.get_rag_enhanced_prompt(full_message_text, rag_config)
            self.log_info(f"📋 RAG增强完成，原始长度: {len(full_message_text)}, 增强后长度: {len(enhanced_question)}")
        else:
            self.log_info("⏭️  RAG未启用，使用原始问题")
            enhanced_question = full_message_text
        
        # 保存用户消息到数据库，即使模型调用失败也要保存
        self.update_chat_and_save(chat, full_message_text, user_message, None, now)
        
        # 导入响应处理器
        from app.utils.response_handler import ResponseHandler
        
        # 根据stream和agent的值决定返回类型
        if stream and use_agent:
            # 同为true用astream_events
            return ResponseHandler.handle_astream_events_response(chat, full_message_text, user_message, now,
                                                               enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name, deep_thinking, use_agent,
                                                               chat_service=self)
        elif not stream and not use_agent:
            # 同为false用astream
            return ResponseHandler.handle_astream_response(chat, full_message_text, user_message, now,
                                                       enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name, deep_thinking, use_agent,
                                                       chat_service=self)
        elif stream:
            # stream为true用普通流式
            return ResponseHandler.handle_streaming_response(chat, full_message_text, user_message, now,
                                                          enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name, deep_thinking, use_agent,
                                                          chat_service=self)
        else:
            # stream为false用普通响应处理
            return ResponseHandler.handle_regular_response(chat, full_message_text, user_message, now,
                                                      enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name, deep_thinking, use_agent,
                                                      chat_service=self)
    
    def send_message(self, chat_id, data):
        """发送消息（应用层）
        
        参数:
            chat_id: 对话ID
            data: 包含所有必要信息的请求数据对象
        """
        # 解析请求数据
        parsed_data = self._parse_request_data(data)
        
        # 使用辅助函数解析模型信息
        parsed_model_name, _, _ = self.parse_model_info(parsed_data['model_name'])
        
        # 获取模型配置
        model = DataService.get_model_by_name(parsed_model_name)
        
        # 验证请求参数
        is_valid, error_response, error_code = self._validate_request(chat_id, parsed_model_name, model)
        if not is_valid:
            return error_response, error_code
        
        # 处理消息发送逻辑
        return self._process_message(chat_id, parsed_data)