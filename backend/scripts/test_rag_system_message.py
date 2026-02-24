"""测试RAG模式下的系统消息读取功能"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.chat.chat_service import ChatService

# 创建ChatService实例
chat_service = ChatService()

# 测试1: 普通模式
print("=== 测试1: 普通模式 ===")
chat_id = "test_chat_id"
enhanced_question = "测试问题"

messages_normal = chat_service._prepare_messages_for_model(chat_id, enhanced_question)

print("生成的消息列表:")
for i, msg in enumerate(messages_normal):
    print(f"消息 {i}:")
    print(f"  角色: {msg['role']}")
    print(f"  内容: {msg['content']}")
    print()

# 检查是否包含系统消息
has_system_message = any(msg['role'] == 'system' for msg in messages_normal)
print(f"是否包含系统消息: {has_system_message}")

if has_system_message:
    system_message = next(msg for msg in messages_normal if msg['role'] == 'system')
    print(f"系统消息内容: {system_message['content']}")

# 测试2: RAG模式
print("\n=== 测试2: RAG模式 ===")

# 模拟RAG上下文文档
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

messages_rag = chat_service._prepare_messages_for_model(
    chat_id, 
    enhanced_question, 
    rag_enabled=True, 
    context_docs=context_docs
)

print("生成的消息列表:")
for i, msg in enumerate(messages_rag):
    print(f"消息 {i}:")
    print(f"  角色: {msg['role']}")
    print(f"  内容: {msg['content']}")
    print()

# 检查是否包含系统消息
has_system_message = any(msg['role'] == 'system' for msg in messages_rag)
print(f"是否包含系统消息: {has_system_message}")

if has_system_message:
    system_message = next(msg for msg in messages_rag if msg['role'] == 'system')
    print(f"系统消息内容: {system_message['content']}")
    # 检查系统消息是否包含RAG上下文
    has_context = any(doc['content'] in system_message['content'] for doc in context_docs)
    print(f"系统消息是否包含RAG上下文: {has_context}")

print("\n测试完成!")
