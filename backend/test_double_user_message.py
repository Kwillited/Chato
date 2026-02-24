"""测试修复双用户消息问题"""
from app.utils.message_builder import MessageBuilder
from app.services.data_service import DataService

# 测试1：模拟对话，包含一条用户消息
print("=== 测试1：模拟对话，包含一条用户消息 ===")

# 创建测试对话
chat_id = "test_chat_1"
test_chat = {
    "id": chat_id,
    "title": "测试对话1",
    "messages": [
        {
            "id": "msg1",
            "role": "user",
            "content": "你好，我是测试用户",
            "createdAt": "2026-02-24T16:00:00"
        }
    ]
}

# 保存测试对话到内存
DataService.add_chat(test_chat)

# 测试构建消息列表
messages = MessageBuilder.build_messages_from_chat(
    chat_id=chat_id,
    query="你是谁？",
    rag_enabled=True
)

print(f"构建的消息数量: {len(messages)}")
for i, msg in enumerate(messages):
    role = msg.get('role', 'unknown')
    content = msg.get('content', '')
    content_preview = content[:50] + ('...' if len(content) > 50 else '')
    print(f"消息{i+1} (role={role}): {content_preview}")

# 测试2：模拟对话，包含多条消息
print("\n=== 测试2：模拟对话，包含多条消息 ===")

# 创建测试对话
chat_id2 = "test_chat_2"
test_chat2 = {
    "id": chat_id2,
    "title": "测试对话2",
    "messages": [
        {
            "id": "msg1",
            "role": "user",
            "content": "你好",
            "createdAt": "2026-02-24T16:00:00"
        },
        {
            "id": "msg2",
            "role": "assistant",
            "content": "你好，我是AI助手",
            "createdAt": "2026-02-24T16:00:01"
        },
        {
            "id": "msg3",
            "role": "user",
            "content": "你是谁？",
            "createdAt": "2026-02-24T16:00:02"
        }
    ]
}

# 保存测试对话到内存
DataService.add_chat(test_chat2)

# 测试构建消息列表
messages2 = MessageBuilder.build_messages_from_chat(
    chat_id=chat_id2,
    query="你能做什么？",
    rag_enabled=True
)

print(f"构建的消息数量: {len(messages2)}")
for i, msg in enumerate(messages2):
    role = msg.get('role', 'unknown')
    content = msg.get('content', '')
    content_preview = content[:50] + ('...' if len(content) > 50 else '')
    print(f"消息{i+1} (role={role}): {content_preview}")

print("\n=== 测试完成 ===")
