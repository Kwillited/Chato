# agent_wrapper.py
from typing import Dict, Any, List, Optional, Union, Callable, AsyncIterator
from functools import wraps
from app.models.base_model import BaseModel
from app.utils.message_utils import MessageUtils
from app.utils.stream_utils import StreamUtils
from app.utils.mcp.mcp_adapter import mcp_adapter
from langchain_core.prompts import ChatPromptTemplate

# 导入智能体创建API
from app.core.logging_config import logger

try:
    from langchain.agents import create_agent
except ImportError:
    logger.error("无法导入智能体创建API，智能体功能不可用")
    create_agent = None


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
        self.is_initialized = False
        print(f"✅ AgentWrapper 初始化完成，base_model: {type(base_model).__name__}")
    
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
        
        # 使用 create_agent API
        try:
            if create_agent:
                logger.info("使用 create_agent API 创建智能体...")
                
                # 使用 create_agent API
                logger.debug("开始调用 create_agent API")
                self.agent_executor = create_agent(
                    model=self.llm,
                    tools=mcp_adapter.get_tools(),
                    system_prompt=final_system_prompt,
                    debug=verbose
                )
                logger.debug("create_agent API 调用完成")
                
                logger.info("智能体执行器类型: {type(self.agent_executor).__name__}")
                logger.info("使用 create_agent API 创建智能体成功")
                self.is_initialized = True
                logger.info("智能体初始化完成，状态: 成功")
                logger.info("=== 智能体初始化完成 ===")
            else:
                logger.error("create_agent 未导入，智能体功能不可用")
                logger.error("智能体初始化完成，状态: 失败")
                logger.info("=== 智能体初始化完成 ===")
        except Exception as e:
            logger.error(f"使用 create_agent API 初始化智能体失败: {str(e)}")
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
                
                # 增强的内容提取逻辑
                if isinstance(result, dict):
                    logger.info(f"结果字典键: {list(result.keys())}")
                    # 尝试多种可能的字段名
                    content_fields = ["output", "content", "answer", "response"]
                    for field in content_fields:
                        if field in result:
                            content = result[field]
                            logger.info(f"从字段 '{field}' 提取内容: 长度={len(str(content))} 字符")
                            logger.debug(f"  内容: {content}")
                            return {"content": content, "content_struct": None, "raw_result": result}
                    
                    # 处理嵌套的消息结构
                    if "messages" in result:
                        nested_messages = result["messages"]
                        logger.info(f"嵌套消息数量: {len(nested_messages)}")
                        if nested_messages and len(nested_messages) > 0:
                            first_message = nested_messages[0]
                            if hasattr(first_message, "content"):
                                content = first_message.content
                                logger.info(f"从嵌套消息对象提取内容: 长度={len(str(content))} 字符")
                                logger.debug(f"  内容: {content}")
                                return {"content": content, "content_struct": None, "raw_result": result}
                            elif isinstance(first_message, dict) and "content" in first_message:
                                content = first_message["content"]
                                logger.info(f"从嵌套消息字典提取内容: 长度={len(str(content))} 字符")
                                logger.debug(f"  内容: {content}")
                                return {"content": content, "content_struct": None, "raw_result": result}
                    
                    # 检查是否有工具调用结果
                    if "tool_calls" in result:
                        tool_calls = result["tool_calls"]
                        logger.info(f"工具调用数量: {len(tool_calls)}")
                        for i, tool_call in enumerate(tool_calls):
                            logger.debug(f"  工具调用 {i+1}: {tool_call}")
                
                # 最后尝试转换为字符串
                content = str(result)
                logger.info(f"转换为字符串提取内容: 长度={len(content)} 字符")
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
        
        # 强制重新初始化智能体，确保使用最新的系统提示词和工具配置
        logger.info("强制重新初始化智能体...")
        await self.initialize(force_reinit=True)
        
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
                # 检查是否有 astream 方法
                if hasattr(self.agent_executor, 'astream'):
                    logger.info("使用智能体原生流式方法 astream")
                    logger.info("=== 智能体原生流式处理开始 ===")
                    
                    # 累积的内容
                    accumulated_content = ""
                    chunk_count = 0
                    
                    logger.debug(f"调用智能体 astream: input={enhanced_input[:100]}..., chat_history_count={len(chat_history)}")
                    async for chunk in self.agent_executor.astream({
                        "input": enhanced_input,
                        "chat_history": chat_history
                    }):
                        chunk_count += 1
                        logger.info(f"接收到流式 chunk #{chunk_count}")
                        logger.debug(f"  Chunk 内容: {chunk}")
                        
                        if isinstance(chunk, dict):
                            # 增强的内容提取逻辑
                            content = ""
                            
                            # 检查是否有工具执行结果
                            if "tool_responses" in chunk:
                                logger.info("发现工具执行结果 chunk")
                                # 处理工具执行结果
                                tool_responses = chunk["tool_responses"]
                                for tool_response in tool_responses:
                                    try:
                                        if isinstance(tool_response, dict):
                                            if "output" in tool_response:
                                                tool_content = "工具执行结果: " + tool_response["output"]
                                            elif "result" in tool_response:
                                                tool_content = "工具执行结果: " + str(tool_response["result"])
                                            else:
                                                tool_content = "工具执行结果: " + str(tool_response)
                                            logger.info(f"提取工具响应结果: 长度={len(tool_content)} 字符")
                                            logger.debug(f"  结果: {tool_content[:200]}...")
                                            formatted_chunk = StreamUtils.format_stream_chunk(tool_content, agent=True)
                                            logger.debug(f"  发送工具响应结果: {formatted_chunk}")
                                            yield formatted_chunk
                                    except Exception as e:
                                        logger.error(f"处理工具响应失败: {str(e)}")
                            
                            # 尝试多种可能的字段名
                            content_fields = ["output", "content", "answer", "response"]
                            for field in content_fields:
                                if field in chunk:
                                    content = chunk[field]
                                    logger.info(f"从字段 '{field}' 提取内容: 长度={len(str(content))} 字符")
                                    break
                            
                            # 处理嵌套的消息结构
                            if not content and "messages" in chunk:
                                nested_messages = chunk["messages"]
                                logger.info(f"发现嵌套消息结构，消息数: {len(nested_messages)}")
                                if nested_messages and len(messages) > 0:
                                    first_message = nested_messages[0]
                                    if hasattr(first_message, "content"):
                                        content = first_message.content
                                        logger.info(f"从嵌套消息对象提取内容: 长度={len(str(content))} 字符")
                                    elif isinstance(first_message, dict) and "content" in first_message:
                                        content = first_message["content"]
                                        logger.info(f"从嵌套消息字典提取内容: 长度={len(str(content))} 字符")
                            
                            # 处理 model.messages 嵌套结构（关键修复）
                            if not content and "model" in chunk:
                                model_data = chunk["model"]
                                if isinstance(model_data, dict) and "messages" in model_data:
                                    model_messages = model_data["messages"]
                                    logger.info(f"发现 model.messages 结构，消息数: {len(model_messages)}")
                                    if model_messages and len(model_messages) > 0:
                                        first_message = model_messages[0]
                                        if hasattr(first_message, "content"):
                                            content = first_message.content
                                            logger.info(f"从 model.messages 提取内容: {content[:100]}...")
                                        elif isinstance(first_message, dict) and "content" in first_message:
                                            content = first_message["content"]
                                            logger.info(f"从 model.messages 字典提取内容: {content[:100]}...")
                                    
                                    # 处理工具调用
                                    for msg in model_messages:
                                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                                            tool_calls_content = "正在执行工具: "
                                            tool_names = []
                                            for tool_call in msg.tool_calls:
                                                # 处理字典类型的tool_call
                                                if isinstance(tool_call, dict) and "name" in tool_call:
                                                    tool_names.append(tool_call['name'])
                                                # 处理对象类型的tool_call
                                                elif hasattr(tool_call, "name"):
                                                    tool_names.append(tool_call.name)
                                            if tool_names:
                                                tool_calls_content += "，".join(tool_names)
                                                logger.info(f"提取工具调用: {tool_calls_content}")
                                                formatted_chunk = StreamUtils.format_stream_chunk(tool_calls_content, agent=True)
                                                logger.debug(f"  发送工具调用通知: {formatted_chunk}")
                                                yield formatted_chunk
                            
                            # 处理 tools.messages 结构（工具执行结果）
                            if not content and "tools" in chunk:
                                tools_data = chunk["tools"]
                                if isinstance(tools_data, dict) and "messages" in tools_data:
                                    tool_messages = tools_data["messages"]
                                    logger.info(f"发现 tools.messages 结构，消息数: {len(tool_messages)}")
                                    for tool_msg in tool_messages:
                                        if hasattr(tool_msg, "content"):
                                            # 处理工具执行结果
                                            tool_content = "工具执行结果: "
                                            if isinstance(tool_msg.content, list):
                                                for item in tool_msg.content:
                                                    if isinstance(item, dict):
                                                        if "text" in item:
                                                            tool_content += item["text"]
                                                        elif "error" in item:
                                                            tool_content += f"错误: {item['error']}"
                                                    else:
                                                        tool_content += str(item)
                                            elif isinstance(tool_msg.content, str):
                                                tool_content += tool_msg.content
                                            else:
                                                tool_content += str(tool_msg.content)
                                            logger.info(f"提取工具执行结果: 长度={len(tool_content)} 字符")
                                            logger.debug(f"  结果: {tool_content[:200]}...")
                                            formatted_chunk = StreamUtils.format_stream_chunk(tool_content, agent=True)
                                            logger.debug(f"  发送工具执行结果: {formatted_chunk}")
                                            yield formatted_chunk
                            
                            # 处理 tool_responses 结构（工具执行结果）
                            if not content and "tool_responses" in chunk:
                                tool_responses = chunk["tool_responses"]
                                logger.info(f"发现 tool_responses 结构，响应数: {len(tool_responses)}")
                                for tool_response in tool_responses:
                                    try:
                                        if isinstance(tool_response, dict):
                                            # 处理字典类型的工具响应
                                            if "output" in tool_response:
                                                tool_content = "工具执行结果: " + tool_response["output"]
                                            elif "result" in tool_response:
                                                tool_content = "工具执行结果: " + str(tool_response["result"])
                                            elif "error" in tool_response:
                                                tool_content = "工具执行失败: " + str(tool_response["error"])
                                            else:
                                                tool_content = "工具执行结果: " + str(tool_response)
                                            logger.info(f"提取工具响应结果: 长度={len(tool_content)} 字符")
                                            logger.debug(f"  结果: {tool_content[:200]}...")
                                            formatted_chunk = StreamUtils.format_stream_chunk(tool_content, agent=True)
                                            logger.debug(f"  发送工具响应结果: {formatted_chunk}")
                                            yield formatted_chunk
                                        else:
                                            # 处理非字典类型的工具响应
                                            tool_content = "工具执行结果: " + str(tool_response)
                                            logger.info(f"提取工具响应结果（非字典）: 长度={len(tool_content)} 字符")
                                            logger.debug(f"  结果: {tool_content[:200]}...")
                                            formatted_chunk = StreamUtils.format_stream_chunk(tool_content, agent=True)
                                            logger.debug(f"  发送工具响应结果: {formatted_chunk}")
                                            yield formatted_chunk
                                    except Exception as e:
                                        logger.error(f"处理工具响应失败: {str(e)}")
                                        # 即使处理失败也要显示错误信息
                                        error_content = f"处理工具响应时出错: {str(e)}"
                                        formatted_chunk = StreamUtils.format_stream_chunk(error_content, agent=True)
                                        yield formatted_chunk
                            
                            if content and content != accumulated_content:
                                # 计算新内容
                                new_content = content[len(accumulated_content):]
                                if new_content:
                                    logger.info(f"智能体回复内容: 长度={len(new_content)} 字符")
                                    logger.debug(f"  内容: {new_content}")
                                    # 直接返回带有agent标记的原始响应
                                    formatted_chunk = StreamUtils.format_stream_chunk(new_content, agent=True)
                                    logger.debug(f"  发送响应 chunk: {formatted_chunk}")
                                    yield formatted_chunk
                                    accumulated_content = content
                            else:
                                # 打印其他类型的 chunk 以便调试
                                logger.debug(f"智能体返回其他类型 chunk: {chunk}")
                        else:
                            # 打印非字典类型的 chunk 以便调试
                            logger.debug(f"智能体返回非字典类型 chunk: {chunk}")
                    
                    # 发送完成信号，添加agent标记
                    logger.info(f"智能体原生流式处理完成，共接收 {chunk_count} 个 chunk")
                    done_signal = StreamUtils.format_stream_done(agent=True)
                    logger.debug(f"发送完成信号: {done_signal}")
                    yield done_signal
                    logger.info("=== 智能体原生流式处理完成 ===")
                    return
                else:
                    logger.info("智能体执行器不支持 astream 方法")
            except Exception as e:
                logger.error(f"使用智能体原生流式方法失败: {str(e)}")
                logger.exception("智能体原生流式方法异常详情:")
            
            # 回退到模拟流式方法
            logger.info("回退到模拟流式方法")
            logger.info("=== 模拟流式处理开始 ===")
            
            logger.debug("调用同步聊天获取完整结果...")
            result = await self.chat(messages, temperature, stream=False, use_agent=True)
            
            # 提取内容
            content = ""
            if isinstance(result, dict):
                content = result.get('content', '') or result.get('output', '') or result.get('answer', '')
            elif isinstance(result, str):
                content = result
            else:
                content = str(result)
            
            logger.info(f"智能体响应长度: {len(content)} 字符")
            logger.debug(f"  内容: {content}")
            
            # 使用模拟流式（分块返回），添加agent标记
            logger.info(f"开始模拟流式分块，预计分块数: {len(content) // 3 + 1}")
            simulate_chunk_count = 0
            async for chunk in StreamUtils.simulate_stream(content, chunk_size=3, delay=0.03, agent=True):
                simulate_chunk_count += 1
                logger.debug(f"模拟流式返回 chunk #{simulate_chunk_count}: {chunk}")
                yield chunk
            
            logger.info(f"模拟流式返回完成，共发送 {simulate_chunk_count} 个 chunk")
            logger.info("=== 模拟流式处理完成 ===")
            
        except Exception as e:
            logger.error(f"智能体流式聊天失败: {str(e)}")
            logger.exception("流式聊天异常详情:")
            logger.warning("回退到原始模型流式方法")
            
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
                logger.error(f"原始模型回退也失败: {str(fallback_error)}")
            finally:
                logger.info("=== 流式聊天处理完成 ===")
    
    def __getattr__(self, name):
        """转发其他方法到原始模型"""
        return getattr(self.base_model, name)