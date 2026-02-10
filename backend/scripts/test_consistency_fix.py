#!/usr/bin/env python3
"""
测试内存数据库和SQLite数据库的一致性修复功能
"""
import os
import sys
import sqlite3
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.data_manager import db, load_data, save_data, get_db_connection, set_dirty_flag
from app.core.logging_config import logger

def create_inconsistency():
    """创建数据不一致性"""
    print("\n💥 创建数据不一致性...")
    
    # 获取数据库连接
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. 在SQLite中添加一个不存在于内存的对话
    cursor.execute('''
    INSERT INTO chats (id, title, preview, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?)
    ''', ('fake-chat-123', '伪造对话', '这是一个伪造的对话', datetime.now().isoformat(), datetime.now().isoformat()))
    
    # 2. 在SQLite中添加一条不存在于内存的消息
    cursor.execute('''
    INSERT INTO messages (id, chat_id, role, content, reasoning_content, created_at, model)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('fake-msg-456', 'fake-chat-123', 'user', '伪造消息内容', None, datetime.now().isoformat(), 'OpenAI'))
    
    # 3. 在SQLite中添加一个不存在于内存的模型
    cursor.execute('''
    INSERT INTO models (name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('FakeModel', '伪造模型', False, False, 'fa-fake', 'bg-red-100', 'text-red-600', '', None))
    
    # 4. 在SQLite中添加一个不存在于内存的设置
    cursor.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?)",
        ('fake_setting', json.dumps('fake_value'))
    )
    
    conn.commit()
    conn.close()
    
    print("   ✅ 不一致性创建完成")
    print("   - 添加了伪造对话和消息")
    print("   - 添加了伪造模型")
    print("   - 添加了伪造设置")

def check_inconsistency():
    """检查数据不一致性"""
    print("\n🔍 检查数据不一致性...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查对话数量
    cursor.execute("SELECT COUNT(*) FROM chats")
    sqlite_chat_count = cursor.fetchone()[0]
    memory_chat_count = len(db['chats'])
    print(f"   对话数量 - SQLite: {sqlite_chat_count}, 内存: {memory_chat_count}")
    chat_inconsistent = sqlite_chat_count != memory_chat_count
    
    # 检查模型数量
    cursor.execute("SELECT COUNT(*) FROM models")
    sqlite_model_count = cursor.fetchone()[0]
    memory_model_count = len(db['models'])
    print(f"   模型数量 - SQLite: {sqlite_model_count}, 内存: {memory_model_count}")
    model_inconsistent = sqlite_model_count != memory_model_count
    
    # 检查设置数量
    cursor.execute("SELECT COUNT(*) FROM settings")
    sqlite_setting_count = cursor.fetchone()[0]
    memory_setting_count = len(db['settings'])
    print(f"   设置数量 - SQLite: {sqlite_setting_count}, 内存: {memory_setting_count}")
    setting_inconsistent = sqlite_setting_count != memory_setting_count
    
    conn.close()
    
    return chat_inconsistent or model_inconsistent or setting_inconsistent

def test_consistency_fix():
    """测试一致性修复功能"""
    print("📊 测试内存数据库和SQLite数据库的一致性修复功能")
    print("=" * 60)
    
    # 1. 初始加载数据
    print("\n🔄 初始加载数据...")
    load_data()
    
    # 2. 创建不一致性
    create_inconsistency()
    
    # 3. 检查是否创建了不一致性
    has_inconsistency = check_inconsistency()
    if not has_inconsistency:
        print("\n❌ 未能创建不一致性，测试失败！")
        return False
    
    print("   ✅ 确认存在数据不一致性")
    
    # 4. 设置脏标记并保存数据
    print("\n🔧 修复数据一致性...")
    set_dirty_flag('chats')
    set_dirty_flag('models')
    set_dirty_flag('settings')
    save_data()
    
    # 5. 再次检查一致性
    print("\n🔍 修复后检查一致性...")
    has_inconsistency = check_inconsistency()
    
    if has_inconsistency:
        print("   ❌ 修复失败，仍然存在数据不一致性！")
        return False
    
    print("   ✅ 修复成功，数据一致！")
    return True

if __name__ == "__main__":
    success = test_consistency_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 一致性修复测试通过！")
        sys.exit(0)
    else:
        print("💥 一致性修复测试失败！")
        sys.exit(1)
