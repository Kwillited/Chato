"""测试删除Chat时是否会正确清理agent_sessions数据"""
import uuid
from datetime import datetime
from app.services.chat.chat_service import ChatService
from app.services.data_service import DataService
from app.core.memory_database import memory_db
from app.core.data_manager import save_data, db

# 创建ChatService实例
chat_service = ChatService()

print("=== 测试删除Chat时是否会正确清理agent_sessions数据 ===")

# 测试1: 创建一个聊天和对应的智能体会话
print("\n1. 测试创建聊天和智能体会话:")
try:
    # 创建聊天
    chat_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    # 创建新对话对象
    new_chat = {
        'id': chat_id,
        'title': '测试聊天',
        'preview': '这是一个测试聊天',
        'createdAt': now,
        'updatedAt': now,
        'messages': []
    }
    
    # 保存到内存数据库
    DataService.add_chat(new_chat)
    print(f"   创建聊天成功: {new_chat['title']} (ID: {new_chat['id']})")
    
    # 创建智能体会话
    session_id = str(uuid.uuid4())
    session = {
        'id': session_id,
        'chat_id': chat_id,
        'created_at': now,
        'updated_at': now,
        'graph_state': '{"test": "state"}',
        'current_node': 'start',
        'step_count': 1
    }
    
    # 保存到内存数据库
    DataService.add_agent_session(session)
    print(f"   创建智能体会话成功: (ID: {session['id']}, Chat ID: {session['chat_id']})")
    
    # 验证数据是否存在
    print(f"   内存中聊天数量: {len(db['chats'])}")
    print(f"   内存中智能体会话数量: {len(db['agent_sessions'])}")
    
    # 验证智能体会话是否创建成功
    sessions = DataService.get_agent_sessions_by_chat_id(chat_id)
    print(f"   验证: 获取到 {len(sessions)} 个智能体会话")
except Exception as e:
    print(f"   错误: {e}")

# 测试2: 删除聊天并验证智能体会话是否也被删除
print("\n2. 测试删除聊天:")
try:
    # 删除聊天
    success = chat_service.delete_chat(chat_id)
    print(f"   删除聊天: {'成功' if success else '失败'}")
    
    # 验证内存中的数据
    print(f"   内存中聊天数量: {len(db['chats'])}")
    print(f"   内存中智能体会话数量: {len(db['agent_sessions'])}")
    
    # 验证智能体会话是否也被删除
    sessions = DataService.get_agent_sessions_by_chat_id(chat_id)
    print(f"   验证智能体会话: 获取到 {len(sessions)} 个智能体会话")
    
    if len(sessions) == 0:
        print("   ✓ 成功: 删除聊天时智能体会话也被正确从内存中删除")
    else:
        print("   ✗ 失败: 删除聊天时智能体会话没有被从内存中删除")
        for session in sessions:
            print(f"     残留的智能体会话: ID={session['id']}, Chat ID={session['chat_id']}")
    
    # 验证脏标记
    from app.core.data_manager import dirty_flags
    print(f"   聊天脏标记: {dirty_flags['chats']}")
    print(f"   智能体会话脏标记: {dirty_flags['agent_sessions']}")
except Exception as e:
    print(f"   错误: {e}")

# 测试3: 执行数据保存并验证SQLite数据库中的数据
print("\n3. 测试数据保存:")
try:
    # 执行数据保存
    print("   执行数据保存...")
    save_data()
    print("   数据保存完成")
    
    # 验证脏标记已清除
    from app.core.data_manager import dirty_flags
    print(f"   聊天脏标记: {dirty_flags['chats']}")
    print(f"   智能体会话脏标记: {dirty_flags['agent_sessions']}")
except Exception as e:
    print(f"   错误: {e}")

# 测试4: 验证发起新对话时不会恢复旧的智能体会话
print("\n4. 测试发起新对话:")
try:
    # 创建新的聊天
    new_chat_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    # 创建新对话对象
    another_chat = {
        'id': new_chat_id,
        'title': '新测试聊天',
        'preview': '这是另一个测试聊天',
        'createdAt': now,
        'updatedAt': now,
        'messages': []
    }
    
    # 保存到内存数据库
    DataService.add_chat(another_chat)
    print(f"   创建新聊天成功: {another_chat['title']} (ID: {another_chat['id']})")
    
    # 验证智能体会话数量
    print(f"   内存中智能体会话数量: {len(db['agent_sessions'])}")
    
    # 验证是否没有旧的智能体会话
    old_sessions = [s for s in db['agent_sessions'] if s['chat_id'] == chat_id]
    if len(old_sessions) == 0:
        print("   ✓ 成功: 发起新对话时没有恢复旧的智能体会话")
    else:
        print("   ✗ 失败: 发起新对话时恢复了旧的智能体会话")
        for session in old_sessions:
            print(f"     恢复的智能体会话: ID={session['id']}, Chat ID={session['chat_id']}")
except Exception as e:
    print(f"   错误: {e}")

# 测试5: 测试清空所有聊天
print("\n5. 测试清空所有聊天:")
try:
    # 清空所有聊天
    success = chat_service.delete_all_chats()
    print(f"   清空所有聊天: {'成功' if success else '失败'}")
    
    # 验证内存中的数据
    print(f"   内存中聊天数量: {len(db['chats'])}")
    print(f"   内存中智能体会话数量: {len(db['agent_sessions'])}")
    
    if len(db['agent_sessions']) == 0:
        print("   ✓ 成功: 清空所有聊天时智能体会话也被正确清空")
    else:
        print("   ✗ 失败: 清空所有聊天时智能体会话没有被清空")
        print(f"     残留的智能体会话数量: {len(db['agent_sessions'])}")
except Exception as e:
    print(f"   错误: {e}")

print("\n=== 测试完成 ===")
