"""测试删除chat时是否会正确删除对应的agent_session记录"""
import uuid
from datetime import datetime
from app.repositories.chat_repository import ChatRepository
from app.repositories.agent_session_repository import AgentSessionRepository
from app.core.memory_database import memory_db

# 创建Repository实例
chat_repo = ChatRepository()
agent_session_repo = AgentSessionRepository()

print("=== 测试删除chat时是否会正确删除对应的agent_session记录 ===")

# 测试1: 创建一个聊天和对应的智能体会话
print("\n1. 测试创建聊天和智能体会话:")
try:
    # 创建聊天
    chat_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    chat = chat_repo.create_chat(
        chat_id=chat_id,
        title="测试聊天",
        preview="这是一个测试聊天",
        created_at=now,
        updated_at=now
    )
    print(f"   创建聊天成功: {chat.title} (ID: {chat.id})")
    
    # 创建智能体会话
    session_id = str(uuid.uuid4())
    session = agent_session_repo.create_session(
        session_id=session_id,
        chat_id=chat_id,
        created_at=now,
        updated_at=now,
        graph_state="{\"test\": \"state\"}",
        current_node="start",
        step_count=1
    )
    print(f"   创建智能体会话成功: (ID: {session.id}, Chat ID: {session.chat_id})")
    
    # 验证智能体会话是否创建成功
    sessions = agent_session_repo.get_sessions_by_chat_id(chat_id)
    print(f"   验证: 获取到 {len(sessions)} 个智能体会话")
except Exception as e:
    print(f"   错误: {e}")

# 测试2: 删除聊天并验证智能体会话是否也被删除
print("\n2. 测试删除聊天:")
try:
    # 删除聊天
    success = chat_repo.delete_chat(chat_id)
    print(f"   删除聊天: {'成功' if success else '失败'}")
    
    # 验证智能体会话是否也被删除
    sessions = agent_session_repo.get_sessions_by_chat_id(chat_id)
    print(f"   验证智能体会话: 获取到 {len(sessions)} 个智能体会话")
    
    if len(sessions) == 0:
        print("   ✓ 成功: 删除聊天时智能体会话也被正确删除")
    else:
        print("   ✗ 失败: 删除聊天时智能体会话没有被删除")
        for session in sessions:
            print(f"     残留的智能体会话: ID={session.id}, Chat ID={session.chat_id}")
except Exception as e:
    print(f"   错误: {e}")

# 测试3: 测试批量删除所有聊天
print("\n3. 测试批量删除所有聊天:")
try:
    # 重新创建一个聊天和智能体会话
    chat_id2 = str(uuid.uuid4())
    now = datetime.now().isoformat()
    chat2 = chat_repo.create_chat(
        chat_id=chat_id2,
        title="测试聊天2",
        preview="这是第二个测试聊天",
        created_at=now,
        updated_at=now
    )
    print(f"   创建聊天成功: {chat2.title} (ID: {chat2.id})")
    
    session_id2 = str(uuid.uuid4())
    session2 = agent_session_repo.create_session(
        session_id=session_id2,
        chat_id=chat_id2,
        created_at=now,
        updated_at=now
    )
    print(f"   创建智能体会话成功: (ID: {session2.id}, Chat ID: {session2.chat_id})")
    
    # 批量删除所有聊天
    success = chat_repo.delete_all_chats()
    print(f"   批量删除所有聊天: {'成功' if success else '失败'}")
    
    # 验证所有智能体会话是否也被删除
    all_sessions = agent_session_repo.get_all_sessions()
    print(f"   验证所有智能体会话: 获取到 {len(all_sessions)} 个智能体会话")
    
    if len(all_sessions) == 0:
        print("   ✓ 成功: 批量删除聊天时所有智能体会话也被正确删除")
    else:
        print("   ✗ 失败: 批量删除聊天时智能体会话没有被完全删除")
        for session in all_sessions:
            print(f"     残留的智能体会话: ID={session.id}, Chat ID={session.chat_id}")
except Exception as e:
    print(f"   错误: {e}")

print("\n=== 测试完成 ===")
