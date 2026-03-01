import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Literal
from langchain_core.messages import (
    BaseMessage, SystemMessage, ToolMessage, AIMessage
)
from langgraph.graph import END

from app.llm.agent.agent_state import AgentState
from app.llm.agent.tool_manager import ToolManager
from app.core.logging_config import logger


class AgentNodes:
    """智能体节点逻辑集合：支持线性/非线性自动分流"""
    
    def __init__(self, llm_with_tools, tool_manager: ToolManager):
        self.llm_with_tools = llm_with_tools
        self.tool_manager = tool_manager

    async def reasoning_node(self, state: AgentState) -> Dict[str, Any]:
        """核心推理节点：决定行动方案"""
        logger.info(f"[Agent] 正在进行第 {state['loop_count']+1} 轮推理...")
        logger.debug(f"[Agent] reasoning_node 输入消息: {[msg.content[:10000] + '...' if len(msg.content) > 1000 else msg.content for msg in state['messages']]}")
        
        from app.utils.prompt_manager import prompt_manager
        agent_message = prompt_manager.get_system_message(mode='agent')
        base_system_prompt = agent_message['content']
        
        # 核心改进：明确告知模型如何处理任务依赖
        agent_specific_prompt = (
            "\n\n### 任务执行规范：\n"
            "1. **并行执行**：如果多个工具调用互不干扰，请同时输出它们。\n"
            "2. **线性执行（依赖）**：如果工具B依赖工具A的结果，请在工具B的参数中使用 '{{tool_N}}' 作为占位符。"
            "例如：工具0返回了用户ID，工具1需要该ID，则工具1参数写为：'user_id': '{{tool_0}}'。\n"
            "3. **思考流程**：始终先在 <thought> 标签内分析逻辑，再输出工具调用或最终回答。"
        )
        
        system_prompt = base_system_prompt + agent_specific_prompt
        
        # 创建消息副本，避免修改原始状态
        msgs = state["messages"].copy()
        if not any(isinstance(m, SystemMessage) for m in msgs):
            msgs = [SystemMessage(content=system_prompt)] + msgs

        response = await self.llm_with_tools.ainvoke(msgs)
        
        # 只返回新生成的消息，让 LangGraph 通过 operator.add 自动累加
        return {
            "messages": [response],
            "loop_count": state["loop_count"]
        }

    async def execute_linear_node(self, state: AgentState) -> Dict[str, Any]:
        """线性任务节点：支持【结果动态注入】的顺序执行"""
        last_msg = state["messages"][-1]
        tool_calls = getattr(last_msg, 'tool_calls', [])
        
        results = []
        # 维护一个当前轮次的工具执行结果映射表
        execution_context = {}
        
        logger.info(f"[Agent] 进入线性执行模式，共 {len(tool_calls)} 个任务")
        logger.debug(f"[Agent] execute_linear_node 输入消息: {[msg.content[:1000] + '...' if len(msg.content) > 1000 else msg.content for msg in state['messages']]}")

        for i, tc in enumerate(tool_calls):
            # 1. 动态注入：将之前工具的结果替换到当前参数中
            original_args = tc.get('args', {})
            injected_args = self._inject_variables(original_args, execution_context)
            tc['args'] = injected_args
            
            # 2. 执行工具
            result_msg = await self.tool_manager.run_tool(tc, tool_index=i)
            results.append(result_msg)
            
            # 3. 更新上下文：存入 tool_0, tool_1 等供后续引用
            execution_context[f"tool_{i}"] = result_msg.content
            
        # 只返回新生成的消息，让 LangGraph 通过 operator.add 自动累加
        return {
            "messages": results,
            "loop_count": state["loop_count"] + 1
        }

    async def execute_nonlinear_node(self, state: AgentState) -> Dict[str, Any]:
        """非线性任务节点：真正的并发并行执行"""
        last_msg = state["messages"][-1]
        tool_calls = getattr(last_msg, 'tool_calls', [])
        
        logger.info(f"[Agent] 进入非线性模式，并行执行 {len(tool_calls)} 个任务")
        logger.debug(f"[Agent] execute_nonlinear_node 输入消息: {[msg.content[:1000] + '...' if len(msg.content) > 1000 else msg.content for msg in state['messages']]}")
        
        tasks = []
        for i, tc in enumerate(tool_calls):
            tasks.append(self.tool_manager.run_tool(tc, tool_index=i))
        
        results = await asyncio.gather(*tasks)
        
        # 只返回新生成的消息，让 LangGraph 通过 operator.add 自动累加
        return {
            "messages": results,
            "loop_count": state["loop_count"] + 1
        }

    def _inject_variables(self, args: Dict, context: Dict) -> Dict:
        """将参数中的占位符 {{tool_N}} 替换为 context 中的实际值"""
        if not context:
            return args
        
        # 将 Dict 转为字符串进行全局替换，处理嵌套结构
        args_str = json.dumps(args, ensure_ascii=False)
        
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            if placeholder in args_str:
                # 如果结果是简单的字符串，直接替换；如果是复杂对象，可以考虑更复杂的逻辑
                # 这里简单处理：将结果转为字符串注入
                args_str = args_str.replace(placeholder, str(value))
        
        return json.loads(args_str)

    def should_continue(self, state: AgentState) -> Literal["execute_linear", "execute_nonlinear", "end"]:
        """决策路由：根据任务特征分流执行路径"""
        logger.debug(f"[Agent] should_continue 输入消息: {[msg.content[:1000] + '...' if len(msg.content) > 1000 else msg.content for msg in state['messages']]}")
        # 从后往前查找，找到最近的包含 tool_calls 的消息（即 reasoning_node 产生的决策）
        tool_calls_msg = None
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_calls_msg = msg
                break
        
        # 如果找不到包含 tool_calls 的消息，或者循环次数达到上限，返回 end
        if not tool_calls_msg or state["loop_count"] >= 10:
            return "end"
        
        tool_calls = tool_calls_msg.tool_calls

        # 判断是否需要线性执行
        # 场景1：只有一个工具调用 -> 线性执行即可
        if len(tool_calls) == 1:
            return "execute_linear"
        
        # 场景2：检查工具参数中是否存在 {{tool_N}} 占位符引用
        has_dependency = False
        for tc in tool_calls:
            args_str = json.dumps(tc.get('args', {}))
            if re.search(r"\{\{tool_\d+\}\}", args_str):
                has_dependency = True
                break
        
        if has_dependency:
            return "execute_linear"
        
        # 场景3：无依赖且有多个调用 -> 并行执行
        return "execute_nonlinear"

    async def reflect_node(self, state: AgentState) -> Dict[str, Any]:
        """反思节点：提取关键信息并评估任务完成度"""
        logger.info(f"[Agent] 正在进行结果反思...")
        logger.debug(f"[Agent] reflect_node 输入消息: {[msg.content[:1000] + '...' if len(msg.content) > 1000 else msg.content for msg in state['messages']]}")
        
        tool_results = []
        for msg in reversed(state["messages"]):
            if isinstance(msg, ToolMessage):
                tool_results.append(msg)
            elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                break
        
        if tool_results:
            reflection_content = self._analyze_tool_results(tool_results)
            reflection_msg = AIMessage(
                content=f"<reflection>\n{reflection_content}\n</reflection>"
            )
            # 只返回新生成的消息，让 LangGraph 通过 operator.add 自动累加
            return {"messages": [reflection_msg], "loop_count": state["loop_count"]}
        
        return {"messages": [], "loop_count": state["loop_count"]}

    def _analyze_tool_results(self, tool_results: List[ToolMessage]) -> str:
        """分析工具执行结果的内部逻辑（保持原逻辑，可按需微调）"""
        # ... 原有的结果统计代码 ...
        success_count = sum(1 for r in tool_results if "error" not in r.content.lower())
        return f"本轮成功执行 {success_count}/{len(tool_results)} 个工具，信息{'已更新' if success_count > 0 else '获取失败'}。"