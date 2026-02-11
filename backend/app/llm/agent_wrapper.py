import asyncio
import json
from typing import Dict, Any, List, Optional, AsyncIterator

from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, SystemMessage
)
from langgraph.graph import StateGraph, END

from app.llm.base.base_model import BaseModel
from app.llm.agent.agent_state import AgentState
from app.llm.agent.agent_nodes import AgentNodes
from app.llm.agent.tool_manager import ToolManager
from app.core.logging_config import logger


class AgentWrapper:
    """智能体包装器"""
    
    def __init__(self, base_model: BaseModel):
        """
        初始化智能体包装器
        
        Args:
            base_model: 基础模型实例
        """
        self.base_model = base_model
        self.llm = base_model.llm
        self.llm_with_tools = None
        self.graph = None
        self.is_initialized = False
        self.tool_manager = ToolManager()
        self.agent_nodes = None
    
    async def initialize(self, mcp_config: Optional[Dict] = None):
        """
        初始化智能体
        
        Args:
            mcp_config: MCP 配置
        """
        if self.is_initialized:
            return
        
        # 初始化工具管理器
        await self.tool_manager.initialize(mcp_config)
        tools = self.tool_manager.get_tools()
        
        # 绑定工具：通用智能体需要工具定义来做推理和决策
        self.llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm
        
        # 初始化智能体节点
        self.agent_nodes = AgentNodes(self.llm_with_tools, self.tool_manager)
        
        # 构建图
        self.graph = self._build_graph()
        self.is_initialized = True
    
    def _build_graph(self):
        """
        构建智能体状态图
        
        Returns:
            编译后的状态图
        """
        builder = StateGraph(AgentState)
        builder.add_node("reasoning", self.agent_nodes.reasoning_node)
        builder.add_node("execute", self.agent_nodes.execute_tools_node)
        builder.add_node("reflect", self.agent_nodes.reflect_node)
        
        builder.set_entry_point("reasoning")
        builder.add_conditional_edges("reasoning", self.agent_nodes.should_continue, {
            "execute": "execute",
            END: END
        })
        builder.add_edge("execute", "reflect")
        builder.add_edge("reflect", "reasoning")
        
        return builder.compile()
    
    async def chat_stream(
        self, 
        messages: List[Dict[str, str]], 
        model_params: Dict[str, Any], 
        use_agent: bool = True
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        智能体流式聊天接口
        
        Args:
            messages: 消息列表
            model_params: 模型参数字典
            use_agent: 是否使用智能体模式
        
        Yields:
            流式输出的事件
        """
        if not self.is_initialized:
            await self.initialize()

        # 1. 集中处理参数（调用基础模型的钩子）
        call_kwargs = self.base_model._prepare_call_kwargs(model_params)
        
        # 2. 绑定工具时传递处理后的参数
        tools = self.tool_manager.get_tools()
        self.llm_with_tools = self.llm.bind_tools(tools, **call_kwargs) if tools else self.llm
        
        # 3. 重新初始化智能体节点和图
        self.agent_nodes = AgentNodes(self.llm_with_tools, self.tool_manager)
        self.graph = self._build_graph()

        prepared_messages = self._prepare_messages(messages)
        
        # 1. 基础模式
        if not use_agent:
            async for event in self.llm.astream_events(prepared_messages, version="v2", **call_kwargs):
                # 打印原始数据块
                print(f"[AgentWrapper.chat_stream] 原始数据块 (基础模式): type={type(event).__name__}, content={str(event)[:200]}...")
                
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
                # 打印原始数据块
                print(f"[AgentWrapper.chat_stream] 原始数据块 (智能体模式): type={type(event).__name__}, content={str(event)[:200]}...")
                
                kind = event.get('event')
                metadata = event.get('metadata', {})
                node = metadata.get('langgraph_node', '')
                
                # 当节点变化时增加步骤计数
                if node != current_node and node:
                    agent_step += 1
                    current_node = node

                if kind == "on_chat_model_stream":
                    chunk = event.get('data', {}).get('chunk')
                    if chunk:
                        # 提取 reasoning_content
                        reasoning_content = None
                        if hasattr(chunk, 'additional_kwargs') and isinstance(chunk.additional_kwargs, dict):
                            reasoning_content = chunk.additional_kwargs.get('reasoning_content')
                        
                        if chunk.content or reasoning_content is not None:
                            # 重点：此处输出包含 <thought> 标签和 reasoning_content，前端可根据此标签渲染 UI
                            yield {
                                'event': 'on_chat_model_stream',
                                'node': node,
                                'agent_step': agent_step,
                                'data': {
                                    'content': chunk.content,
                                    'reasoning_content': reasoning_content
                                }
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
                    yield {
                        'event': 'on_tool_start',
                        'node': node,
                        'agent_step': agent_step,
                        'name': tool_name,
                        'data': {'input': event.get('data', {}).get('input', {})}
                    }
                elif kind == "on_tool_end":
                    tool_name = event.get('name', '')
                    yield {
                        'event': 'on_tool_end',
                        'node': node,
                        'agent_step': agent_step,
                        'name': tool_name,
                        'data': {'output': event.get('data', {}).get('output', {})}
                    }

        except Exception as e:
            logger.error(f"[Agent] Stream Error: {str(e)}")
            yield {"event": "on_error", "data": str(e)}
    
    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """
        准备消息格式
        
        Args:
            messages: 原始消息列表
        
        Returns:
            格式化后的消息列表
        """
        formatted = []
        for msg in messages:
            role, content = msg.get('role', 'user'), msg.get('content', '')
            if role == 'user':
                formatted.append(HumanMessage(content=content))
            elif role == 'assistant':
                formatted.append(AIMessage(content=content))
            elif role == 'system':
                formatted.append(SystemMessage(content=content))
        return formatted
    
    def __getattr__(self, name):
        """
        代理获取基础模型的属性
        
        Args:
            name: 属性名
        
        Returns:
            基础模型的属性
        """
        return getattr(self.base_model, name)
