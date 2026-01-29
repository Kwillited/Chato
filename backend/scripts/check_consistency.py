#!/usr/bin/env python3
"""
检查内存数据库和SQLite数据库的一致性
"""
import os
import sys
import sqlite3
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.data_manager import db, load_data, get_db_connection, load_chats_from_db, load_models_from_db, load_settings_from_db
from app.core.logging_config import logger

def check_chat_consistency():
    """检查对话数据一致性"""
    print("\n🔍 检查对话数据一致性...")
    
    # 获取SQLite中的对话数量
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取对话数量
    cursor.execute("SELECT COUNT(*) FROM chats")
    sqlite_chat_count = cursor.fetchone()[0]
    memory_chat_count = len(db['chats'])
    
    print(f"   SQLite对话数量: {sqlite_chat_count}")
    print(f"   内存对话数量: {memory_chat_count}")
    
    if sqlite_chat_count != memory_chat_count:
        print(f"   ❌ 对话数量不一致: SQLite={sqlite_chat_count}, 内存={memory_chat_count}")
        return False
    
    # 检查每条对话的消息数量
    for chat in db['chats']:
        chat_id = chat['id']
        memory_msg_count = len(chat.get('messages', []))
        
        cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,))
        sqlite_msg_count = cursor.fetchone()[0]
        
        if memory_msg_count != sqlite_msg_count:
            print(f"   ❌ 对话 {chat_id} 消息数量不一致: SQLite={sqlite_msg_count}, 内存={memory_msg_count}")
            return False
    
    print("   ✅ 对话数据一致")
    return True

def check_model_consistency():
    """检查模型数据一致性"""
    print("\n🔍 检查模型数据一致性...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取模型数量
    cursor.execute("SELECT COUNT(*) FROM models")
    sqlite_model_count = cursor.fetchone()[0]
    memory_model_count = len(db['models'])
    
    print(f"   SQLite模型数量: {sqlite_model_count}")
    print(f"   内存模型数量: {memory_model_count}")
    
    if sqlite_model_count != memory_model_count:
        print(f"   ❌ 模型数量不一致: SQLite={sqlite_model_count}, 内存={memory_model_count}")
        return False
    
    # 检查每条模型的版本数量
    for model in db['models']:
        model_name = model['name']
        memory_version_count = len(model.get('versions', []))
        
        cursor.execute("SELECT id FROM models WHERE name = ?", (model_name,))
        model_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM model_versions WHERE model_id = ?", (model_id,))
        sqlite_version_count = cursor.fetchone()[0]
        
        if memory_version_count != sqlite_version_count:
            print(f"   ❌ 模型 {model_name} 版本数量不一致: SQLite={sqlite_version_count}, 内存={memory_version_count}")
            return False
    
    print("   ✅ 模型数据一致")
    return True

def check_setting_consistency():
    """检查设置数据一致性"""
    print("\n🔍 检查设置数据一致性...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取设置数量
    cursor.execute("SELECT COUNT(*) FROM settings")
    sqlite_setting_count = cursor.fetchone()[0]
    memory_setting_count = len(db['settings'])
    
    print(f"   SQLite设置数量: {sqlite_setting_count}")
    print(f"   内存设置数量: {memory_setting_count}")
    
    if sqlite_setting_count != memory_setting_count:
        print(f"   ❌ 设置数量不一致: SQLite={sqlite_setting_count}, 内存={memory_setting_count}")
        return False
    
    # 检查每个设置的值
    cursor.execute("SELECT key, value FROM settings")
    sqlite_settings = {row[0]: json.loads(row[1]) if row[1] else None for row in cursor.fetchall()}
    
    for key, memory_value in db['settings'].items():
        if key not in sqlite_settings:
            print(f"   ❌ 设置 {key} 在SQLite中不存在")
            return False
        
        sqlite_value = sqlite_settings[key]
        if memory_value != sqlite_value:
            print(f"   ❌ 设置 {key} 值不一致: SQLite={sqlite_value}, 内存={memory_value}")
            return False
    
    print("   ✅ 设置数据一致")
    return True

def check_all_consistency():
    """检查所有数据一致性"""
    print("📊 开始检查内存数据库和SQLite数据库的一致性")
    print("=" * 60)
    
    # 先加载数据
    print("\n🔄 正在加载数据...")
    load_data()
    
    # 检查各类型数据
    chat_ok = check_chat_consistency()
    model_ok = check_model_consistency()
    setting_ok = check_setting_consistency()
    
    print("\n" + "=" * 60)
    if chat_ok and model_ok and setting_ok:
        print("🎉 所有数据一致！")
        return True
    else:
        print("💥 发现数据不一致问题！")
        return False

def fix_message_consistency():
    """修复消息一致性问题：删除SQLite中存在但内存中不存在的消息"""
    print("\n🔧 正在修复消息一致性问题...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取所有对话ID
    cursor.execute("SELECT id FROM chats")
    chat_ids = [row[0] for row in cursor.fetchall()]
    
    for chat_id in chat_ids:
        # 获取内存中该对话的所有消息ID
        chat = next((c for c in db['chats'] if c['id'] == chat_id), None)
        if not chat:
            continue
        
        memory_msg_ids = {msg['id'] for msg in chat.get('messages', [])}
        
        # 获取SQLite中该对话的所有消息ID
        cursor.execute("SELECT id FROM messages WHERE chat_id = ?", (chat_id,))
        sqlite_msg_ids = {row[0] for row in cursor.fetchall()}
        
        # 找出需要删除的消息ID
        msg_ids_to_delete = sqlite_msg_ids - memory_msg_ids
        
        if msg_ids_to_delete:
            print(f"   删除对话 {chat_id} 中不存在于内存的消息: {len(msg_ids_to_delete)} 条")
            # 批量删除
            for msg_id in msg_ids_to_delete:
                cursor.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
    
    conn.commit()
    conn.close()
    print("   ✅ 消息一致性修复完成")

def fix_model_consistency():
    """修复模型一致性问题"""
    print("\n🔧 正在修复模型一致性问题...")
    
    # 重新加载模型数据
    load_models_from_db()
    print("   ✅ 模型数据重新加载完成")

def fix_chat_consistency():
    """修复对话一致性问题"""
    print("\n🔧 正在修复对话一致性问题...")
    
    # 重新加载对话数据
    load_chats_from_db()
    print("   ✅ 对话数据重新加载完成")

def fix_setting_consistency():
    """修复设置一致性问题"""
    print("\n🔧 正在修复设置一致性问题...")
    
    # 重新加载设置数据
    load_settings_from_db()
    print("   ✅ 设置数据重新加载完成")

def fix_all_consistency():
    """修复所有一致性问题"""
    print("🔧 开始修复数据一致性问题")
    print("=" * 60)
    
    fix_chat_consistency()
    fix_message_consistency()
    fix_model_consistency()
    fix_setting_consistency()
    
    print("\n" + "=" * 60)
    print("🔄 修复后再次检查一致性...")
    return check_all_consistency()

if __name__ == "__main__":
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="检查和修复内存数据库和SQLite数据库的一致性")
    parser.add_argument("--fix", action="store_true", help="修复发现的一致性问题")
    args = parser.parse_args()
    
    # 运行检查
    consistent = check_all_consistency()
    
    # 如果发现不一致且请求修复，则运行修复
    if not consistent and args.fix:
        fix_all_consistency()
    elif not consistent:
        print("\n💡 提示：使用 --fix 参数可以修复发现的一致性问题")
    
    # 退出状态码
    sys.exit(0 if consistent else 1)
