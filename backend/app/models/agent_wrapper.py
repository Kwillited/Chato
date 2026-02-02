import asyncio
import json
from typing import Dict, Any, List, Optional, AsyncIterator
from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
)
from langgraph.graph import StateGraph, END
from app.models.base_model import BaseModel
from app.utils.mcp.mcp_adapter import mcp_adapter
from app.core.logging_config import logger

# --- 序列化辅助函数 ---
def serialize_message(message):
    if hasattr(message, 'dict'): return message.dict()
    if hasattr(message, '__dict__'): return message.__dict__
    return str(message)

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
        # 绑定工具后的模型
        self.llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm
        self.graph = self._build_graph()
        self.is_initialized = True

    # --- 图节点逻辑 ---

    async def _think_node(self, state: Dict):
        """
        节点 1：思考节点。
        使用原始 LLM（不带工具），强制模型进行分析和规划。
        """
        logger.info("[Agent] 正在思考规划...")
        
        # 构建一个临时的 Prompt，要求模型只思考不行动
        # 我们在消息列表末尾增加一个提示，但不真正改变 state["messages"]
        thinking_prompt = state["messages"] + [
            HumanMessage(content=(
                "[系统指令：请简要说明你接下来的计划（例如：'我将调用XX工具查XX' 或 '我已经拿到结果，准备进行总结回复'）。"
                "注意：只需写出思考和计划，不要直接回答用户的问题，也不要调用工具。请以'【思考】：'开头。]"
            ))
        ]
        
        # 调用不带工具的 LLM
        ai_msg = await self.llm.ainvoke(thinking_prompt)
        
        # 将思考结果存入消息历史
        return {
            "messages": state["messages"] + [ai_msg]
        }

    async def _analyze_node(self, state: Dict):
        """
        节点 2：决策/行动节点。
        带着思考后的背景，决定是调用工具还是给出最终回答。
        """
        logger.info("[Agent] 正在决策行动...")
        # 调用带工具绑定的模型
        ai_msg = await self.llm_with_tools.ainvoke(state["messages"])
        return {
            "messages": state["messages"] + [ai_msg],
            "loop_count": state.get("loop_count", 0)
        }

    async def _execute_tools_node(self, state: Dict):
        """节点 3：工具执行节点"""
        last_msg = state["messages"][-1]
        tool_calls = getattr(last_msg, 'tool_calls', [])
        new_messages = []
        tools_map = {t.name: t for t in self.tools_cache} if self.tools_cache else {}
        
        for tc in tool_calls:
            t_name, t_args, t_id = tc['name'], tc['args'], tc['id']
            try:
                if t_name in tools_map:
                    result = await tools_map[t_name].ainvoke(t_args)
                    res_str = json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result
                else:
                    res_str = f"Error: Tool {t_name} not found"
            except Exception as e:
                res_str = f"Error: {str(e)}"
            
            new_messages.append(ToolMessage(content=res_str, tool_call_id=t_id))
        
        return {
            "messages": state["messages"] + new_messages,
            "loop_count": state.get("loop_count", 0) + 1
        }

    def _build_graph(self):
        """构建逻辑图：Think -> Analyze -> (Tool? -> Execute -> Think | End)"""
        
        def should_continue(state: Dict):
            last_msg = state["messages"][-1]
            # 如果 Analyze 节点输出了工具调用
            if getattr(last_msg, 'tool_calls', []) and state.get("loop_count", 0) < 5:
                return "execute_tools"
            return END

        builder = StateGraph(dict)
        
        builder.add_node("think", self._think_node)
        builder.add_node("analyze", self._analyze_node)
        builder.add_node("execute_tools", self._execute_tools_node)
        
        # 入口改为思考节点
        builder.set_entry_point("think")
        
        # 思考完后必定进入决策节点
        builder.add_edge("think", "analyze")
        
        # 决策节点后判断是执行工具还是结束
        builder.add_conditional_edges(
            "analyze",
            should_continue,
            {
                "execute_tools": "execute_tools",
                END: END
            }
        )
        
        # 执行完工具后，回到思考节点进行结果分析
        builder.add_edge("execute_tools", "think")
        
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
        
        if not use_agent:
            async for event in self.llm.astream_events(prepared_messages, version="v2"):
                if event.get('event') == "on_chat_model_stream":
                    content = event.get('data', {}).get('chunk', {}).content
                    if content:
                        yield {'event': 'on_chat_model_stream', 'data': {'chunk': {'content': content}}}
            return

        initial_state = {
            "messages": prepared_messages,
            "loop_count": 0
        }
        
        try:
            async for event in self.graph.astream_events(initial_state, version="v2"):
                kind = event.get('event')
                # metadata 里的 langgraph_node 可以帮我们区分现在是哪个节点在出流
                node = event.get('metadata', {}).get('langgraph_node', '')

                # 1. 捕获文本流 (不管是 think 节点还是 analyze 节点)
                if kind == "on_chat_model_stream":
                    chunk = event.get('data', {}).get('chunk')
                    if chunk and chunk.content:
                        yield {
                            'event': 'on_chat_model_stream',
                            'node': node,  # 返回节点名，方便前端区分
                            'data': {'chunk': {'content': chunk.content}}
                        }
                    
                    if chunk and hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
                        yield {
                            'event': 'on_tool_call_stream',
                            'data': {'tool_calls': chunk.tool_call_chunks}
                        }

                # 2. 工具执行事件
                elif kind == "on_tool_start":
                    yield {
                        'event': 'on_tool_start',
                        'name': event.get('name'),
                        'data': {'input': event.get('data', {}).get('input', {})}
                    }
                elif kind == "on_tool_end":
                    yield {
                        'event': 'on_tool_end',
                        'name': event.get('name'),
                        'data': {'output': event.get('data', {}).get('output', {})}
                    }

        except Exception as e:
            logger.error(f"[Agent] Stream Error: {str(e)}")
            yield {"event": "on_node_error", "data": {"error": str(e)}}

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