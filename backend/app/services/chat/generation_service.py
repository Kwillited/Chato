"""生成服务 - 负责基于检索到的上下文生成响应"""
from app.core.config import config_manager
from app.services.base_service import BaseService
from app.utils.prompt_manager import prompt_manager

class GenerationService(BaseService):
    """生成服务类 - 封装所有与LLM推理相关的操作"""
    
    def __init__(self):
        """初始化生成服务"""
        pass
    
    def build_prompt(self, query, context_docs, chat_history=None, prompt_template=None):
        """构建提示模板，将查询、聊天历史和检索到的上下文结合
        
        Args:
            query: 用户查询
            context_docs: 检索到的上下文文档列表
            chat_history: 聊天历史记录
            prompt_template: 自定义提示模板，默认为None
            
        Returns:
            str: 构建好的提示
        """
        # 使用prompt_manager构建人类消息，然后提取内容作为提示
        human_message = prompt_manager.build_human_message(
            query=query,
            context_docs=context_docs,
            chat_history=chat_history,
            prompt_template=prompt_template
        )
        return human_message['content']
    
    def generate_response(self, prompt, llm=None):
        """调用LLM生成响应
        
        Args:
            prompt: 构建好的提示
            llm: LLM实例，用于依赖注入
            
        Returns:
            dict: 生成的响应信息
        """
        try:
            # 如果没有提供LLM，使用默认配置
            if not llm:
                from app.llm.managers.model_manager import ModelManager
                llm = ModelManager.get_default_llm()
            
            # 调用LLM生成响应
            response = llm.invoke(prompt)
            
            # 提取响应内容
            answer = None
            if hasattr(response, 'content'):
                answer = response.content
            elif isinstance(response, dict) and 'content' in response:
                answer = response['content']
            else:
                answer = str(response)
            
            return {
                'answer': answer,
                'success': True
            }
        except Exception as e:
            self.log_error(f"生成响应失败: {str(e)}")
            return {
                'answer': f"生成响应失败: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def generate_rag_response(self, query, context_docs, chat_history=None, llm=None, prompt_template=None):
        """执行完整的RAG生成流程：构建提示 + 生成响应
        
        Args:
            query: 用户查询
            context_docs: 检索到的上下文文档列表
            chat_history: 聊天历史记录
            llm: LLM实例，用于依赖注入
            prompt_template: 自定义提示模板
            
        Returns:
            dict: RAG生成结果
        """
        try:
            # 构建提示
            prompt = self.build_prompt(query, context_docs, chat_history, prompt_template)
            
            # 生成响应
            response = self.generate_response(prompt, llm)
            
            # 整合结果
            result = {
                'query': query,
                'answer': response['answer'],
                'success': response['success'],
                'context_docs': context_docs,
                'context_count': len(context_docs)
            }
            
            if not response['success'] and 'error' in response:
                result['error'] = response['error']
            
            return result
        except Exception as e:
            self.log_error(f"RAG响应生成失败: {str(e)}")
            return {
                'query': query,
                'answer': f"RAG响应生成失败: {str(e)}",
                'success': False,
                'context_docs': context_docs,
                'context_count': len(context_docs),
                'error': str(e)
            }
    
    def build_agent_prompt(self, system_prompt=None):
        """构建智能体提示词
        
        Args:
            system_prompt: 自定义系统提示词，默认为None
            
        Returns:
            str: 构建好的系统提示词
        """
        if system_prompt:
            return system_prompt
        # 使用prompt_manager获取智能体系统消息
        agent_message = prompt_manager.get_system_message(mode='agent')
        return agent_message['content']
    
    def get_agent_prompt_template(self, system_prompt=None):
        """获取智能体提示词模板
        
        Args:
            system_prompt: 自定义系统提示词，默认为None
            
        Returns:
            ChatPromptTemplate: 智能体提示词模板
        """
        try:
            from langchain_core.prompts import ChatPromptTemplate
            
            # 构建系统提示词
            final_system_prompt = self.build_agent_prompt(system_prompt)
            
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
