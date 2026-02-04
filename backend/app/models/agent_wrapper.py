import asyncio
import json
from typing import Dict, Any, List, Optional, AsyncIterator, TypedDict, Annotated
import operator

from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
)
from langgraph.graph import StateGraph, END
from app.models.base_model import BaseModel
from app.utils.mcp.mcp_adapter import mcp_adapter
from app.core.logging_config import logger

# --- 定义智能体状态 ---
class AgentState(TypedDict):
    # messages 允许通过 operator.add 自动累加历史
    messages: Annotated[List[BaseMessage], operator.add]
    # 循环计数
    loop_count: int

class AgentWrapper:  # <--- 这里改回了 AgentWrapper，修复导入错误
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
        
        # 绑定工具：通用智能体需要工具定义来做推理和决策
        self.llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm
        self.graph = self._build_graph()
        self.is_initialized = True

    # --- 节点 1: 推理节点 (Reasoning) ---
    async def _reasoning_node(self, state: AgentState):
        """核心节点：负责思考、规划并决定下一步行动"""
        logger.info(f"[Agent] 正在进行第 {state['loop_count']+1} 轮推理...")
        
        system_prompt = (
            "你是一个拥有强大自主能力的通用智能体。请按以下流程思考：\n"
            "1. 分析用户意图和当前状态。\n"
            "2. 如果信息不足，决定调用什么工具，并在 <thought> 标签中说明理由。\n"
            "3. 如果信息足够，直接给出最终回答。\n"
            "请始终先在 <thought> 标签内进行内心独白，再输出结果或调用工具。"
        )
        
        msgs = state["messages"]
        # 确保系统提示词存在
        if not any(isinstance(m, SystemMessage) for m in msgs):
            msgs = [SystemMessage(content=system_prompt)] + msgs

        # 一次性调用：获取 [思考 + 工具调用] 或 [思考 + 最终回答]
        response = await self.llm_with_tools.ainvoke(msgs)
        
        return {
            "messages": [response],
            "loop_count": state["loop_count"]
        }

    # --- 节点 2: 执行节点 (Action) ---
    async def _execute_tools_node(self, state: AgentState):
        """执行工具调用"""
        last_msg = state["messages"][-1]
        tool_calls = getattr(last_msg, 'tool_calls', [])
        tools_map = {t.name: t for t in self.tools_cache} if self.tools_cache else {}
        
        # 存储工具调用索引和名称的映射
        self.tool_call_map = {}
        for i, tc in enumerate(tool_calls):
            tool_name = tc.get('name', '')
            if tool_name:
                self.tool_call_map[tool_name] = i
        
        tasks = []
        for i, tc in enumerate(tool_calls):
            # 为每个工具调用添加索引
            tasks.append(self._run_single_tool(tc, tools_map, tool_index=i))
        
        results = await asyncio.gather(*tasks)
        
        return {
            "messages": results,
            "loop_count": state["loop_count"] + 1
        }

    async def _run_single_tool(self, tool_call, tools_map, tool_index=0):
        t_name, t_args, t_id = tool_call['name'], tool_call['args'], tool_call['id']
        try:
            if t_name in tools_map:
                result = await tools_map[t_name].ainvoke(t_args)
                res_str = self._format_tool_result(result)
            else:
                res_str = f"错误: 未找到工具 {t_name}"
        except Exception as e:
            res_str = f"执行出错: {str(e)}"
        
        tool_message = ToolMessage(content=res_str, tool_call_id=t_id)
        # 为 ToolMessage 添加工具索引
        tool_message.tool_index = tool_index
        return tool_message

    # --- 构建图 ---
    def _build_graph(self):
        def should_continue(state: AgentState):
            last_msg = state["messages"][-1]
            # 如果模型输出了工具调用，且循环次数未超限
            if getattr(last_msg, 'tool_calls', []) and state["loop_count"] < 10:
                return "execute"
            return END

        builder = StateGraph(AgentState)
        builder.add_node("reasoning", self._reasoning_node)
        builder.add_node("execute", self._execute_tools_node)
        
        builder.set_entry_point("reasoning")
        builder.add_conditional_edges("reasoning", should_continue, {
            "execute": "execute",
            END: END
        })
        builder.add_edge("execute", "reasoning")
        
        return builder.compile()

    # --- 核心流式方法 ---
    async def chat_stream(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7, 
        use_agent: bool = True
    ) -> AsyncIterator[Dict[str, Any]]:
        
        if not self.is_initialized:
            await self.initialize()

        prepared_messages = self._prepare_messages(messages)
        
        # 1. 基础模式
        if not use_agent:
            async for event in self.llm.astream_events(prepared_messages, version="v2"):
                if event.get('event') == "on_chat_model_stream":
                    content = event.get('data', {}).get('chunk', {}).content
                    if content:
                        yield {'event': 'on_chat_model_stream', 'data': {'chunk': {'content': content}}}
            return

        # 2. 智能体模式
        initial_state = {
            "messages": prepared_messages,
            "loop_count": 0
        }
        
        # 节点执行步骤计数和当前节点跟踪
        agent_step = 0
        current_node = None
        
        try:
            async for event in self.graph.astream_events(initial_state, version="v2"):
                kind = event.get('event')
                metadata = event.get('metadata', {})
                node = metadata.get('langgraph_node', '')
                
                # 当节点变化时增加步骤计数
                if node != current_node and node:
                    agent_step += 1
                    current_node = node

                if kind == "on_chat_model_stream":
                    chunk = event.get('data', {}).get('chunk')
                    if chunk and chunk.content:
                        # 重点：此处输出包含 <thought> 标签，前端可根据此标签渲染 UI
                        yield {
                            'event': 'on_chat_model_stream',
                            'node': node,
                            'agent_step': agent_step,
                            'data': {'content': chunk.content}
                        }
                    
                    if chunk and hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
                        yield {
                            'event': 'on_tool_call_stream',
                            'node': node,
                            'agent_step': agent_step,
                            'data': {'tool_calls': chunk.tool_call_chunks}
                        }

                elif kind == "on_tool_start":
                    tool_name = event.get('name', '')
                    # 从工具调用映射中获取正确的 tool_index
                    tool_index = 0
                    if hasattr(self, 'tool_call_map') and tool_name in self.tool_call_map:
                        tool_index = self.tool_call_map[tool_name]
                    yield {
                        'event': 'on_tool_start',
                        'node': node,
                        'agent_step': agent_step,
                        'tool_index': tool_index,
                        'name': tool_name,
                        'data': {'input': event.get('data', {}).get('input', {})}
                    }
                elif kind == "on_tool_end":
                    tool_name = event.get('name', '')
                    # 从工具调用映射中获取正确的 tool_index
                    tool_index = 0
                    if hasattr(self, 'tool_call_map') and tool_name in self.tool_call_map:
                        tool_index = self.tool_call_map[tool_name]
                    yield {
                        'event': 'on_tool_end',
                        'node': node,
                        'agent_step': agent_step,
                        'tool_index': tool_index,
                        'name': tool_name,
                        'data': {'output': event.get('data', {}).get('output', {})}
                    }

        except Exception as e:
            logger.error(f"[Agent] Stream Error: {str(e)}")
            yield {"event": "on_error", "data": str(e)}

    def _format_tool_result(self, result: Any) -> str:
        if isinstance(result, str): return result
        return json.dumps(result, ensure_ascii=False)

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