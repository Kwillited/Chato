"""测试RAG模式下的系统消息获取问题"""
from app.utils.prompt_manager import prompt_manager
from app.utils.message_builder import MessageBuilder

# 测试1：模拟RAG模式但context_docs为空
print("=== 测试1：RAG模式但context_docs为空 ===")
system_msg_rag_empty = prompt_manager.get_system_message(mode='rag', context_docs=None)
print(f"系统消息内容: {system_msg_rag_empty['content'][:100]}...")
print(f"使用的是: {'rag_system_message' if '基于检索增强' in system_msg_rag_empty['content'] else 'system_message'}")

# 测试2：模拟RAG模式且context_docs不为空
print("\n=== 测试2：RAG模式且context_docs不为空 ===")
test_context = [{'content': '测试文档内容1'}, {'content': '测试文档内容2'}]
system_msg_rag_with_context = prompt_manager.get_system_message(mode='rag', context_docs=test_context)
print(f"系统消息内容: {system_msg_rag_with_context['content'][:100]}...")
print(f"使用的是: {'rag_system_message' if '基于检索增强' in system_msg_rag_with_context['content'] else 'system_message'}")

# 测试3：使用MessageBuilder.build_rag_messages，context_docs为空
print("\n=== 测试3：MessageBuilder.build_rag_messages，context_docs为空 ===")
try:
    messages_rag_empty = MessageBuilder.build_rag_messages("测试问题", context_docs=[])
    for msg in messages_rag_empty:
        if msg['role'] == 'system':
            print(f"系统消息内容: {msg['content'][:100]}...")
            print(f"使用的是: {'rag_system_message' if '基于检索增强' in msg['content'] else 'system_message'}")
except Exception as e:
    print(f"错误: {e}")

# 测试4：使用MessageBuilder.build_rag_messages，context_docs不为空
print("\n=== 测试4：MessageBuilder.build_rag_messages，context_docs不为空 ===")
try:
    messages_rag_with_context = MessageBuilder.build_rag_messages("测试问题", context_docs=test_context)
    for msg in messages_rag_with_context:
        if msg['role'] == 'system':
            print(f"系统消息内容: {msg['content'][:100]}...")
            print(f"使用的是: {'rag_system_message' if '基于检索增强' in msg['content'] else 'system_message'}")
except Exception as e:
    print(f"错误: {e}")
