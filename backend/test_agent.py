import asyncio
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool

# 1. 定义工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    return f"{city}检索失败。"

# 2. 创建 Agent (使用新的 create_agent)
agent = create_agent(
    model=ChatOllama(model="qwen2.5:7b"),  # 使用 Ollama 的 qwen2.5:7b 模型
    tools=[get_weather],
    system_prompt="""你是一个严谨的天气助手。"""
)

# 使用 astream_events 实现事件流
async def run_agent():
    print("=== 原始事件流输出 ===")
    async for event in agent.astream_events(
        {"messages": [("user", "上海天气怎么样？")]},
        version="v2"
    ):
        # 直接打印完整的原始事件
        print(event)
        print()

# 运行异步函数
if __name__ == "__main__":
    asyncio.run(run_agent())