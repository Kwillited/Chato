"""提示词构建工具类"""
from typing import List, Dict, Optional, Any


class PromptUtils:
    """提示词构建工具类，用于构建各种类型的提示词"""
    
    @staticmethod
    def build_chat_prompt(query: str, chat_history: List[Dict[str, str]] = None, prompt_template: str = None) -> str:
        """构建普通对话提示词
        
        Args:
            query: 用户查询
            chat_history: 聊天历史记录
            prompt_template: 自定义提示模板，默认为None
            
        Returns:
            str: 构建好的提示
        """
        # 构建聊天历史
        chat_history_str = ""
        if chat_history:
            chat_history_str = "\n".join([f"{'用户' if msg['role'] == 'user' else '助手'}: {msg['content']}" for msg in chat_history])
        
        # 使用自定义提示模板或默认模板
        if prompt_template:
            return prompt_template.format(chat_history=chat_history_str, query=query)
        
        # 默认提示模板
        default_template = """你是一个AI助手，使用以下聊天历史来回答用户问题。如果你不知道答案，就说你不知道。保持回答简洁明了。\n\n{chat_history}\n\n用户问题：{query}"""
        return default_template.format(chat_history=chat_history_str, query=query)
    
    @staticmethod
    def build_rag_prompt(query: str, context_docs: List[Any], chat_history: Optional[List[Dict[str, str]]] = None, prompt_template: Optional[str] = None) -> str:
        """构建RAG提示词
        
        Args:
            query: 用户查询
            context_docs: 检索到的上下文文档列表
            chat_history: 聊天历史记录
            prompt_template: 自定义提示模板
            
        Returns:
            str: 构建好的RAG提示词
        """
        # 构建上下文，支持dict和object类型
        context = "\n".join([f"参考文档{i+1}：{doc['content'] if isinstance(doc, dict) else doc.page_content}" for i, doc in enumerate(context_docs)])
        
        # 构建聊天历史
        chat_history_str = ""
        if chat_history:
            chat_history_str = "\n".join([f"{'用户' if msg['role'] == 'user' else '助手'}: {msg['content']}" for msg in chat_history])
        
        # 使用自定义提示模板或默认模板
        if prompt_template:
            return prompt_template.format(context=context, chat_history=chat_history_str, query=query)
        
        # 默认RAG提示模板
        default_template = """你是一个AI助手，使用以下上下文信息来回答用户问题。请严格基于提供的上下文信息进行回答，不要添加任何外部信息。如果你不知道答案，就说你不知道。保持回答简洁明了。\n\n{context}\n\n{chat_history}\n\n用户问题：{query}"""
        return default_template.format(context=context, chat_history=chat_history_str, query=query)
    
    @staticmethod
    def build_agent_prompt(system_prompt: Optional[str] = None) -> str:
        """构建智能体提示词
        
        Args:
            system_prompt: 自定义系统提示词，默认为None
            
        Returns:
            str: 构建好的系统提示词
        """
        # 增强的系统提示词
        default_system_prompt = """你是一个强大的AI助手，能够使用工具来完成各种任务。请按照以下要求工作：

1. 分析用户需求，制定详细的执行计划
2. 如果需要，使用适当的工具来获取信息或执行操作
3. 提供完整、详细的响应，不要中途停止
4. 使用中文回答用户问题
5. 对于天气查询，请使用天气工具获取实时信息
6. 对于文件操作，请使用文件系统工具
7. 确保工具调用参数完整，格式正确
8. 生成响应时要完整，不要只输出部分内容
9. 不要在响应中使用"为了"这样的不完整开头

请始终提供完整的响应，确保用户能够获得满意的答案。"""
        
        return system_prompt or default_system_prompt
    
    @staticmethod
    def get_agent_prompt_template(system_prompt: Optional[str] = None) -> Optional[Any]:
        """获取智能体提示词模板
        
        Args:
            system_prompt: 自定义系统提示词，默认为None
            
        Returns:
            ChatPromptTemplate: 智能体提示词模板
        """
        try:
            from langchain_core.prompts import ChatPromptTemplate
            
            # 构建系统提示词
            final_system_prompt = PromptUtils.build_agent_prompt(system_prompt)
            
            # 创建提示词模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", final_system_prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            
            return prompt
        except Exception as e:
            # 简化错误处理，避免循环导入
            print(f"创建智能体提示词模板失败: {str(e)}")
            return None
    
    @staticmethod
    def build_prompt(query: str, context_docs: List[Any] = None, chat_history: List[Dict[str, str]] = None, prompt_template: str = None) -> str:
        """构建通用提示词（兼容旧方法）
        
        Args:
            query: 用户查询
            context_docs: 检索到的上下文文档列表
            chat_history: 聊天历史记录
            prompt_template: 自定义提示模板，默认为None
            
        Returns:
            str: 构建好的提示
        """
        if context_docs:
            return PromptUtils.build_rag_prompt(query, context_docs, chat_history, prompt_template)
        else:
            return PromptUtils.build_chat_prompt(query, chat_history, prompt_template)
