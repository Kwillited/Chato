"""测试重构后的提示词系统"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.prompt_manager import prompt_manager
from app.utils.message_builder import MessageBuilder

print("=== 测试重构后的提示词系统 ===")

# 测试1: 测试PromptManager
print("\n=== 测试1: PromptManager ===")

# 测试获取系统消息
print("\n1.1 测试获取普通系统消息:")
system_message = prompt_manager.get_system_message(mode='normal')
print(f"角色: {system_message['role']}")
print(f"内容: {system_message['content']}")

# 测试获取RAG系统消息
print("\n1.2 测试获取RAG系统消息:")
context_docs = [
    {
        'content': '这是第一个文档的内容，包含关于测试的信息。',
        'metadata': {'score': 0.95}
    },
    {
        'content': '这是第二个文档的内容，包含更多关于测试的详细信息。',
        'metadata': {'score': 0.92}
    }
]
rag_system_message = prompt_manager.get_system_message(mode='rag', context_docs=context_docs)
print(f"角色: {rag_system_message['role']}")
print(f"内容: {rag_system_message['content']}")

# 测试构建人类消息
print("\n1.3 测试构建人类消息:")
human_message = prompt_manager.build_human_message(
    query="测试问题",
    chat_history=[
        {'role': 'user', 'content': '你好'}, 
        {'role': 'assistant', 'content': '你好，我是AI助手'}
    ]
)
print(f"角色: {human_message['role']}")
print(f"内容: {human_message['content']}")

# 测试构建完整消息列表
print("\n1.4 测试构建完整消息列表:")
messages = prompt_manager.build_messages(
    query="测试问题",
    context_docs=context_docs,
    chat_history=[
        {'role': 'user', 'content': '你好'}, 
        {'role': 'assistant', 'content': '你好，我是AI助手'}
    ],
    mode='rag'
)
print(f"消息数量: {len(messages)}")
for i, msg in enumerate(messages):
    print(f"\n消息 {i}:")
    print(f"  角色: {msg['role']}")
    print(f"  内容: {msg['content']}")

# 测试2: 测试MessageBuilder
print("\n=== 测试2: MessageBuilder ===")

# 测试构建普通消息
print("\n2.1 测试构建普通消息:")
normal_messages = MessageBuilder.build_normal_messages(
    query="测试问题",
    chat_history=[
        {'role': 'user', 'content': '你好'}, 
        {'role': 'assistant', 'content': '你好，我是AI助手'}
    ]
)
print(f"消息数量: {len(normal_messages)}")
for i, msg in enumerate(normal_messages):
    print(f"\n消息 {i}:")
    print(f"  角色: {msg['role']}")
    print(f"  内容: {msg['content']}")

# 测试构建RAG消息
print("\n2.2 测试构建RAG消息:")
rag_messages = MessageBuilder.build_rag_messages(
    query="测试问题",
    context_docs=context_docs,
    chat_history=[
        {'role': 'user', 'content': '你好'}, 
        {'role': 'assistant', 'content': '你好，我是AI助手'}
    ]
)
print(f"消息数量: {len(rag_messages)}")
for i, msg in enumerate(rag_messages):
    print(f"\n消息 {i}:")
    print(f"  角色: {msg['role']}")
    print(f"  内容: {msg['content']}")

# 测试构建智能体消息
print("\n2.3 测试构建智能体消息:")
agent_messages = MessageBuilder.build_agent_messages(
    query="测试问题",
    chat_history=[
        {'role': 'user', 'content': '你好'}, 
        {'role': 'assistant', 'content': '你好，我是AI助手'}
    ]
)
print(f"消息数量: {len(agent_messages)}")
for i, msg in enumerate(agent_messages):
    print(f"\n消息 {i}:")
    print(f"  角色: {msg['role']}")
    print(f"  内容: {msg['content']}")

print("\n=== 测试完成 ===")
