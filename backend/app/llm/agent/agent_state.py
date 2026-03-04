from typing import Dict, Any, List, TypedDict, Annotated
import operator

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """智能体状态定义"""
    # messages 允许通过 operator.add 自动累加历史
    messages: Annotated[List[BaseMessage], operator.add]
    # 循环计数
    loop_count: int


class ToolCallInfo(TypedDict):
    """工具调用信息"""
    name: str
    args: Dict[str, Any]
    id: str


class ToolResultInfo(TypedDict):
    """工具执行结果信息"""
    tool_call_id: str
    content: str
    tool_index: int
