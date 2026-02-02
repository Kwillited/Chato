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

    async def initialize(self, mcp_config: Optional[Dict] = None):
        if self.is_initialized: return
        await mcp_adapter.initialize(mcp_config)
        tools = mcp_adapter.get_tools()
        if tools:
            self.llm_with_tools = self.llm.bind_tools(tools)
        self.graph = self._build_graph()
        self.is_initialized = True

    def _build_graph(self):
        """构建简单的 LangGraph 图"""
        # 分析节点
        async def analyze_node(state):
            print("[Agent] Step 1: 分析中...")
            ai_msg = await self.llm_with_tools.ainvoke(state["messages"])
            return {
                "messages": state["messages"] + [ai_msg],
                "tool_results": state.get("tool_results", {}),
                "is_finished": state.get("is_finished", False)
            }

        # 工具执行节点
        async def execute_tools_node(state):
            last_msg = state["messages"][-1]
            tool_calls = getattr(last_msg, 'tool_calls', [])
            if not tool_calls:
                return state
            
            tools_map = {t.name: t for t in mcp_adapter.get_tools()}
            tool_results = state.get("tool_results", {})
            messages = state["messages"].copy()
            
            for tc in tool_calls:
                t_name, t_args, t_id = tc['name'], tc['args'], tc['id']
                print(f"[Agent] Step 2: 执行工具 {t_name}")
                
                try:
                    if t_name in tools_map:
                        result = await tools_map[t_name].ainvoke(t_args)
                        res_str = str(result)
                        tool_results[t_id] = res_str
                        messages.append(ToolMessage(content=res_str, tool_call_id=t_id))
                    else:
                        error_msg = f"Error: {t_name} not found"
                        tool_results[t_id] = error_msg
                        messages.append(ToolMessage(content=error_msg, tool_call_id=t_id))
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    tool_results[t_id] = error_msg
                    messages.append(ToolMessage(content=error_msg, tool_call_id=t_id))
            
            return {
                "messages": messages,
                "tool_results": tool_results,
                "is_finished": state.get("is_finished", False)
            }

        # 生成响应节点
        async def generate_response_node(state):
            print("[Agent] Step 3: 开始吐流...")
            return {
                "messages": state["messages"],
                "tool_results": state.get("tool_results", {}),
                "is_finished": True
            }

        # 构建图 - 使用简单的状态结构
        builder = StateGraph(dict)
        builder.add_node("analyze", analyze_node)
        builder.add_node("execute_tools", execute_tools_node)
        builder.add_node("generate_response", generate_response_node)
        
        builder.set_entry_point("analyze")
        builder.add_edge("analyze", "execute_tools")
        builder.add_edge("execute_tools", "generate_response")
        builder.add_edge("generate_response", END)
        
        return builder.compile()

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float, use_agent: bool = True) -> AsyncIterator[Dict[str, Any]]:
        if not self.is_initialized:
            await self.initialize()

        input_messages = self._prepare_messages(messages)
        
        try:
            # 创建初始状态（字典格式）
            initial_state = {
                "messages": input_messages,
                "tool_results": {},
                "is_finished": False
            }

            # 执行图
            final_state = await self.graph.ainvoke(initial_state)
            
            # 检查是否有工具调用
            tool_calls = []
            if final_state["messages"]:
                last_msg = final_state["messages"][-2] if len(final_state["messages"]) >= 2 else None
                if last_msg:
                    tool_calls = getattr(last_msg, 'tool_calls', [])
                    
                    if tool_calls:
                        # 发送工具开始事件
                        for tc in tool_calls:
                            t_name, t_args, t_id = tc['name'], tc['args'], tc['id']
                            yield {
                                "event": "on_tool_start",
                                "data": {
                                    "tool_call": {
                                        "name": t_name,
                                        "args": t_args,
                                        "id": t_id
                                    }
                                }
                            }
                    
                    # 检查是否有工具结果（ToolMessage）
                    tool_results = final_state.get("tool_results", {})
                    if tool_results:
                        # 发送工具结束事件
                        for t_id, result in tool_results.items():
                            yield {
                                "event": "on_tool_end",
                                "data": {
                                    "tool_call_id": t_id,
                                    "result": result
                                }
                            }

            # 使用 astream_events() 获取完整事件流
            async for event in self.llm.astream_events(final_state["messages"]):
                # 序列化事件中的所有对象
                serialized_event = serialize_event(event)
                yield serialized_event

        except (GeneratorExit, asyncio.CancelledError):
            print("[Agent] 通讯管道关闭，清理资源")
            # 对于 GeneratorExit，不应该 yield 任何值，直接返回
            return
        except Exception as e:
            print(f"[Agent] 异常: {str(e)}")
            yield {
                "event": "on_chat_model_end",
                "data": {
                    "error": str(e)
                }
            }

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