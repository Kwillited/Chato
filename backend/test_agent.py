import asyncio
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool

# 启用 reasoning 模式
model = ChatOllama(
    model="qwen3:0.6b",
    reasoning=True,
    temperature=0.7
)

agent = create_agent(
    model=model,
    tools=[],
    system_prompt="你是一个助手"
)

response = agent.invoke({
    "messages": [{"role": "user", "content": "strawberry 这个词有多少个字母 r？"}]
})

# 正确方式：按字典访问
last_message = response["messages"][-1]

print("=" * 50)
print("【调试信息】")
print(f"消息类型: {type(last_message)}")
print(f"是否有 content_blocks 属性: {hasattr(last_message, 'content_blocks')}")
print(f"是否有 additional_kwargs 属性: {hasattr(last_message, 'additional_kwargs')}")
print("=" * 50)
print()

# 方法1：检查是否有 content_blocks
if hasattr(last_message, 'content_blocks') and last_message.content_blocks:
    print("【使用方法1】content_blocks 方式")
    for block in last_message.content_blocks:
        if isinstance(block, dict):
            if block.get("type") == "reasoning":
                print(f"推理过程: {block.get('reasoning', block.get('text', ''))}")
            elif block.get("type") == "text":
                print(f"最终答案: {block.get('text', '')}")
else:
    # 方法2：直接获取 content
    print("【使用方法2】直接 content 方式")
    print(f"直接回答: {last_message.content}")
    
# 方法3：检查 additional_kwargs（Ollama 可能把推理内容放这里）
if hasattr(last_message, 'additional_kwargs'):
    reasoning = last_message.additional_kwargs.get('reasoning')
    if reasoning:
        print(f"【使用方法3】additional_kwargs 方式")
        print(f"推理过程 (additional_kwargs): {reasoning}")
    else:
        print(f"【使用方法3】additional_kwargs 中没有 'reasoning' 字段")
        print(f"additional_kwargs 内容: {last_message.additional_kwargs}")
else:
    print("【使用方法3】对象没有 additional_kwargs 属性")