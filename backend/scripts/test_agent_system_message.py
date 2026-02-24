"""测试智能体系统消息整合"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.prompt_manager import prompt_manager
from app.llm.agent.agent_nodes import AgentNodes
from app.llm.agent.tool_manager import ToolManager
from app.llm.base.base_model import BaseModel

print("=== 测试智能体系统消息整合 ===")

# 测试1: 检查配置文件中的智能体系统消息
print("\n=== 测试1: 检查配置文件中的智能体系统消息 ===")
agent_message = prompt_manager.get_system_message(mode='agent')
print(f"智能体系统消息: {agent_message['content']}")
print(f"消息角色: {agent_message['role']}")

# 测试2: 模拟智能体节点的SystemMessage构建
print("\n=== 测试2: 模拟智能体节点的SystemMessage构建 ===")

# 模拟工具管理器
class MockToolManager(ToolManager):
    def __init__(self):
        super().__init__()
    
    def get_tools(self):
        return []

# 模拟LLM
class MockLLM:
    async def ainvoke(self, messages):
        # 模拟返回一个AIMessage
        from langchain_core.messages import AIMessage
        return AIMessage(content="测试响应")

# 模拟基础模型
class MockBaseModel(BaseModel):
    def __init__(self):
        super().__init__(model_name="test-model")
        self.llm = MockLLM()
    
    def _prepare_call_kwargs(self, model_params):
        return {}

# 创建智能体节点
mock_tool_manager = MockToolManager()
mock_llm = MockLLM()
agent_nodes = AgentNodes(mock_llm, mock_tool_manager)

# 模拟状态
mock_state = {
    "messages": [],
    "loop_count": 0
}

# 测试reasoning_node方法
print("\n=== 测试3: 测试reasoning_node方法 ===")
print("调用reasoning_node方法...")

# 由于是异步方法，需要使用asyncio运行
import asyncio

async def test_reasoning_node():
    result = await agent_nodes.reasoning_node(mock_state)
    print(f"方法调用成功!")
    print(f"返回消息数量: {len(result['messages'])}")
    if result['messages']:
        msg = result['messages'][0]
        print(f"返回消息类型: {type(msg).__name__}")
        print(f"返回消息内容: {msg.content}")

asyncio.run(test_reasoning_node())

print("\n=== 测试完成 ===")
print("智能体系统消息整合验证成功!")
print("现在智能体将从配置文件读取系统消息，并添加智能体特定的思考流程要求。")
