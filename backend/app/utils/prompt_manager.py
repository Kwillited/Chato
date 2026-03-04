"""提示词管理模块，集中管理所有提示词模板"""

import json
import os


class PromptManager:
    """提示词管理器，负责管理和构建各种类型的提示词"""
    
    # 单例模式
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PromptManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化提示词管理器"""
        # 加载配置
        self._load_config()
        
        # 定义默认提示词模板
        self._default_templates = {
            'chat': """你是一个AI助手，使用以下聊天历史来回答用户问题。如果你不知道答案，就说你不知道。保持回答简洁明了。\n\n{chat_history}\n\n用户问题：{query}""",
            'rag': """你是一个AI助手，使用以下上下文信息来回答用户问题。请严格基于提供的上下文信息进行回答，不要添加任何外部信息。如果你不知道答案，就说你不知道。保持回答简洁明了。\n\n{context}\n\n{chat_history}\n\n用户问题：{query}""",
            'agent': """你是一个强大的AI助手，能够使用工具来完成各种任务。请按照以下要求工作：
1. 分析用户需求，制定详细的执行计划
2. 如果需要，使用适当的工具来获取信息或执行操作
3. 提供完整、详细的响应，不要中途停止
4. 使用中文回答用户问题
5. 确保工具调用参数完整，格式正确
6. 生成响应时要完整，不要只输出部分内容

请始终提供完整的响应，确保用户能够获得满意的答案。"""
        }
    
    def _load_config(self):
        """加载配置文件"""
        # 构建配置文件路径
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        parent_dir = os.path.dirname(current_dir)
        grandparent_dir = os.path.dirname(parent_dir)
        
        # 正确的backend目录应该是祖父目录（H:\ChaTo\backend）
        backend_dir = grandparent_dir
        config_path = os.path.join(backend_dir, 'config', 'system_config.json')
        
        # 默认配置
        self._config = {
            'system_message': '你是ChaTo，一个智能AI助手。请根据用户的问题和对话历史，提供准确、详细、友好的回答。',
            'rag_system_message': '你是ChaTo，一个基于检索增强的智能AI助手。请严格基于提供的上下文信息来回答用户问题，不要添加任何外部信息。如果你不知道答案，就说你不知道。保持回答简洁明了。',
            'agent_system_message': '你是ChaTo，一个强大的AI助手，能够使用工具来完成各种任务。请按照以下要求工作：\n1. 分析用户需求，制定详细的执行计划\n2. 如果需要，使用适当的工具来获取信息或执行操作\n3. 提供完整、详细的响应，不要中途停止\n4. 使用中文回答用户问题\n5. 确保工具调用参数完整，格式正确\n6. 生成响应时要完整，不要只输出部分内容\n\n请始终提供完整的响应，确保用户能够获得满意的答案。'
        }
        
        # 尝试从配置文件加载
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._config.update(config_data)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
    
    def get_system_message(self, mode='normal', context_docs=None, web_search_results=None):
        """获取系统消息
        
        Args:
            mode: 模式，可选值：'normal', 'rag', 'agent'
            context_docs: RAG上下文文档列表（仅在rag模式下使用）
            web_search_results: 网络搜索结果
            
        Returns:
            dict: 系统消息对象，格式为 {'role': 'system', 'content': '...'}
        """
        if mode == 'rag':
            # 从配置文件或默认模板获取RAG系统消息
            rag_system_msg = self._config.get('rag_system_message', self._default_templates['rag'])
            
            # 如果有上下文文档，添加到系统消息中
            if context_docs:
                # 构建RAG上下文
                context_str = ""
                for i, doc in enumerate(context_docs):
                    if isinstance(doc, dict):
                        doc_content = doc.get('content', '') or doc.get('page_content', '')
                    else:
                        doc_content = getattr(doc, 'page_content', '') or getattr(doc, 'content', '')
                    context_str += f"参考文档{i+1}：{doc_content}\n\n"
                
                # 构建带上下文的RAG系统消息
                content = f"{rag_system_msg}\n\n{context_str}"
            else:
                # 构建不带上下文的RAG系统消息
                content = rag_system_msg
        elif mode == 'agent':
            # 从配置文件或默认模板获取智能体系统消息
            content = self._config.get('agent_system_message', self._default_templates['agent'])
        else:
            content = self._config.get('system_message', self._default_templates['chat'])
        
        # 添加网络搜索结果
        if web_search_results:
            search_str = "\n\n网络搜索结果：\n"
            try:
                # 处理不同格式的搜索结果
                if isinstance(web_search_results, dict):
                    if 'results' in web_search_results:
                        for i, result in enumerate(web_search_results['results']):
                            if isinstance(result, dict):
                                title = result.get('title', '未命名')
                                snippet = result.get('snippet', '')
                                url = result.get('url', '')
                                search_str += f"{i+1}. {title}\n{snippet}\n{url}\n\n"
                    else:
                        search_str += str(web_search_results)
                elif isinstance(web_search_results, list):
                    for i, result in enumerate(web_search_results):
                        search_str += f"{i+1}. {str(result)}\n\n"
                else:
                    search_str += str(web_search_results)
                content += search_str
            except Exception:
                pass
        
        return {
            'role': 'system',
            'content': content
        }
    
    def build_human_message(self, query, context_docs=None, chat_history=None, prompt_template=None):
        """构建人类消息（只包含原始查询）
        
        Args:
            query: 用户查询
            context_docs: 检索到的上下文文档列表
            chat_history: 聊天历史记录
            prompt_template: 自定义提示模板
            
        Returns:
            dict: 人类消息对象，格式为 {'role': 'user', 'content': '...'}
        """
        # 直接返回原始查询，不包含提示词模板
        return {
            'role': 'user',
            'content': query
        }
    
    def build_messages(self, query, context_docs=None, chat_history=None, mode='normal', prompt_template=None, web_search_results=None):
        """构建完整的消息列表
        
        Args:
            query: 用户查询
            context_docs: 检索到的上下文文档列表
            chat_history: 聊天历史记录
            mode: 模式，可选值：'normal', 'rag', 'agent'
            prompt_template: 自定义提示模板
            web_search_results: 网络搜索结果
            
        Returns:
            List[dict]: 消息列表，包含SystemMessage和HumanMessage
        """
        messages = []
        
        # 添加系统消息
        system_message = self.get_system_message(mode=mode, context_docs=context_docs if mode == 'rag' else None, web_search_results=web_search_results)
        messages.append(system_message)
        
        # 添加聊天历史（如果有）
        if chat_history:
            messages.extend(chat_history)
        
        # 添加人类消息（只包含原始查询）
        human_message = self.build_human_message(
            query=query,
            context_docs=context_docs if mode != 'rag' else None,  # RAG模式下上下文已在SystemMessage中
            chat_history=None,  # 聊天历史已单独添加
            prompt_template=prompt_template
        )
        messages.append(human_message)
        
        return messages


# 全局提示词管理器实例
prompt_manager = PromptManager()
