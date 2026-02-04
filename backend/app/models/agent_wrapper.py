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
        # 基础 LLM（用于思考节点，不带工具，保证 100% 出流）
        self.llm = base_model.llm
        # 绑定工具后的 LLM（用于决策节点）
        self.llm_with_tools = None
        self.graph = None
        self.is_initialized = False
        self.tools_cache = None

    async def initialize(self, mcp_config: Optional[Dict] = None):
        if self.is_initialized: return
        await mcp_adapter.initialize(mcp_config)
        tools = mcp_adapter.get_tools()
        self.tools_cache = tools
        
        # 预绑定工具
        self.llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm
        self.graph = self._build_graph()
        self.is_initialized = True

    # --- 图节点逻辑 ---

    async def _think_node(self, state: Dict):
        """
        [节点 1] 思考节点：
        不加载工具定义，强制模型以纯文本形式输出观察结果和行动计划。
        """
        logger.info("[Agent] 进入思考阶段...")
        
        # 注入临时指令，诱导模型进行思考而非直接回答
        # 注意：这些临时指令不会被存入 state["messages"] 历史，避免干扰后续对话
        thinking_prompt = state["messages"] + [
            HumanMessage(content=(
                "[系统指令：请根据当前对话历史和已获得的工具结果，简要说明你接下来的计划。"
                "如果是准备调用工具，请说明原因。如果是准备总结回答，请说明你已拿到足够信息。"
                "请以'【思考】：'开头。这一步禁止尝试调用任何工具。]"
            ))
        ]
        
        # 使用不带工具的原始 LLM，确保它必须通过文本说话
        ai_msg = await self.llm.ainvoke(thinking_prompt)
        
        return {
            "messages": state["messages"] + [ai_msg]
        }

    async def _analyze_node(self, state: Dict):
        """
        [节点 2] 决策节点：
        携带思考后的上下文，正式决定执行工具调用还是给出最终回答。
        """
        logger.info("[Agent] 进入决策阶段...")
        # 使用带工具绑定的模型
        ai_msg = await self.llm_with_tools.ainvoke(state["messages"])
        return {
            "messages": state["messages"] + [ai_msg],
            "loop_count": state.get("loop_count", 0)
        }

    async def _execute_tools_node(self, state: Dict):
        """[节点 3] 工具执行节点"""
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
            "loop_count": state.get("loop_count", 0) + 1 # 计数增加
        }

    def _build_graph(self):
        """
        构建循环工作流：
        Start -> Think -> Analyze --(if tools)--> Execute -> Think ...
                                --(no tools)--> End
        """
        def should_continue(state: Dict):
            last_msg = state["messages"][-1]
            # 如果 Analyze 节点检测到需要工具调用且未超过循环上限
            if getattr(last_msg, 'tool_calls', []) and state.get("loop_count", 0) < 5:
                return "execute_tools"
            return END

        builder = StateGraph(dict)
        
        builder.add_node("think", self._think_node)
        builder.add_node("analyze", self._analyze_node)
        builder.add_node("execute_tools", self._execute_tools_node)
        
        builder.set_entry_point("think")
        builder.add_edge("think", "analyze")
        
        builder.add_conditional_edges(
            "analyze",
            should_continue,
            {
                "execute_tools": "execute_tools",
                END: END
            }
        )
        
        # 执行完工具后再次回到 think 节点，让模型分析工具执行结果
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
        
        # 1. 基础对话模式（不开启 Agent）
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
        
        try:
            async for event in self.graph.astream_events(initial_state, version="v2"):
                kind = event.get('event')
                metadata = event.get('metadata', {})
                # 获取当前事件发生的节点和步数，用于前端区分多次循环
                node = metadata.get('langgraph_node', '')
                step = metadata.get('langgraph_step', 0)

                # 处理模型输出流
                if kind == "on_chat_model_stream":
                    chunk = event.get('data', {}).get('chunk')
                    if chunk and chunk.content:
                        print(f"[AgentWrapper] 生成模型输出流: node={node}, step={step}, content={chunk.content[:50]}...")
                        yield {
                            'event': 'on_chat_model_stream',
                            'node': node,   # 节点名：think 或 analyze
                            'step': step,   # 步骤计数
                            'data': {'chunk': {'content': chunk.content}}
                        }
                    
                    # 捕获工具调用片段
                    if chunk and hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
                        print(f"[AgentWrapper] 生成工具调用流: node={node}, step={step}, tool_calls={chunk.tool_call_chunks}")
                        yield {
                            'event': 'on_tool_call_stream',
                            'node': node,
                            'step': step,
                            'data': {'tool_calls': chunk.tool_call_chunks}
                        }

                # 处理工具执行状态
                elif kind == "on_tool_start":
                    yield {
                        'event': 'on_tool_start',
                        'name': event.get('name'),
                        'node': node,   # 添加节点信息
                        'step': step,
                        'data': {'input': event.get('data', {}).get('input', {})}
                    }
                elif kind == "on_tool_end":
                    yield {
                        'event': 'on_tool_end',
                        'name': event.get('name'),
                        'node': node,   # 添加节点信息
                        'step': step,
                        'data': {'output': event.get('data', {}).get('output', {})}
                    }

        except Exception as e:
            logger.error(f"[Agent] Stream Error: {str(e)}")
            yield {"event": "on_node_error", "data": {"error": str(e)}}

    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """将原始字典消息转换为 LangChain 对象"""
        formatted = []
        for msg in messages:
            role, content = msg.get('role', 'user'), msg.get('content', '')
            if role == 'user': formatted.append(HumanMessage(content=content))
            elif role == 'assistant': formatted.append(AIMessage(content=content))
            elif role == 'system': formatted.append(SystemMessage(content=content))
        return formatted

    def __getattr__(self, name):
        return getattr(self.base_model, name)