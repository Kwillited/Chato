"""测试智能体消息完整处理流程"""
import sys
import os
import json
from datetime import datetime
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.chat.chat_service import ChatService
from app.utils.response_strategy.handler import ResponseHandler

async def test_agent_message_flow():
    """测试智能体消息完整处理流程"""
    print("开始测试智能体消息完整处理流程...")
    
    try:
        # 创建服务实例
        print("1. 创建ChatService实例...")
        chat_service = ChatService()
        print("创建成功")
        
        # 创建测试对话
        print("2. 创建测试对话...")
        chat = chat_service.create_chat("测试智能体消息流程")
        chat_id = chat['id']
        print(f"创建对话成功，ID: {chat_id}")
        
        # 创建用户消息
        print("3. 创建用户消息...")
        now = datetime.now().isoformat()
        user_message = {
            'id': str(uuid.uuid4()),
            'role': 'user',
            'content': '天气怎么样？',
            'createdAt': now,
            'model': None,
            'files': []
        }
        print(f"创建用户消息成功，ID: {user_message['id']}")
        
        # 准备智能体消息处理参数
        print("4. 准备智能体消息处理参数...")
        message_text = user_message['content']
        enhanced_question = message_text
        parsed_model_name = 'gpt-4'
        parsed_version_name = 'default'
        model_params = {'temperature': 0.7}
        model_display_name = 'GPT-4'
        use_agent = True
        
        # 使用ResponseHandler处理智能体响应
        print("5. 使用ResponseHandler处理智能体响应...")
        response = await ResponseHandler.handle_streaming_response(
            chat=chat,
            message_text=message_text,
            user_message=user_message,
            now=now,
            enhanced_question=enhanced_question,
            parsed_model_name=parsed_model_name,
            parsed_version_name=parsed_version_name,
            model_params=model_params,
            model_display_name=model_display_name,
            use_agent=use_agent,
            chat_service=chat_service
        )
        
        # 执行生成器，模拟流式响应处理
        if callable(response):
            print("6. 执行生成器，模拟流式响应处理...")
            generator = response()
            async for chunk in generator:
                print(f"   接收到响应块: {chunk[:100]}...")
        
        # 检查消息是否已保存
        print("7. 检查消息是否已保存...")
        saved_chat = chat_service.get_chat(chat_id)
        if not saved_chat:
            print("❌ 获取对话失败")
            return False
        
        print(f"✅ 获取对话成功，消息数量: {len(saved_chat.get('messages', []))}")
        for i, msg in enumerate(saved_chat.get('messages', [])):
            print(f"   消息 {i+1}: role={msg['role']}, type={msg.get('message_type', 'normal')}")
        
        # 检查数据库中是否有智能体消息
        print("8. 检查数据库中是否有智能体消息...")
        messages = chat_service.message_repo.get_messages_by_chat_id(chat_id)
        print(f"✅ 从数据库获取到 {len(messages)} 条消息")
        for i, msg in enumerate(messages):
            print(f"   数据库消息 {i+1}: role={msg.role}, type={msg.message_type}")
        
        # 检查智能体会话是否已创建
        print("9. 检查智能体会话是否已创建...")
        sessions = chat_service.get_agent_sessions_by_chat_id(chat_id)
        print(f"✅ 获取到 {len(sessions)} 个智能体会话")
        for i, session in enumerate(sessions):
            print(f"   智能体会话 {i+1}: ID={session['id']}, node={session['current_node']}")
        
        print("\n🎉 智能体消息完整处理流程测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_agent_message_flow())
    sys.exit(0 if success else 1)
