# agent_wrapper.py
from typing import Dict, Any, List, Optional, Union, Callable, AsyncIterator
from functools import wraps
from app.models.base_model import BaseModel
from app.utils.message_utils import MessageUtils
from app.utils.stream_utils import StreamUtils
from app.utils.mcp.mcp_adapter import mcp_adapter
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
from langgraph.runtime import get_runtime
from langgraph.prebuilt import ToolNode

# 导入智能体创建API
from app.core.logging_config import logger


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
        self.agent_executor: Optional[Any] = None
        self.is_initialized = False
        print(f"✅ AgentWrapper 初始化完成，base_model: {type(self.base_model).__name__}")
    
    async def initialize(self, 
                        mcp_config: Optional[Dict] = None,
                        system_prompt: Optional[str] = None,
                        verbose: bool = True, 
                        force_reinit: bool = False) -> None:
        """初始化智能体"""
        print("🔧 AgentWrapper.initialize() 被调用")
        
        from app.core.logging_config import logger
        
        logger.info("=== 开始初始化智能体 ===")
        logger.info(f"基础模型: {type(self.base_model).__name__}")
        logger.info(f"LLM 类型: {type(self.llm).__name__}")
        logger.info(f"是否已初始化: {self.is_initialized}, 强制重新初始化: {force_reinit}")
        
        if self.is_initialized and not force_reinit:
            logger.info("智能体已经初始化，跳过初始化过程")
            return
        
        # 初始化 MCP 适配器
        logger.info("正在初始化 MCP 适配器...")
        mcp_initialized = await mcp_adapter.initialize(mcp_config)
        
        if not mcp_initialized:
            logger.error("MCP 适配器初始化失败，智能体功能不可用")
            return
            
        # 使用 PromptUtils 构建系统提示词
        from app.utils.prompt_utils import PromptUtils
        
        # 构建系统提示词
        final_system_prompt = PromptUtils.build_agent_prompt(system_prompt)
        
        # 添加工具使用指导
        tool_usage_guide = mcp_adapter.get_tool_usage_guide()
        final_system_prompt += tool_usage_guide
        
        # 记录实际工具名称
        tool_info = mcp_adapter.get_tool_info()
        logger.info(f"检测到的工具：天气工具={tool_info['weather_tool']}, 文件系统工具={tool_info['filesystem_tool']}")
        
        logger.info(f"系统提示词长度: {len(final_system_prompt)} 字符")
        
        logger.info("正在创建智能体...")
        logger.info(f"创建参数: model={type(self.llm).__name__}, tools_count={len(mcp_adapter.get_tools())}, verbose={verbose}")
        
        # 使用 LangGraph 创建智能体
        try:
            from langgraph.graph import END
            
            # 定义状态结构
            class AgentState(Dict):
                input: str
                chat_history: List[Dict[str, str]]
                output: Optional[str] = None
                tool_calls: Optional[List[Dict]] = None
                tool_results: Optional[List[Dict]] = None
            
            # 获取工具
            tools = mcp_adapter.get_tools()
            
            # 创建工具节点
            tool_node = ToolNode(tools)
            
            # 创建思考节点
            async def think_node(state: AgentState):
                """思考节点：分析输入并决定是否使用工具"""
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
                
                # 构建消息
                messages = [SystemMessage(content=final_system_prompt)]
                
                # 添加聊天历史
                for msg in state.get('chat_history', []):
                    if msg['role'] == 'user':
                        messages.append(HumanMessage(content=msg['content']))
                    elif msg['role'] == 'assistant':
                        messages.append(AIMessage(content=msg['content']))
                
                # 添加当前输入
                messages.append(HumanMessage(content=state['input']))
                
                # 调用 LLM
                response = await self.llm.ainvoke(messages)
                
                # 检查是否有工具调用
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    return {
                        'tool_calls': response.tool_calls,
                        'output': None
                    }
                else:
                    return {
                        'output': response.content,
                        'tool_calls': None
                    }
            
            # 创建响应节点
            def respond_node(state: AgentState):
                """响应节点：生成最终回复"""
                return {
                    'output': state.get('output', 'I apologize, but I was unable to generate a response.'),
                    'tool_calls': None
                }
            
            # 创建路由函数
            def should_use_tool(state: AgentState):
                """决定是否使用工具"""
                return 'tools' if state.get('tool_calls') else 'respond'
            
            # 创建状态图
            workflow = StateGraph(AgentState)
            
            # 添加节点
            workflow.add_node('think', think_node)
            workflow.add_node('tools', tool_node)
            workflow.add_node('respond', respond_node)
            
            # 添加边
            workflow.set_entry_point('think')
            workflow.add_conditional_edges(
                'think',
                should_use_tool,
                {
                    'tools': 'tools',
                    'respond': 'respond'
                }
            )
            workflow.add_edge('tools', 'think')
            workflow.add_edge('respond', END)
            
            # 编译图
            self.agent_executor = workflow.compile()
            self.is_initialized = True
            
            logger.info("使用 LangGraph 创建智能体成功")
            logger.info("智能体初始化完成，状态: 成功")
            logger.info("=== 智能体初始化完成 ===")
            
        except Exception as e:
            logger.error(f"使用 LangGraph 初始化智能体失败: {str(e)}")
            logger.error("智能体初始化完成，状态: 失败")
            logger.info("=== 智能体初始化完成 ===")
    
    async def chat(self, 
                   messages: List[Dict[str, str]], 
                   temperature: float,
                   stream: bool = False,
                   use_agent: bool = True) -> Any:
        """统一的聊天接口"""
        print(f"🤖 AgentWrapper.chat() 被调用，use_agent={use_agent}")
        
        from app.core.logging_config import logger
        
        logger.info("=== 开始聊天处理 ===")
        logger.info(f"配置参数: use_agent={use_agent}, is_initialized={self.is_initialized}, stream={stream}, temperature={temperature}")
        
        # 记录消息详情
        logger.info(f"消息数量: {len(messages)}")
        for i, msg in enumerate(messages):
            msg_role = msg.get('role', 'unknown')
            msg_content = msg.get('content', '')
            logger.info(f"消息 {i+1}: 角色={msg_role}, 内容长度={len(msg_content)} 字符")
            if len(msg_content) < 200:
                logger.debug(f"  内容: {msg_content}")
            else:
                logger.debug(f"  内容: {msg_content[:200]}...")
        
        if not use_agent:
            logger.info("未启用智能体，使用原始模型")
            logger.info("=== 聊天处理完成（使用原始模型）===")
            return self.base_model.chat(messages, temperature, stream)
        
        if not self.is_initialized:
            logger.warning("智能体未初始化，使用原始模型")
            logger.info("=== 聊天处理完成（使用原始模型）===")
            return self.base_model.chat(messages, temperature, stream)
        
        logger.info("使用智能体模式聊天")
        
        try:
            # 使用智能体模式
            latest_input, chat_history = MessageUtils.extract_latest_input(messages)
            logger.info(f"提取的最新输入: 长度={len(latest_input)} 字符")
            logger.debug(f"  内容: {latest_input}")
            logger.info(f"聊天历史消息数: {len(chat_history)}")
            if chat_history:
                logger.debug(f"  历史消息示例: {chat_history[:2]}")
            
            # 构建完整的提示词输入，合并用户输入和提示词工程
            from app.utils.prompt_utils import PromptUtils
            # 智能体模式下直接使用原始输入，避免重复系统提示词
            if use_agent and self.is_initialized:
                enhanced_input = latest_input
            else:
                enhanced_input = PromptUtils.build_prompt(
                    query=latest_input,
                    chat_history=chat_history
                )
            logger.info(f"增强后的输入长度: {len(enhanced_input)} 字符")
            logger.debug(f"  增强内容: {enhanced_input}")
            
            # 尝试调用智能体
            try:
                logger.info("开始调用智能体执行器...")
                logger.debug(f"调用参数: input={enhanced_input[:100]}..., chat_history_count={len(chat_history)}")
                
                result = await self.agent_executor.ainvoke({
                    "input": enhanced_input,
                    "chat_history": chat_history
                })
                
                logger.info(f"智能体调用成功，结果类型: {type(result).__name__}")
                logger.debug(f"完整返回结果: {result}")
                
                # 提取内容
                content = result.get('output', str(result))
                logger.info(f"智能体回复长度: {len(content)} 字符")
                logger.debug(f"  内容: {content}")
                
                logger.info("=== 聊天处理完成（使用智能体）===")
                return {"content": content, "content_struct": None, "raw_result": result}
                    
            except Exception as e:
                logger.error(f"调用智能体失败: {str(e)}")
                logger.exception("智能体调用异常详情:")
                logger.warning("回退到原始模型")
                logger.info("=== 聊天处理完成（回退到原始模型）===")
                return self.base_model.chat(messages, temperature, stream)
                
        except Exception as e:
            logger.error(f"智能体聊天失败: {str(e)}")
            logger.exception("聊天处理异常详情:")
            logger.warning("回退到原始模型")
            logger.info("=== 聊天处理完成（回退到原始模型）===")
            return self.base_model.chat(messages, temperature, stream)
    
    async def chat_stream(self, 
                         messages: List[Dict[str, str]], 
                         temperature: float,
                         use_agent: bool = True) -> AsyncIterator[str]:
        """流式聊天接口"""
        print(f"🌊 AgentWrapper.chat_stream() 被调用，use_agent={use_agent}")
        
        from app.core.logging_config import logger
        
        logger.info("=== 开始流式聊天处理 ===")
        logger.info(f"配置参数: use_agent={use_agent}, is_initialized={self.is_initialized}, temperature={temperature}")
        
        # 记录消息详情
        logger.info(f"消息数量: {len(messages)}")
        for i, msg in enumerate(messages):
            msg_role = msg.get('role', 'unknown')
            msg_content = msg.get('content', '')
            logger.info(f"消息 {i+1}: 角色={msg_role}, 内容长度={len(msg_content)} 字符")
            if len(msg_content) < 200:
                logger.debug(f"  内容: {msg_content}")
            else:
                logger.debug(f"  内容: {msg_content[:200]}...")
        
        if not use_agent:
            logger.info("未启用智能体，使用原始模型流式方法")
            logger.info("=== 流式聊天处理开始（使用原始模型）===")
            try:
                async for chunk in self.base_model.chat_stream(messages, temperature):
                    logger.debug(f"原始模型流式返回: {chunk[:100]}...")
                    yield chunk
                logger.info("=== 流式聊天处理完成（使用原始模型）===")
            except Exception as e:
                logger.error(f"原始模型流式方法失败: {str(e)}")
                logger.info("=== 流式聊天处理失败 ===")
                raise
            return
        
        if not self.is_initialized:
            logger.warning("智能体未初始化，使用原始模型流式方法")
            logger.info("=== 流式聊天处理开始（使用原始模型）===")
            try:
                async for chunk in self.base_model.chat_stream(messages, temperature):
                    logger.debug(f"原始模型流式返回: {chunk[:100]}...")
                    yield chunk
                logger.info("=== 流式聊天处理完成（使用原始模型）===")
            except Exception as e:
                logger.error(f"原始模型流式方法失败: {str(e)}")
                logger.info("=== 流式聊天处理失败 ===")
                raise
            return
        
        logger.info("使用智能体模式流式聊天")
        
        try:
            # 提取最新输入和聊天历史
            latest_input, chat_history = MessageUtils.extract_latest_input(messages)
            logger.info(f"提取的最新输入: 长度={len(latest_input)} 字符")
            logger.debug(f"  内容: {latest_input}")
            logger.info(f"聊天历史消息数: {len(chat_history)}")
            if chat_history:
                logger.debug(f"  历史消息示例: {chat_history[:2]}")
            
            # 请求重写逻辑：当检测到查看目录请求时，强制使用文件系统工具
            directory_keywords = ['查看当前目录', '列出文件', '当前目录', '当前文件夹', '目录内容', '文件夹内容', 'ls', 'dir']
            is_directory_request = any(keyword in latest_input for keyword in directory_keywords)
            
            if is_directory_request:
                logger.info("检测到查看目录请求，重写输入以强制使用文件系统工具")
                # 重写输入，明确指示使用文件系统工具
                enhanced_input = f"请使用文件系统工具列出当前目录的文件和文件夹。具体来说，应该使用list_directory工具或类似的目录列出工具。"
            else:
                # 构建完整的提示词输入，合并用户输入和提示词工程
                from app.utils.prompt_utils import PromptUtils
                # 智能体模式下直接使用原始输入，避免重复系统提示词
                if use_agent and self.is_initialized:
                    enhanced_input = latest_input
                else:
                    enhanced_input = PromptUtils.build_prompt(
                        query=latest_input,
                        chat_history=chat_history
                    )
            logger.info(f"增强后的输入长度: {len(enhanced_input)} 字符")
            logger.debug(f"  增强内容: {enhanced_input}")
            
            # 尝试使用智能体原生流式方法
            try:
                logger.info("使用智能体原生流式方法")
                logger.info("=== 智能体原生流式处理开始 ===")
                
                # 累积的内容
                accumulated_content = ""
                chunk_count = 0
                
                logger.debug(f"调用智能体流式接口: input={enhanced_input[:100]}..., chat_history_count={len(chat_history)}")
                
                # 流式调用
                async for event in self.agent_executor.astream_events({
                    "input": enhanced_input,
                    "chat_history": chat_history
                }, version="v1"):
                    chunk_count += 1
                    logger.info(f"接收到流式事件 #{chunk_count}: {event['event']}")
                    logger.debug(f"  事件详情: {event}")
                    
                    # 处理工具调用事件
                    if event['event'] == 'start' and event.get('node') == 'tools':
                        tool_calls_content = "正在执行工具..."
                        formatted_chunk = StreamUtils.format_stream_chunk(tool_calls_content, agent=True)
                        logger.debug(f"  发送工具调用通知: {formatted_chunk}")
                        yield formatted_chunk
                    
                    # 处理工具结果事件
                    elif event['event'] == 'end' and event.get('node') == 'tools':
                        tool_results = event.get('data', {}).get('output', {})
                        if tool_results:
                            tool_content = f"工具执行结果: {tool_results}"
                            formatted_chunk = StreamUtils.format_stream_chunk(tool_content, agent=True)
                            logger.debug(f"  发送工具执行结果: {formatted_chunk}")
                            yield formatted_chunk
                    
                    # 处理响应事件
                    elif event['event'] == 'end' and event.get('node') == 'respond':
                        output = event.get('data', {}).get('output', {}).get('output', '')
                        if output:
                            if output != accumulated_content:
                                # 计算新内容
                                new_content = output[len(accumulated_content):]
                                if new_content:
                                    logger.info(f"智能体回复内容: 长度={len(new_content)} 字符")
                                    logger.debug(f"  内容: {new_content}")
                                    formatted_chunk = StreamUtils.format_stream_chunk(new_content, agent=True)
                                    logger.debug(f"  发送响应 chunk: {formatted_chunk}")
                                    yield formatted_chunk
                                    accumulated_content = output
                
                logger.info(f"智能体原生流式处理完成，共接收 {chunk_count} 个事件")
                done_signal = StreamUtils.format_stream_done(agent=True)
                logger.debug(f"发送完成信号: {done_signal}")
                yield done_signal
                logger.info("=== 智能体原生流式处理完成 ===")
                return
                
            except Exception as e:
                logger.error(f"使用智能体原生流式方法失败: {str(e)}")
                logger.exception("智能体原生流式方法异常详情:")
            
            # 智能体原生流式方法失败，直接回退到原始模型
            logger.warning("智能体原生流式方法失败，回退到原始模型")
            
            # 回退到原始模型
            logger.info("=== 回退到原始模型流式处理 ===")
            try:
                fallback_chunk_count = 0
                async for chunk in self.base_model.chat_stream(messages, temperature):
                    fallback_chunk_count += 1
                    logger.debug(f"原始模型回退返回 chunk #{fallback_chunk_count}: {chunk[:100]}...")
                    yield chunk
                logger.info(f"原始模型回退完成，共发送 {fallback_chunk_count} 个 chunk")
            except Exception as fallback_error:
                logger.error(f"原始模型回退也失败: {fallback_error}")
            finally:
                logger.info("=== 流式聊天处理完成 ===")
                return
                
        except Exception as e:
            logger.error(f"智能体流式聊天失败: {str(e)}")
            logger.exception("流式聊天异常详情:")
            logger.warning("回退到原始模型")
            
            # 出错时回退到原始模型
            logger.info("=== 回退到原始模型流式处理 ===")
            try:
                fallback_chunk_count = 0
                async for chunk in self.base_model.chat_stream(messages, temperature):
                    fallback_chunk_count += 1
                    logger.debug(f"原始模型回退返回 chunk #{fallback_chunk_count}: {chunk[:100]}...")
                    yield chunk
                logger.info(f"原始模型回退完成，共发送 {fallback_chunk_count} 个 chunk")
            except Exception as fallback_error:
                logger.error(f"原始模型回退也失败: {fallback_error}")
            finally:
                logger.info("=== 流式聊天处理完成 ===")
                return
    
    def __getattr__(self, name):
        """转发其他方法到原始模型"""
        return getattr(self.base_model, name)