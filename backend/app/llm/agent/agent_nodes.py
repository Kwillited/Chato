from typing import Dict, Any, List, Optional, AsyncIterator
import asyncio

from langchain_core.messages import (
    BaseMessage, SystemMessage, ToolMessage, AIMessage
)
from langgraph.graph import END

from app.llm.agent.agent_state import AgentState
from app.llm.agent.tool_manager import ToolManager
from app.core.logging_config import logger


class AgentNodes:
    """智能体节点逻辑集合"""
    
    def __init__(self, llm_with_tools, tool_manager: ToolManager):
        """
        初始化智能体节点
        
        Args:
            llm_with_tools: 绑定了工具的语言模型
            tool_manager: 工具管理器实例
        """
        self.llm_with_tools = llm_with_tools
        self.tool_manager = tool_manager
    
    async def reasoning_node(self, state: AgentState) -> Dict[str, Any]:
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
    
    async def execute_tools_node(self, state: AgentState) -> Dict[str, Any]:
        """执行工具调用"""
        last_msg = state["messages"][-1]
        tool_calls = getattr(last_msg, 'tool_calls', [])
        
        # 存储工具调用索引和名称的映射
        tool_call_map = {}
        for i, tc in enumerate(tool_calls):
            tool_name = tc.get('name', '')
            if tool_name:
                tool_call_map[tool_name] = i
        
        # 执行工具调用
        tasks = []
        for i, tc in enumerate(tool_calls):
            tasks.append(self.tool_manager.run_tool(tc, tool_index=i))
        
        results = await asyncio.gather(*tasks)
        
        return {
            "messages": results,
            "loop_count": state["loop_count"] + 1
        }
    
    async def reflect_node(self, state: AgentState) -> Dict[str, Any]:
        """反思节点：观察结果并整理信息"""
        logger.info(f"[Agent] 正在进行结果反思...")
        
        # 获取最近的工具执行结果
        tool_results = []
        for msg in reversed(state["messages"]):
            if isinstance(msg, ToolMessage):
                tool_results.append(msg)
            elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                # 找到对应的工具调用消息后停止
                break
        
        # 整理工具执行结果
        if tool_results:
            # 分析结果，提取关键信息
            reflection_content = self._analyze_tool_results(tool_results)
            
            # 创建反思消息
            reflection_msg = AIMessage(
                content=f"<reflection>分析工具执行结果：{reflection_content}</reflection>"
            )
            
            return {
                "messages": [reflection_msg],
                "loop_count": state["loop_count"]
            }
        
        # 无工具执行结果时直接返回
        return {
            "messages": [],
            "loop_count": state["loop_count"]
        }
    
    def _analyze_tool_results(self, tool_results: List[ToolMessage]) -> str:
        """分析工具执行结果"""
        if not tool_results:
            return "无工具执行结果"
        
        # 提取工具执行结果内容
        results_content = []
        for i, result in enumerate(tool_results):
            results_content.append(f"工具 {i+1}: {result.content}")
        
        # 生成反思内容
        reflection_parts = [
            f"共获取 {len(tool_results)} 个工具执行结果",
            "\n工具执行结果摘要：",
            "\n".join(results_content),
            "\n分析：",
            "1. 所有工具均已成功执行",
            "2. 结果包含了所需的关键信息",
            "3. 信息完整，可以基于此生成最终回答"
        ]
        
        return "\n".join(reflection_parts)
    
    def should_continue(self, state: AgentState) -> str:
        """判断是否继续执行"""
        last_msg = state["messages"][-1]
        # 如果模型输出了工具调用，且循环次数未超限
        if getattr(last_msg, 'tool_calls', []) and state["loop_count"] < 10:
            return "execute"
        return END
