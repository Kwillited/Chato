"""测试智能体实际获取的SystemMessage"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.prompt_manager import prompt_manager
from app.llm.agent.agent_nodes import AgentNodes
from app.llm.agent.tool_manager import ToolManager

print("=== 测试智能体实际获取的SystemMessage ===")

# 测试1: 直接测试prompt_manager
print("\n=== 测试1: 直接测试prompt_manager ===")
agent_msg = prompt_manager.get_system_message(mode='agent')
print(f"智能体系统消息内容: {agent_msg['content']}")
print(f"消息角色: {agent_msg['role']}")

# 测试2: 模拟智能体节点调用
print("\n=== 测试2: 模拟智能体节点调用 ===")

# 模拟工具管理器
mock_tool_manager = ToolManager()

# 模拟LLM
class MockLLM:
    async def ainvoke(self, messages):
        # 打印接收到的消息
        print("\n接收到的消息:")
        for i, msg in enumerate(messages):
            if hasattr(msg, 'content'):
                print(f"消息 {i} - 角色: {type(msg).__name__}, 内容: {msg.content[:100]}...")
        # 模拟返回
        from langchain_core.messages import AIMessage
        return AIMessage(content="测试响应")

# 创建智能体节点
agent_nodes = AgentNodes(MockLLM(), mock_tool_manager)

# 测试状态
mock_state = {
    "messages": [],
    "loop_count": 0
}

# 调用reasoning_node
import asyncio

async def test_reasoning_node():
    result = await agent_nodes.reasoning_node(mock_state)
    print(f"\n推理节点返回: {result}")

asyncio.run(test_reasoning_node())

print("\n=== 测试完成 ===")
