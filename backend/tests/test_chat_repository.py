"""测试ChatRepository修改后的功能"""
import uuid
from datetime import datetime
from app.repositories.chat_repository import ChatRepository
from app.core.memory_database import memory_db

# 创建ChatRepository实例
chat_repo = ChatRepository()

print("=== 测试ChatRepository修改后的功能 ===")

# 测试1: 获取所有聊天
print("\n1. 测试获取所有聊天:")
try:
    chats = chat_repo.get_all_chats()
    print(f"   获取到 {len(chats)} 个聊天")
    for chat in chats:
        print(f"   - {chat.title} (ID: {chat.id})")
except Exception as e:
    print(f"   错误: {e}")

# 测试2: 创建新聊天
print("\n2. 测试创建新聊天:")
try:
    chat_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    chat = chat_repo.create_chat(
        chat_id=chat_id,
        title="测试聊天",
        preview="这是一个测试聊天",
        created_at=now,
        updated_at=now
    )
    print(f"   创建成功: {chat.title} (ID: {chat.id})")
except Exception as e:
    print(f"   错误: {e}")

# 测试3: 获取指定聊天
print("\n3. 测试获取指定聊天:")
try:
    chats = chat_repo.get_all_chats()
    if chats:
        chat_id = chats[0].id
        chat = chat_repo.get_chat_by_id(chat_id)
        print(f"   获取成功: {chat.title} (ID: {chat.id})")
except Exception as e:
    print(f"   错误: {e}")

# 测试4: 更新聊天
print("\n4. 测试更新聊天:")
try:
    chats = chat_repo.get_all_chats()
    if chats:
        chat_id = chats[0].id
        now = datetime.now().isoformat()
        updated_chat = chat_repo.update_chat(
            chat_id=chat_id,
            title="更新后的测试聊天",
            preview="这是更新后的测试聊天",
            updated_at=now,
            pinned=1
        )
        print(f"   更新成功: {updated_chat.title} (ID: {updated_chat.id})")
        print(f"   置顶状态: {updated_chat.pinned}")
except Exception as e:
    print(f"   错误: {e}")

# 测试5: 验证内存数据库与SQLite同步
print("\n5. 测试内存数据库与SQLite同步:")
try:
    # 从内存数据库获取
    memory_chats = memory_db.get('chats')
    print(f"   内存数据库中有 {len(memory_chats)} 个聊天")
    
    # 刷新内存数据库
    memory_db.refresh('chats')
    refreshed_chats = memory_db.get('chats')
    print(f"   刷新后内存数据库中有 {len(refreshed_chats)} 个聊天")
    
    if len(memory_chats) == len(refreshed_chats):
        print("   同步正常: 内存数据库与SQLite数据一致")
    else:
        print("   同步异常: 内存数据库与SQLite数据不一致")
except Exception as e:
    print(f"   错误: {e}")

# 测试6: 删除聊天
print("\n6. 测试删除聊天:")
try:
    chats = chat_repo.get_all_chats()
    if chats:
        chat_id = chats[-1].id  # 删除最后一个聊天
        success = chat_repo.delete_chat(chat_id)
        if success:
            print(f"   删除成功 (ID: {chat_id})")
        else:
            print(f"   删除失败 (ID: {chat_id})")
        
        # 验证删除后的数据
        chats_after = chat_repo.get_all_chats()
        print(f"   删除后剩余 {len(chats_after)} 个聊天")
except Exception as e:
    print(f"   错误: {e}")

print("\n=== 测试完成 ===")
