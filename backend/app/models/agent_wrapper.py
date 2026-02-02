import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncIterator

from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
)
from langgraph.graph import StateGraph, END
from app.models.base_model import BaseModel
from app.utils.mcp.mcp_adapter import mcp_adapter
from app.core.logging_config import logger

# 序列化辅助函数
def serialize_message(message):
    """将 LangChain 消息对象转换为可序列化的字典"""
    if hasattr(message, 'dict'):
        return message.dict()
    elif hasattr(message, '__dict__'):
        return message.__dict__
    else:
        return str(message)

def serialize_event(event):
    """递归序列化事件中的所有对象"""
    if isinstance(event, dict):
        return {k: serialize_event(v) for k, v in event.items()}
    elif isinstance(event, list):
        return [serialize_event(item) for item in event]
    elif isinstance(event, (BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage)):
        return serialize_message(event)
    else:
        return event

class AgentWrapper:
    def __init__(self, base_model: BaseModel):
        self.base_model = base_model
        self.llm = base_model.llm
        self.llm_with_tools = None
        self.graph = None
        self.is_initialized = False
        self.tools_cache = None

    async def initialize(self, mcp_config: Optional[Dict] = None):
        if self.is_initialized: return
        await mcp_adapter.initialize(mcp_config)
        tools = mcp_adapter.get_tools()
        self.tools_cache = tools
        if tools:
            self.llm_with_tools = self.llm.bind_tools(tools)
        self.graph = self._build_graph()
        self.is_initialized = True

    async def _analyze_node(self, state):
        """分析节点逻辑"""
        logger.info("[Agent] 分析中...")
        ai_msg = await self.llm_with_tools.ainvoke(state["messages"])
        return {
            "messages": state["messages"] + [ai_msg],
            "tool_results": state.get("tool_results", {}),
            "is_finished": state.get("is_finished", False)
        }

    async def _execute_tools_node(self, state):
        """工具执行节点逻辑"""
        last_msg = state["messages"][-1]
        tool_calls = getattr(last_msg, 'tool_calls', [])
        if not tool_calls:
            return state
        
        tools_map = {t.name: t for t in self.tools_cache}
        tool_results = state.get("tool_results", {})
        messages = state["messages"].copy()
        
        for tc in tool_calls:
            t_name, t_args, t_id = tc['name'], tc['args'], tc['id']
            logger.info(f"[Agent] 执行工具 {t_name}，参数: {t_args}")
            
            try:
                if t_name in tools_map:
                    result = await tools_map[t_name].ainvoke(t_args)
                    res_str = str(result)
                    tool_results[t_id] = res_str
                    messages.append(ToolMessage(content=res_str, tool_call_id=t_id))
                    logger.info(f"[Agent] 工具 {t_name} 执行成功")
                else:
                    error_msg = f"Error: 工具 {t_name} 未找到"
                    tool_results[t_id] = error_msg
                    messages.append(ToolMessage(content=error_msg, tool_call_id=t_id))
                    logger.warning(f"[Agent] 工具 {t_name} 未找到")
            except Exception as e:
                error_msg = f"Error executing tool {t_name}: {str(e)}"
                tool_results[t_id] = error_msg
                messages.append(ToolMessage(content=error_msg, tool_call_id=t_id))
                logger.error(f"[Agent] 执行工具 {t_name} 时出错: {str(e)}")
        
        return {
            "messages": messages,
            "tool_results": tool_results,
            "is_finished": state.get("is_finished", False)
        }

    async def _generate_response_node(self, state):
        """生成响应节点逻辑"""
        logger.info("[Agent] 开始生成响应...")
        return {
            "messages": state["messages"],
            "tool_results": state.get("tool_results", {}),
            "is_finished": True
        }

    def _build_graph(self):
        """构建循环执行的 LangGraph 图"""
        # 分析节点
        async def analyze_node(state):
            return await self._analyze_node(state)

        # 工具执行节点
        async def execute_tools_node(state):
            return await self._execute_tools_node(state)

        # 生成响应节点
        async def generate_response_node(state):
            return await self._generate_response_node(state)
        
        # 工具执行后处理节点
        async def after_execute_tools(state):
            # 增加循环计数
            new_state = state.copy()
            new_state["loop_count"] = state.get("loop_count", 0) + 1
            return new_state
        
        # 判断是否需要继续执行的条件函数
        def should_continue(state):
            last_msg = state["messages"][-1]
            # 检查是否有工具调用
            tool_calls = getattr(last_msg, 'tool_calls', [])
            # 检查循环次数，防止无限循环
            loop_count = state.get("loop_count", 0)
            if loop_count >= 5:  # 最大循环次数限制
                logger.warning("Maximum loop count reached, exiting loop")
                return "generate_response"
            # 如果有工具调用，继续执行工具节点
            if tool_calls:
                return "execute_tools"
            # 否则，生成响应并结束
            return "generate_response"

        # 构建图
        builder = StateGraph(dict)
        builder.add_node("analyze", analyze_node)
        builder.add_node("execute_tools", execute_tools_node)
        builder.add_node("after_execute_tools", after_execute_tools)  # 注册为节点
        builder.add_node("generate_response", generate_response_node)
        
        builder.set_entry_point("analyze")
        # 分析节点之后，根据条件决定下一步
        builder.add_conditional_edges(
            "analyze",
            should_continue,
            {
                "execute_tools": "execute_tools",
                "generate_response": "generate_response"
            }
        )
        # 工具执行节点之后，经过处理节点回到分析节点，形成循环
        builder.add_edge("execute_tools", "after_execute_tools")
        builder.add_edge("after_execute_tools", "analyze")
        builder.add_edge("generate_response", END)
        
        return builder.compile()

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float, use_agent: bool = True) -> AsyncIterator[Dict[str, Any]]:
        if not self.is_initialized:
            await self.initialize()

        input_messages = self._prepare_messages(messages)
        
        try:
            # 初始化状态
            initial_state = {
                "messages": input_messages,
                "tool_results": {},
                "is_finished": False,
                "loop_count": 0
            }
            
            logger.info("[Agent] 开始执行工作流")
            logger.info(f"[Agent] 输入消息: {messages}")
            
            # 记录最终状态
            final_workflow_state = initial_state
            
            # 使用编译后的图执行工作流
            async for event in self.graph.astream_events(initial_state, version="v1"):
                # 序列化事件中的所有对象
                serialized_event = serialize_event(event)
                
                # 对工作流事件进行过滤
                if serialized_event.get('event') == 'on_tool_start':
                    # 过滤工具开始事件，只保留有用的数据
                    filtered_event = {
                        'event': 'on_tool_start',
                        'name': serialized_event.get('name'),
                        'data': {
                            'input': serialized_event.get('data', {}).get('input', {})
                        }
                    }
                    # 打印过滤后的工具开始事件信息
                    logger.info(f"[Agent] 过滤后的工作流事件: {filtered_event}")
                    yield filtered_event
                else:
                    # 其他事件保持原样
                    logger.info(f"[Agent] 工作流事件: {serialized_event}")
                    yield serialized_event
                
                # 捕获最终状态
                if event.get('event') == 'on_complete':
                    final_workflow_state = event.get('data', {}).get('state', initial_state)
            
            # 工作流执行完成后，流式返回最终的 LLM 响应
            # 构建最终状态，包含所有消息
            final_state = {
                "messages": final_workflow_state["messages"],
                "tool_results": final_workflow_state.get("tool_results", {}),
                "is_finished": True
            }
            
            logger.info("[Agent] 工作流执行完成，开始生成最终响应")
            
            # 流式返回 LLM 事件
            async for event in self.llm.astream_events(final_state["messages"]):
                # 序列化事件中的所有对象
                serialized_event = serialize_event(event)
                
                # 对事件进行过滤
                if serialized_event.get('event') == 'on_chat_model_stream':
                    # 只保留事件类型和内容数据
                    filtered_event = {
                        'event': 'on_chat_model_stream',
                        'data': {
                            'chunk': {
                                'content': serialized_event.get('data', {}).get('chunk', {}).get('content', '')
                            }
                        }
                    }
                    # 打印过滤后的 LLM 事件信息
                    # logger.info(f"[Agent] 过滤后的 LLM 事件: {filtered_event}")
                    yield filtered_event
                elif serialized_event.get('event') == 'on_tool_start':
                    # 过滤工具开始事件，只保留有用的数据
                    filtered_event = {
                        'event': 'on_tool_start',
                        'name': serialized_event.get('name'),
                        'data': {
                            'input': serialized_event.get('data', {}).get('input', {})
                        }
                    }
                    # 打印过滤后的工具开始事件信息
                    # logger.info(f"[Agent] 过滤后的工具开始事件: {filtered_event}")
                    yield filtered_event
                else:
                    # 其他事件保持原样
                    logger.info(f"[Agent] LLM 事件: {serialized_event}")
                    yield serialized_event

        except (GeneratorExit, asyncio.CancelledError):
            logger.info("[Agent] 通讯管道关闭，清理资源")
            # 对于 GeneratorExit，不应该 yield 任何值，直接返回
            return
        except Exception as e:
            logger.error(f"[Agent] 异常: {str(e)}")
            error_event = {
                "event": "on_node_error",
                "data": {
                    "error": str(e)
                }
            }
            logger.error(f"[Agent] 错误事件: {error_event}")
            yield error_event

    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        formatted = []
        for msg in messages:
            role, content = msg.get('role', 'user'), msg.get('content', '')
            if role == 'user': formatted.append(HumanMessage(content=content))
            elif role == 'assistant': formatted.append(AIMessage(content=content))
            elif role == 'system': formatted.append(SystemMessage(content=content))
        return formatted

    def __getattr__(self, name):
        return getattr(self.base_model, name)