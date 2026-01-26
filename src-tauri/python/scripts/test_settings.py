#!/usr/bin/env python3
"""
测试设置数据的SQLite存储功能
"""
import os
import sqlite3
from app.core.config import config_manager
from app.core.data_manager import load_data, save_data, db

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
    test_setting_key = 'test_setting'
    test_setting_value = {
        'key1': 'value1',
        'key2': 123,
        'key3': True
    }
    db['settings'][test_setting_key] = test_setting_value
    print(f"✅ 添加了测试设置: {test_setting_key}")
    
    # 3. 保存设置到SQLite
    print("💾 保存设置到SQLite...")
    save_data()
    
    # 4. 检查数据库中的设置
    print("🔍 检查数据库中的设置...")
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings WHERE key = ?", (test_setting_key,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        print(f"✅ 数据库中找到设置: {result[0]}")
        print(f"   值: {result[1]}")
    else:
        print("❌ 数据库中未找到设置")
        return False
    
    # 5. 清除内存中的设置，模拟重启应用
    print("🗑️  清除内存中的设置...")
    db['settings'].clear()
    print(f"📊 清除后设置数量: {len(db['settings'])}")
    
    # 6. 重新加载设置
    print("🔄 重新加载设置...")
    from app.core.data_manager import load_settings_from_db
    load_settings_from_db()
    print(f"📊 重新加载后设置数量: {len(db['settings'])}")
    
    # 7. 检查设置是否正确加载
    if test_setting_key in db['settings']:
        loaded_value = db['settings'][test_setting_key]
        print(f"✅ 成功加载测试设置: {test_setting_key}")
        print(f"   原始值: {test_setting_value}")
        print(f"   加载值: {loaded_value}")
        
        if loaded_value == test_setting_value:
            print("✅ 设置值完全匹配")
            return True
        else:
            print("❌ 设置值不匹配")
            return False
    else:
        print(f"❌ 未找到测试设置: {test_setting_key}")
        return False

# 主函数
if __name__ == "__main__":
    try:
        if test_settings_sqlite():
            print("🎉 测试通过，设置数据的SQLite存储功能正常工作！")
        else:
            print("❌ 测试失败，设置数据的SQLite存储功能存在问题！")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")