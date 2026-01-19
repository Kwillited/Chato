"""LangChain RAG服务 - 使用LangChain的高级RAG功能"""
import os
from typing import Dict, Any, List
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.services.vector.vector_store_service import VectorStoreService
from app.core.config import config_manager
from app.services.base_service import BaseService


class LangChainRAGService(BaseService):
    """基于LangChain的RAG服务类 - 提供高级RAG功能"""
    
    _instance = None
    
    def __init__(self):
        """初始化LangChain RAG服务"""
        self.vector_service = VectorStoreService.get_instance()
        self.llm = None  # 懒加载LLM
        self.rag_chain = None  # 懒加载RAG链
        self.config = config_manager.get('rag', {})
        self.log_info("✅ LangChain RAG服务已初始化")
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _init_rag_chain(self, llm=None):
        """初始化RAG链"""
        if self.rag_chain and not llm:
            return self.rag_chain
        
        if llm:
            self.llm = llm
        
        if not self.llm:
            # 如果没有提供LLM，使用默认配置
            from app.models.model_manager import ModelManager
            self.llm = ModelManager.get_default_llm()
        
        # 创建检索器
        retriever = self.vector_service.vector_store.as_retriever(
            search_type=self.config.get('search_type', 'similarity'),
            search_kwargs={
                'k': self.config.get('top_k', 3),
                'score_threshold': self.config.get('score_threshold', 0.7)
            }
        )
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个AI助手，使用以下上下文来回答用户问题。如果你不知道答案，就说你不知道。保持回答简洁明了。\n\n{context}"),
            ("human", "{input}")
        ])
        
        # 创建文档处理链
        combine_docs_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=prompt
        )
        
        # 创建检索链
        self.rag_chain = create_retrieval_chain(
            retriever=retriever,
            combine_docs_chain=combine_docs_chain
        )
        
        return self.rag_chain
    
    def get_enhanced_prompt(self, question: str, rag_config: Dict[str, Any] = None) -> str:
        """使用LangChain RAG链获取增强提示"""
        if not rag_config or not rag_config.get('enabled', False):
            return question
        
        try:
            # 更新配置
            if rag_config:
                self.config.update(rag_config)
            
            # 获取向量存储
            if not self.vector_service.vector_store:
                self.log_error("向量存储未初始化")
                return question
            
            # 执行相似性搜索
            k = self.config.get('top_k', 3)
            score_threshold = self.config.get('score_threshold', 0.7)
            
            results = self.vector_service.search_documents(
                query=question,
                k=k,
                score_threshold=score_threshold
            )
            
            if results:
                # 使用生成服务的build_prompt方法构建提示，避免重复实现
                from app.services.rag.generation_service import GenerationService
                generation_service = GenerationService()
                return generation_service.build_prompt(question, results)
            
            return question
        except Exception as e:
            self.log_error(f"RAG增强提示生成失败: {str(e)}")
            return question
    
    def generate_response(self, question: str, rag_config: Dict[str, Any] = None, llm=None) -> Dict[str, Any]:
        """使用LangChain RAG链生成完整响应"""
        from app.utils.callback_manager import trigger_callback
        
        if not rag_config or not rag_config.get('enabled', False):
            if llm:
                return {
                    'answer': llm.invoke(question).content,
                    'sources': []
                }
            return {
                'answer': "",
                'sources': []
            }
        
        try:
            # 更新配置
            if rag_config:
                self.config.update(rag_config)
            
            self.log_info(f"🚀 开始RAG对话流程: 查询='{question[:50]}{'...' if len(question) > 50 else ''}'")
            
            # 触发RAG链开始回调
            trigger_callback('rag_chain_start', 
                           question=question[:50] + "..." if len(question) > 50 else question)
            
            # 初始化RAG链
            rag_chain = self._init_rag_chain(llm)
            self.log_info("📋 RAG链初始化完成")
            
            # 执行RAG链
            self.log_info("🔍 正在搜索相关文档...")
            result = rag_chain.invoke({
                "input": question
            })
            
            # 提取来源
            sources = []
            if 'context' in result:
                context_count = len(result['context'])
                self.log_info(f"✅ 找到 {context_count} 个相关文档片段")
                for i, doc in enumerate(result['context']):
                    sources.append({
                        'id': i+1,
                        'content': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        'metadata': doc.metadata
                    })
            
            self.log_info(f"📝 生成RAG响应完成: 答案长度={len(result['answer'])} 字符, 参考文档数={len(sources)}")
            
            # 触发RAG链结束回调
            trigger_callback('rag_chain_end', 
                           question=question[:50] + "..." if len(question) > 50 else question,
                           answer=result['answer'][:100] + "..." if len(result['answer']) > 100 else result['answer'],
                           sources_count=len(sources))
            
            return {
                'answer': result['answer'],
                'sources': sources
            }
        except Exception as e:
            self.log_error(f"RAG响应生成失败: {str(e)}")
            
            # 触发错误回调
            trigger_callback('error', 
                           event='rag_chain',
                           error=str(e))
            
            return {
                'answer': f"生成响应失败: {str(e)}",
                'sources': []
            }
    
    def get_retriever(self, rag_config: Dict[str, Any] = None) -> Any:
        """获取配置好的检索器"""
        if rag_config:
            self.config.update(rag_config)
        
        return self.vector_service.vector_store.as_retriever(
            search_type=self.config.get('search_type', 'similarity'),
            search_kwargs={
                'k': self.config.get('top_k', 3),
                'score_threshold': self.config.get('score_threshold', 0.7)
            }
        )
    
    def add_documents_with_langchain(self, file_paths: List[str]) -> Dict[str, Any]:
        """使用LangChain的DirectoryLoader和LoaderChain添加文档"""
        from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, Docx2txtLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        try:
            # 创建加载器映射
            loader_mapping = {
                '.txt': TextLoader,
                '.pdf': PyPDFLoader,
                '.doc': Docx2txtLoader,
                '.docx': Docx2txtLoader
            }
            
            all_documents = []
            
            # 加载所有文件
            for file_path in file_paths:
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in loader_mapping:
                    loader = loader_mapping[file_ext](file_path)
                    documents = loader.load()
                    all_documents.extend(documents)
            
            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.get('chunk_size', 1000),
                chunk_overlap=self.config.get('chunk_overlap', 200)
            )
            
            split_documents = text_splitter.split_documents(all_documents)
            
            # 添加到向量存储
            success = self.vector_service.add_documents(split_documents)
            
            return {
                'success': success,
                'total_documents': len(all_documents),
                'split_documents_count': len(split_documents),
                'message': f"成功处理 {len(all_documents)} 个文档，生成 {len(split_documents)} 个文本块"
            }
        except Exception as e:
            self.log_error(f"使用LangChain添加文档失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
