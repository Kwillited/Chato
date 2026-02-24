"""测试系统消息读取功能"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.chat.chat_service import ChatService

# 创建ChatService实例
chat_service = ChatService()

# 测试_prepare_messages_for_model方法
chat_id = "test_chat_id"
enhanced_question = "测试问题"

print("开始测试系统消息读取...")
messages = chat_service._prepare_messages_for_model(chat_id, enhanced_question)

print("\n生成的消息列表:")
for i, msg in enumerate(messages):
    print(f"消息 {i}:")
    print(f"  角色: {msg['role']}")
    print(f"  内容: {msg['content']}")
    print()

# 检查是否包含系统消息
has_system_message = any(msg['role'] == 'system' for msg in messages)
print(f"是否包含系统消息: {has_system_message}")

if has_system_message:
    system_message = next(msg for msg in messages if msg['role'] == 'system')
    print(f"系统消息内容: {system_message['content']}")

print("\n测试完成!")
