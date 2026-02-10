#!/usr/bin/env python3
"""
通知设置迁移脚本
将 notification_settings 表中的数据迁移到 system_settings 表中
"""
import os
import sqlite3
from datetime import datetime
from platformdirs import PlatformDirs

# 初始化平台目录管理
dirs = PlatformDirs(appname="Chato", appauthor="Chato")

# 获取数据库路径
def get_db_path():
    """获取数据库路径"""
    # 使用与应用程序相同的方式获取用户数据目录
    user_data_dir = dirs.user_data_dir
    os.makedirs(user_data_dir, exist_ok=True)
    config_dir = os.path.join(user_data_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'chato.db')

# 连接数据库
def connect_db(db_path):
    """连接到数据库"""
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"连接数据库失败: {e}")
        return None

# 检查表是否存在
def check_tables(conn):
    """检查必要的表是否存在"""
    cursor = conn.cursor()
    
    # 检查 notification_settings 表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notification_settings'")
    notification_table_exists = cursor.fetchone() is not None
    
    # 检查 system_settings 表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_settings'")
    system_table_exists = cursor.fetchone() is not None
    
    return notification_table_exists, system_table_exists

# 检查 system_settings 表是否有通知相关字段
def check_system_table_fields(conn):
    """检查 system_settings 表是否有通知相关字段"""
    cursor = conn.cursor()
    
    # 获取表结构
    cursor.execute("PRAGMA table_info(system_settings)")
    columns = cursor.fetchall()
    
    column_names = [col['name'] for col in columns]
    
    # 检查是否有所有必要的通知字段
    required_fields = ['enabled', 'new_message', 'sound', 'system', 'display_time']
    missing_fields = [field for field in required_fields if field not in column_names]
    
    return missing_fields

# 从 notification_settings 表读取数据
def read_notification_settings(conn):
    """从 notification_settings 表读取数据"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notification_settings LIMIT 1")
    return cursor.fetchone()

# 检查 system_settings 表是否已有数据
def check_system_settings_data(conn):
    """检查 system_settings 表是否已有数据"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM system_settings")
    return cursor.fetchone()[0] > 0

# 从 system_settings 表读取数据
def read_system_settings(conn):
    """从 system_settings 表读取数据"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_settings LIMIT 1")
    return cursor.fetchone()

# 更新 system_settings 表，添加通知设置
def update_system_settings(conn, notification_data, system_data):
    """更新 system_settings 表，添加通知设置"""
    cursor = conn.cursor()
    
    # 构建更新语句
    update_sql = '''
        UPDATE system_settings SET 
            enabled = ?, 
            new_message = ?, 
            sound = ?, 
            system = ?, 
            display_time = ?
        WHERE id = ?
    '''
    
    # 执行更新
    cursor.execute(update_sql, (
        notification_data['enabled'],
        notification_data['new_message'],
        notification_data['sound'],
        notification_data['system'],
        notification_data['display_time'],
        system_data['id']
    ))
    
    conn.commit()
    print("系统设置表更新成功")

# 插入新的 system_settings 记录，包含通知设置
def insert_system_settings(conn, notification_data):
    """插入新的 system_settings 记录，包含通知设置"""
    cursor = conn.cursor()
    
    # 构建插入语句
    insert_sql = '''
        INSERT INTO system_settings (
            dark_mode, font_size, font_family, language, auto_scroll,
            show_timestamps, confirm_delete, streaming_enabled, chat_style_document,
            view_mode, default_model, rag_view_mode, enabled, new_message, sound, system, display_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    # 执行插入
    cursor.execute(insert_sql, (
        False,  # dark_mode
        16,     # font_size
        "Inter, system-ui, sans-serif",  # font_family
        "zh-CN",  # language
        True,   # auto_scroll
        True,   # show_timestamps
        True,   # confirm_delete
        True,   # streaming_enabled
        False,  # chat_style_document
        "grid",  # view_mode
        "",     # default_model
        True,   # rag_view_mode
        # 通知设置
        notification_data['enabled'],
        notification_data['new_message'],
        notification_data['sound'],
        notification_data['system'],
        notification_data['display_time']
    ))
    
    conn.commit()
    print("系统设置表插入成功")

# 主迁移函数
def main():
    """主迁移函数"""
    print("=" * 60)
    print(f"通知设置迁移脚本")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取数据库路径
    db_path = get_db_path()
    print(f"数据库路径: {db_path}")
    
    # 连接数据库
    conn = connect_db(db_path)
    if not conn:
        return
    
    try:
        # 检查必要的表
        notification_table_exists, system_table_exists = check_tables(conn)
        
        if not notification_table_exists:
            print("错误: notification_settings 表不存在")
            return
        
        if not system_table_exists:
            print("错误: system_settings 表不存在")
            return
        
        # 检查 system_settings 表字段
        missing_fields = check_system_table_fields(conn)
        if missing_fields:
            print(f"错误: system_settings 表缺少字段: {missing_fields}")
            print("请先运行应用程序，让 SQLAlchemy 自动创建字段")
            return
        
        # 从 notification_settings 表读取数据
        notification_data = read_notification_settings(conn)
        if not notification_data:
            print("通知设置表中没有数据，跳过迁移")
            return
        
        print("从通知设置表读取到的数据:")
        print(f"  enabled: {notification_data['enabled']}")
        print(f"  new_message: {notification_data['new_message']}")
        print(f"  sound: {notification_data['sound']}")
        print(f"  system: {notification_data['system']}")
        print(f"  display_time: {notification_data['display_time']}")
        
        # 检查 system_settings 表是否已有数据
        system_data_exists = check_system_settings_data(conn)
        
        if system_data_exists:
            # 读取现有数据
            system_data = read_system_settings(conn)
            print("\n系统设置表已有数据，将更新现有记录")
            update_system_settings(conn, notification_data, system_data)
        else:
            print("\n系统设置表无数据，将插入新记录")
            insert_system_settings(conn, notification_data)
        
        print("\n" + "=" * 60)
        print("通知设置迁移完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"迁移过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
