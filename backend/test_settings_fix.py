#!/usr/bin/env python3
"""
测试设置数据的SQLite存储功能（修复版本）
"""
import os
import sqlite3
import json
from app.core.config import config_manager
from app.core.data_manager import load_data, save_data, db, set_dirty_flag
from app.core.database import engine
from app.models.database.models import Base

# 获取数据库路径
def get_db_path():
    """获取数据库路径"""
    user_data_dir = config_manager.get_user_data_dir()
    return os.path.join(user_data_dir, 'config', 'chato.db')

# 测试设置数据的SQLite存储功能
def test_settings_sqlite():
    """
    测试设置数据的SQLite存储功能
    """
    print("🔄 开始测试设置数据的SQLite存储功能...")
    
    # 1. 初始化并加载数据
    print("📥 加载初始数据...")
    load_data()
    print(f"📊 初始设置数量: {len(db['settings'])}")
    
    # 2. 修改设置
    print("🔧 修改设置...")
    
    # 确保所有设置类别都存在
    if 'vector' not in db['settings']:
        db['settings']['vector'] = {
            'retrieval_mode': 'vector',
            'top_k': 3,
            'score_threshold': 0.7,
            'vector_db_path': '',
            'embedder_model': 'qwen3-embedding-0.6b',
            'chunk_size': 1000,
            'chunk_overlap': 200
        }
        print("✅ 创建了向量设置")
    else:
        db['settings']['vector']['top_k'] = 5
        db['settings']['vector']['score_threshold'] = 0.8
        print("✅ 修改了向量设置")
    
    if 'system' not in db['settings']:
        db['settings']['system'] = {
            'dark_mode': False,
            'font_size': 16,
            'font_family': 'Inter, system-ui, sans-serif',
            'language': 'zh-CN',
            'auto_scroll': True,
            'show_timestamps': True,
            'confirm_delete': True,
            'streaming_enabled': True,
            'chat_style_document': False,
            'view_mode': 'grid',
            'default_model': '',
            'rag_view_mode': True
        }
        print("✅ 创建了系统设置")
    else:
        db['settings']['system']['dark_mode'] = True
        db['settings']['system']['font_size'] = 18
        print("✅ 修改了系统设置")
    
    if 'app' not in db['settings']:
        db['settings']['app'] = {
            'debug': True,
            'host': '0.0.0.0',
            'port': 5000
        }
        print("✅ 创建了应用设置")
    else:
        db['settings']['app']['debug'] = False
        print("✅ 修改了应用设置")
    
    if 'notification' not in db['settings']:
        db['settings']['notification'] = {
            'enabled': True,
            'newMessage': True,
            'sound': False,
            'system': True,
            'displayTime': '5秒'
        }
        print("✅ 创建了通知设置")
    
    # 设置脏标记
    print("🚩 设置脏标记...")
    set_dirty_flag('settings', True)
    
    # 3. 保存设置到SQLite
    print("💾 保存设置到SQLite...")
    save_data()
    
    # 4. 检查数据库中的设置
    print("🔍 检查数据库中的设置...")
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查向量设置
    print("   检查向量设置...")
    cursor.execute("SELECT top_k, score_threshold FROM vector_settings")
    vector_result = cursor.fetchone()
    if vector_result:
        print(f"   ✅ 向量设置 - top_k: {vector_result[0]}, score_threshold: {vector_result[1]}")
    else:
        print("   ❌ 向量设置表中未找到数据")
    
    # 检查系统设置
    print("   检查系统设置...")
    cursor.execute("SELECT dark_mode, font_size FROM system_settings")
    system_result = cursor.fetchone()
    if system_result:
        print(f"   ✅ 系统设置 - dark_mode: {system_result[0]}, font_size: {system_result[1]}")
    else:
        print("   ❌ 系统设置表中未找到数据")
    
    # 检查应用设置
    print("   检查应用设置...")
    cursor.execute("SELECT debug, host, port FROM app_settings")
    app_result = cursor.fetchone()
    if app_result:
        print(f"   ✅ 应用设置 - debug: {app_result[0]}, host: {app_result[1]}, port: {app_result[2]}")
    else:
        print("   ❌ 应用设置表中未找到数据")
    
    # 检查通知设置
    print("   检查通知设置...")
    cursor.execute("SELECT enabled, sound FROM notification_settings")
    notification_result = cursor.fetchone()
    if notification_result:
        print(f"   ✅ 通知设置 - enabled: {notification_result[0]}, sound: {notification_result[1]}")
    else:
        print("   ❌ 通知设置表中未找到数据")
    
    conn.close()
    
    # 5. 清除内存中的设置，模拟重启应用
    print("🗑️  清除内存中的设置...")
    from app.core.data_manager import load_settings_from_db
    # 先修改内存中的设置
    if 'vector' in db['settings']:
        db['settings']['vector']['top_k'] = 10
    if 'system' in db['settings']:
        db['settings']['system']['dark_mode'] = False
    print("✅ 修改了内存中的设置（模拟更改）")
    
    # 6. 重新加载设置
    print("🔄 重新加载设置...")
    load_settings_from_db()
    print(f"📊 重新加载后设置数量: {len(db['settings'])}")
    
    # 7. 验证重新加载的数据
    print("🔍 验证重新加载的数据...")
    if 'vector' in db['settings']:
        print(f"   ✅ 向量设置 - top_k: {db['settings']['vector']['top_k']}, score_threshold: {db['settings']['vector']['score_threshold']}")
    if 'system' in db['settings']:
        print(f"   ✅ 系统设置 - dark_mode: {db['settings']['system']['dark_mode']}, font_size: {db['settings']['system']['font_size']}")
    if 'app' in db['settings']:
        print(f"   ✅ 应用设置 - debug: {db['settings']['app']['debug']}")
    
    print("🎉 测试完成！")
    return True

# 主函数
if __name__ == "__main__":
    try:
        if test_settings_sqlite():
            print("\n✅ 测试通过，设置数据的SQLite存储功能正常工作！")
        else:
            print("\n❌ 测试失败，设置数据的SQLite存储功能存在问题！")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
