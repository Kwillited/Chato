"""测试RAG模式完整调用流程"""
from app.utils.prompt_manager import prompt_manager
from app.utils.message_builder import MessageBuilder

# 测试1：直接调用prompt_manager.get_system_message
print("=== 测试1：直接调用prompt_manager.get_system_message ===")

# 测试1.1：RAG模式，context_docs为空
system_msg_rag_empty = prompt_manager.get_system_message(mode='rag', context_docs=None)
print("1.1 RAG模式，context_docs为空:")
print(f"   系统消息内容: {system_msg_rag_empty['content'][:100]}...")
print(f"   使用的是: {'rag_system_message' if '基于检索增强' in system_msg_rag_empty['content'] else 'system_message'}")

# 测试1.2：RAG模式，context_docs为空列表
system_msg_rag_empty_list = prompt_manager.get_system_message(mode='rag', context_docs=[])
print("\n1.2 RAG模式，context_docs为空列表:")
print(f"   系统消息内容: {system_msg_rag_empty_list['content'][:100]}...")
print(f"   使用的是: {'rag_system_message' if '基于检索增强' in system_msg_rag_empty_list['content'] else 'system_message'}")

# 测试1.3：RAG模式，context_docs不为空
test_context = [{'content': '测试文档内容1'}, {'content': '测试文档内容2'}]
system_msg_rag_with_context = prompt_manager.get_system_message(mode='rag', context_docs=test_context)
print("\n1.3 RAG模式，context_docs不为空:")
print(f"   系统消息内容: {system_msg_rag_with_context['content'][:100]}...")
print(f"   使用的是: {'rag_system_message' if '基于检索增强' in system_msg_rag_with_context['content'] else 'system_message'}")

# 测试2：调用MessageBuilder.build_rag_messages
print("\n=== 测试2：调用MessageBuilder.build_rag_messages ===")

# 测试2.1：build_rag_messages，context_docs为空
messages_rag_empty = MessageBuilder.build_rag_messages("测试问题", context_docs=None)
print("2.1 build_rag_messages，context_docs为空:")
for msg in messages_rag_empty:
    if msg['role'] == 'system':
        print(f"   系统消息内容: {msg['content'][:100]}...")
        print(f"   使用的是: {'rag_system_message' if '基于检索增强' in msg['content'] else 'system_message'}")

# 测试2.2：build_rag_messages，context_docs为空列表
messages_rag_empty_list = MessageBuilder.build_rag_messages("测试问题", context_docs=[])
print("\n2.2 build_rag_messages，context_docs为空列表:")
for msg in messages_rag_empty_list:
    if msg['role'] == 'system':
        print(f"   系统消息内容: {msg['content'][:100]}...")
        print(f"   使用的是: {'rag_system_message' if '基于检索增强' in msg['content'] else 'system_message'}")

# 测试2.3：build_rag_messages，context_docs不为空
messages_rag_with_context = MessageBuilder.build_rag_messages("测试问题", context_docs=test_context)
print("\n2.3 build_rag_messages，context_docs不为空:")
for msg in messages_rag_with_context:
    if msg['role'] == 'system':
        print(f"   系统消息内容: {msg['content'][:100]}...")
        print(f"   使用的是: {'rag_system_message' if '基于检索增强' in msg['content'] else 'system_message'}")

# 测试3：调用MessageBuilder.build_messages_from_chat
print("\n=== 测试3：调用MessageBuilder.build_messages_from_chat ===")

# 测试3.1：build_messages_from_chat，rag_enabled=True，context_docs为空
try:
    messages_from_chat_rag_empty = MessageBuilder.build_messages_from_chat(
        chat_id="test_chat", 
        query="测试问题", 
        rag_enabled=True, 
        context_docs=None
    )
    print("3.1 build_messages_from_chat，rag_enabled=True，context_docs为空:")
    for msg in messages_from_chat_rag_empty:
        if msg['role'] == 'system':
            print(f"   系统消息内容: {msg['content'][:100]}...")
            print(f"   使用的是: {'rag_system_message' if '基于检索增强' in msg['content'] else 'system_message'}")
except Exception as e:
    print(f"3.1 错误: {e}")

# 测试3.2：build_messages_from_chat，rag_enabled=True，context_docs为空列表
try:
    messages_from_chat_rag_empty_list = MessageBuilder.build_messages_from_chat(
        chat_id="test_chat", 
        query="测试问题", 
        rag_enabled=True, 
        context_docs=[]
    )
    print("\n3.2 build_messages_from_chat，rag_enabled=True，context_docs为空列表:")
    for msg in messages_from_chat_rag_empty_list:
        if msg['role'] == 'system':
            print(f"   系统消息内容: {msg['content'][:100]}...")
            print(f"   使用的是: {'rag_system_message' if '基于检索增强' in msg['content'] else 'system_message'}")
except Exception as e:
    print(f"3.2 错误: {e}")

# 测试3.3：build_messages_from_chat，rag_enabled=True，context_docs不为空
try:
    messages_from_chat_rag_with_context = MessageBuilder.build_messages_from_chat(
        chat_id="test_chat", 
        query="测试问题", 
        rag_enabled=True, 
        context_docs=test_context
    )
    print("\n3.3 build_messages_from_chat，rag_enabled=True，context_docs不为空:")
    for msg in messages_from_chat_rag_with_context:
        if msg['role'] == 'system':
            print(f"   系统消息内容: {msg['content'][:100]}...")
            print(f"   使用的是: {'rag_system_message' if '基于检索增强' in msg['content'] else 'system_message'}")
except Exception as e:
    print(f"3.3 错误: {e}")

print("\n=== 测试完成 ===")
