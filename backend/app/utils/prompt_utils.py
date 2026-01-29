"""提示词构建工具类"""
from typing import List, Dict, Optional, Any
from app.services.base_service import BaseService


class PromptUtils:
    """提示词构建工具类，用于构建各种类型的提示词"""
    
    @staticmethod
    def build_prompt(query: str, context_docs: List[Any] = None, chat_history: List[Dict[str, str]] = None, prompt_template: str = None) -> str:
        """构建提示模板，将查询、聊天历史和检索到的上下文结合
        
        Args:
            query: 用户查询
            context_docs: 检索到的上下文文档列表
            chat_history: 聊天历史记录
            prompt_template: 自定义提示模板，默认为None
            
        Returns:
            str: 构建好的提示
        """
        if not context_docs:
            # 如果没有上下文，考虑聊天历史
            if chat_history:
                chat_history_str = "\n".join([f"{'用户' if msg['role'] == 'user' else '助手'}: {msg['content']}" for msg in chat_history])
                default_template = """你是一个AI助手，使用以下聊天历史来回答用户问题。如果你不知道答案，就说你不知道。保持回答简洁明了。\n\n{chat_history}\n\n用户问题：{query}"""
                return default_template.format(chat_history=chat_history_str, query=query)
            return query
        
        # 使用自定义提示模板或默认模板
        if prompt_template:
            context = "\n".join([f"参考文档{i+1}：{doc['content'][:200] if isinstance(doc, dict) else doc.page_content[:200]}..." for i, doc in enumerate(context_docs)])
            if chat_history:
                chat_history_str = "\n".join([f"{'用户' if msg['role'] == 'user' else '助手'}: {msg['content']}" for msg in chat_history])
                return prompt_template.format(context=context, chat_history=chat_history_str, query=query)
            return prompt_template.format(context=context, query=query)
        
        # 默认提示模板
        default_template = """你是一个AI助手，使用以下上下文和聊天历史来回答用户问题。如果你不知道答案，就说你不知道。保持回答简洁明了。\n\n{context}\n\n{chat_history}\n\n用户问题：{query}"""
        
        # 构建上下文，支持dict和object类型
        context = "\n".join([doc['content'] if isinstance(doc, dict) else doc.page_content for doc in context_docs])
        
        # 构建聊天历史
        chat_history_str = ""
        if chat_history:
            chat_history_str = "\n".join([f"{'用户' if msg['role'] == 'user' else '助手'}: {msg['content']}" for msg in chat_history])
        
        return default_template.format(context=context, chat_history=chat_history_str, query=query)
    
    @staticmethod
    def build_agent_prompt(system_prompt: Optional[str] = None) -> str:
        """构建智能体提示词
        
        Args:
            system_prompt: 自定义系统提示词，默认为None
            
        Returns:
            str: 构建好的系统提示词
        """
        # 默认系统提示词
        default_system_prompt = """你是一个有用的助手，可以调用工具来帮助用户解决问题。
        当你需要使用工具时，请调用适当的工具。"""
        
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
            BaseService.log_error(f"创建智能体提示词模板失败: {str(e)}")
            return None
    
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
        return PromptUtils.build_prompt(query, context_docs, chat_history, prompt_template)
