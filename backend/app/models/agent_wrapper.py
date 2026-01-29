# agent_wrapper.py
from typing import Dict, Any, List, Optional, Union, Callable, AsyncIterator
from functools import wraps
from app.models.base_model import BaseModel
from app.utils.message_utils import MessageUtils
from app.utils.stream_utils import StreamUtils
from langchain_core.prompts import ChatPromptTemplate

# 导入兼容性处理
try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    try:
        from langchain_core.agents import AgentExecutor
        from langchain.agents import create_tool_calling_agent
    except ImportError:
        try:
            from langchain.agents import create_agent
            from langchain_core.agents import AgentExecutor
            create_tool_calling_agent = create_agent
        except ImportError:
            from langchain.agents import create_agent
            create_tool_calling_agent = create_agent
            AgentExecutor = None

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
except ImportError:
    MultiServerMCPClient = None


class AgentWrapper:
    """智能体包装器，动态包装任意BaseModel实例"""
    
    def __init__(self, base_model: BaseModel):
        """初始化包装器
        
        Args:
            base_model: 要包装的基础模型实例
        """
        if not hasattr(base_model, 'llm'):
            raise ValueError("base_model 必须有 'llm' 属性")
        
        self.base_model = base_model
        self.llm = base_model.llm
        self.agent_executor = None
        self.mcp_client = None
        self.is_initialized = False
        print(f"✅ AgentWrapper 初始化完成，base_model: {type(base_model).__name__}")
    
    async def initialize(self, 
                        mcp_config: Optional[Dict] = None,
                        system_prompt: Optional[str] = None,
                        verbose: bool = False) -> None:
        """初始化智能体"""
        print("🔧 AgentWrapper.initialize() 被调用")
        
        from app.core.logging_config import logger
        
        logger.info("开始初始化智能体...")
        
        if self.is_initialized:
            logger.info("智能体已经初始化，跳过初始化过程")
            return
        
        # 检查 MultiServerMCPClient 是否导入成功
        if MultiServerMCPClient is None:
            logger.error("MultiServerMCPClient 导入失败，智能体功能不可用")
            return
            
        # 默认MCP配置
        if mcp_config is None:
            mcp_config = {
                "filesystem": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem"],
                }
            }
        
        logger.info(f"MCP 配置: {mcp_config}")
        
        try:
            # 初始化MCP客户端
            logger.info("正在初始化 MCP 客户端...")
            self.mcp_client = MultiServerMCPClient(mcp_config)
            logger.info("MCP 客户端初始化成功")
            
            # 获取工具
            logger.info("正在获取 MCP 工具...")
            tools = await self.mcp_client.get_tools()
            logger.info(f"成功获取 {len(tools)} 个 MCP 工具")
            
            # 记录工具详情
            for i, tool in enumerate(tools):
                try:
                    tool_name = getattr(tool, 'name', str(tool))
                    logger.info(f"工具 {i+1}: {tool_name}")
                except Exception:
                    logger.info(f"工具 {i+1}: {str(tool)}")
            
            # 使用 PromptUtils 构建系统提示词
            from app.utils.prompt_utils import PromptUtils
            
            # 构建系统提示词
            final_system_prompt = PromptUtils.build_agent_prompt(system_prompt)
            
            logger.info("正在创建智能体...")
            
            # 尝试使用新的 create_agent API
            try:
                from langchain.agents import create_agent
                
                logger.info("使用新的 create_agent API 创建智能体...")
                
                # 使用新的 create_agent API
                self.agent_executor = create_agent(
                    model=self.llm,
                    tools=tools,
                    system_prompt=final_system_prompt,
                    debug=verbose
                )
                
                logger.info("使用 create_agent API 创建智能体成功")
                self.is_initialized = True
                logger.info("智能体初始化完成，状态: 成功")
            except Exception as e:
                logger.error(f"使用 create_agent API 初始化智能体失败: {str(e)}")
                
                # 尝试使用旧的方式
                try:
                    from langchain.agents import create_tool_calling_agent
                    from langchain.agents import AgentExecutor
                    
                    logger.info("尝试使用旧的 create_tool_calling_agent API...")
                    
                    # 使用 PromptUtils 创建提示词模板
                    prompt = PromptUtils.get_agent_prompt_template(system_prompt)
                    
                    # 如果创建失败，使用默认模板
                    if not prompt:
                        logger.warning("创建智能体提示词模板失败，使用默认模板")
                        from langchain_core.prompts import ChatPromptTemplate
                        prompt = ChatPromptTemplate.from_messages([
                            ("system", final_system_prompt),
                            ("placeholder", "{chat_history}"),
                            ("human", "{input}"),
                            ("placeholder", "{agent_scratchpad}"),
                        ])
                    
                    # 创建智能体
                    agent = create_tool_calling_agent(
                        llm=self.llm,
                        tools=tools,
                        prompt=prompt
                    )
                    
                    self.agent_executor = AgentExecutor(
                        agent=agent,
                        tools=tools,
                        verbose=verbose,
                        handle_parsing_errors=True,
                        max_iterations=5
                    )
                    
                    logger.info("使用旧 API 创建智能体成功")
                    self.is_initialized = True
                    logger.info("智能体初始化完成，状态: 成功")
                except Exception as e2:
                    logger.error(f"使用旧 API 初始化智能体失败: {str(e2)}")
                    logger.error("智能体初始化完成，状态: 失败")
        except Exception as e:
            logger.error(f"初始化智能体失败: {str(e)}")
            logger.error("智能体初始化完成，状态: 失败")
    
    async def chat(self, 
                   messages: List[Dict[str, str]], 
                   temperature: float,
                   stream: bool = False,
                   use_agent: bool = True) -> Any:
        """统一的聊天接口"""
        print(f"🤖 AgentWrapper.chat() 被调用，use_agent={use_agent}")
        
        from app.core.logging_config import logger
        
        logger.info(f"开始聊天，use_agent={use_agent}, is_initialized={self.is_initialized}")
        
        if not use_agent:
            logger.info("未启用智能体，使用原始模型")
            return self.base_model.chat(messages, temperature, stream)
        
        if not self.is_initialized:
            logger.warning("智能体未初始化，使用原始模型")
            return self.base_model.chat(messages, temperature, stream)
        
        logger.info("使用智能体模式聊天")
        
        try:
            # 使用智能体模式
            latest_input, chat_history = MessageUtils.extract_latest_input(messages)
            logger.info(f"处理消息: 输入='{latest_input[:50]}{'...' if len(latest_input) > 50 else ''}'")
            
            # 尝试调用智能体
            try:
                result = await self.agent_executor.ainvoke({
                    "input": latest_input,
                    "chat_history": chat_history
                })
                
                logger.info("智能体调用成功")
                
                # 保持与原始模型一致的返回格式
                if isinstance(result, dict):
                    if "output" in result:
                        return {"content": result["output"], "content_struct": None}
                    elif "content" in result:
                        return {"content": result["content"], "content_struct": None}
                    elif "answer" in result:
                        return {"content": result["answer"], "content_struct": None}
                
                return {"content": str(result), "content_struct": None}
                    
            except Exception as e:
                logger.error(f"调用智能体失败: {str(e)}")
                logger.warning("回退到原始模型")
                return self.base_model.chat(messages, temperature, stream)
                
        except Exception as e:
            logger.error(f"智能体聊天失败: {str(e)}")
            logger.warning("回退到原始模型")
            return self.base_model.chat(messages, temperature, stream)
    
    async def chat_stream(self, 
                         messages: List[Dict[str, str]], 
                         temperature: float,
                         use_agent: bool = True) -> AsyncIterator[str]:
        """流式聊天接口"""
        print(f"🌊 AgentWrapper.chat_stream() 被调用，use_agent={use_agent}")
        
        from app.core.logging_config import logger
        
        logger.info(f"开始流式聊天，use_agent={use_agent}, is_initialized={self.is_initialized}")
        
        if not use_agent:
            logger.info("未启用智能体，使用原始模型流式方法")
            async for chunk in self.base_model.chat_stream(messages, temperature):
                yield chunk
            return
        
        if not self.is_initialized:
            logger.warning("智能体未初始化，使用原始模型流式方法")
            async for chunk in self.base_model.chat_stream(messages, temperature):
                yield chunk
            return
        
        logger.info("使用智能体模式流式聊天")
        
        try:
            # 提取最新输入和聊天历史
            latest_input, chat_history = MessageUtils.extract_latest_input(messages)
            
            # 尝试使用智能体原生流式方法
            try:
                # 检查是否有 astream 方法
                if hasattr(self.agent_executor, 'astream'):
                    logger.info("使用智能体原生流式方法 astream")
                    
                    # 累积的内容
                    accumulated_content = ""
                    
                    async for chunk in self.agent_executor.astream({
                        "input": latest_input,
                        "chat_history": chat_history
                    }):
                        # 处理流式输出
                        if isinstance(chunk, dict):
                            # 提取内容
                            if "output" in chunk:
                                content = chunk["output"]
                                if content and content != accumulated_content:
                                    # 计算新内容
                                    new_content = content[len(accumulated_content):]
                                    if new_content:
                                        logger.info(f"智能体回复: {new_content}")
                                        yield StreamUtils.format_stream_chunk(new_content)
                                        accumulated_content = content
                            elif "content" in chunk:
                                content = chunk["content"]
                                if content and content != accumulated_content:
                                    # 计算新内容
                                    new_content = content[len(accumulated_content):]
                                    if new_content:
                                        logger.info(f"智能体回复: {new_content}")
                                        yield StreamUtils.format_stream_chunk(new_content)
                                        accumulated_content = content
                            else:
                                # 打印其他类型的 chunk 以便调试
                                logger.debug(f"智能体返回其他类型: {chunk}")
                        else:
                            # 打印非字典类型的 chunk 以便调试
                            logger.debug(f"智能体返回非字典类型: {chunk}")
                    
                    # 发送完成信号
                    yield StreamUtils.format_stream_done()
                    logger.info("智能体原生流式返回完成")
                    return
                else:
                    logger.info("智能体执行器不支持 astream 方法")
            except Exception as e:
                logger.error(f"使用智能体原生流式方法失败: {str(e)}")
            
            # 回退到模拟流式方法
            logger.info("回退到模拟流式方法")
            result = await self.chat(messages, temperature, stream=False, use_agent=True)
            
            # 提取内容
            content = ""
            if isinstance(result, dict):
                content = result.get('content', '') or result.get('output', '') or result.get('answer', '')
            elif isinstance(result, str):
                content = result
            else:
                content = str(result)
            
            logger.info(f"智能体响应长度: {len(content)}")
            
            # 使用模拟流式（分块返回）
            logger.info(f"智能体回复: {content}")
            async for chunk in StreamUtils.simulate_stream(content, chunk_size=3, delay=0.03):
                yield chunk
            
            logger.info("模拟流式返回完成")
            
        except Exception as e:
            logger.error(f"智能体流式聊天失败: {str(e)}")
            
            # 出错时回退到原始模型
            async for chunk in self.base_model.chat_stream(messages, temperature):
                yield chunk
    
    def __getattr__(self, name):
        """转发其他方法到原始模型"""
        return getattr(self.base_model, name)