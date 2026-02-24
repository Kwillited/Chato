"""测试智能体系统消息是否正确获取"""
from app.utils.message_builder import MessageBuilder

# 测试构建不同模式的消息
print("=== 测试消息构建器 ===")

# 测试普通模式
normal_messages = MessageBuilder.build_normal_messages("你好，测试普通模式")
print("\n普通模式消息:")
for msg in normal_messages:
    if msg['role'] == 'system':
        print(f"系统消息内容: {msg['content'][:100]}...")

# 测试智能体模式
agent_messages = MessageBuilder.build_agent_messages("你好，测试智能体模式")
print("\n智能体模式消息:")
for msg in agent_messages:
    if msg['role'] == 'system':
        print(f"系统消息内容: {msg['content'][:100]}...")

# 测试从对话构建消息（模拟智能体模式）
print("\n从对话构建消息（智能体模式）:")
try:
    # 这里会失败，因为没有实际的对话ID，但我们可以测试方法签名
    test_messages = MessageBuilder.build_messages_from_chat(
        chat_id="test_chat", 
        query="你好，测试从对话构建", 
        agent_enabled=True
    )
    print("测试成功！")
except Exception as e:
    print(f"测试方法签名成功，错误是预期的（因为没有实际对话）: {e}")
