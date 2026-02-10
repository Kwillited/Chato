#!/usr/bin/env python3
"""
设置数据迁移脚本
将旧的settings表中的数据迁移到新的独立设置表中
"""
import os
import sqlite3
import json
from datetime import datetime

# 获取数据库路径
def get_db_path():
    """获取数据库路径"""
    # 使用默认的用户数据目录
    user_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Chato')
    return os.path.join(user_data_dir, 'config', 'chato.db')

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

# 检查新表是否存在
def check_new_tables(conn):
    """检查新的设置表是否存在"""
    cursor = conn.cursor()
    
    tables = ['vector_settings', 'notification_settings']
    missing_tables = []
    
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            missing_tables.append(table)
    
    return missing_tables

# 创建新表
def create_new_tables(conn):
    """创建新的设置表"""
    cursor = conn.cursor()
    
    # 创建向量设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vector_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            retrieval_mode TEXT DEFAULT 'vector',
            top_k INTEGER DEFAULT 3,
            score_threshold REAL DEFAULT 0.7,
            vector_db_path TEXT DEFAULT '',
            embedder_model TEXT DEFAULT 'qwen3-embedding-0.6b',
            chunk_size INTEGER DEFAULT 1000,
            chunk_overlap INTEGER DEFAULT 200
        )
    ''')
    
    # 创建通知设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enabled BOOLEAN DEFAULT TRUE,
            new_message BOOLEAN DEFAULT TRUE,
            sound BOOLEAN DEFAULT FALSE,
            system BOOLEAN DEFAULT TRUE,
            display_time TEXT DEFAULT '5秒'
        )
    ''')
    
    conn.commit()
    print("创建新表成功")

# 从旧表读取设置
def read_old_settings(conn):
    """从旧的settings表中读取设置"""
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    return cursor.fetchall()

# 迁移向量设置
def migrate_vector_settings(conn, vector_settings):
    """迁移向量设置"""
    cursor = conn.cursor()
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM vector_settings")
    if cursor.fetchone()[0] > 0:
        print("向量设置表已有数据，跳过迁移")
        return False
    
    # 插入向量设置
    cursor.execute('''
        INSERT INTO vector_settings (
            retrieval_mode, top_k, score_threshold, vector_db_path, 
            embedder_model, chunk_size, chunk_overlap
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        vector_settings.get('retrieval_mode', 'vector'),
        vector_settings.get('top_k', 3),
        vector_settings.get('score_threshold', 0.7),
        vector_settings.get('vector_db_path', ''),
        vector_settings.get('embedder_model', 'qwen3-embedding-0.6b'),
        vector_settings.get('chunk_size', 1000),
        vector_settings.get('chunk_overlap', 200)
    ))
    
    conn.commit()
    print("向量设置迁移成功")
    return True



# 迁移通知设置
def migrate_notification_settings(conn, notification_settings):
    """迁移通知设置"""
    cursor = conn.cursor()
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM notification_settings")
    if cursor.fetchone()[0] > 0:
        print("通知设置表已有数据，跳过迁移")
        return False
    
    # 插入通知设置
    cursor.execute('''
        INSERT INTO notification_settings (
            enabled, new_message, sound, system, display_time
        ) VALUES (?, ?, ?, ?, ?)
    ''', (
        notification_settings.get('enabled', True),
        notification_settings.get('newMessage', True),
        notification_settings.get('sound', False),
        notification_settings.get('system', True),
        notification_settings.get('displayTime', '5秒')
    ))
    
    conn.commit()
    print("通知设置迁移成功")
    return True



# 主迁移函数
def main():
    """主迁移函数"""
    print("=" * 60)
    print(f"设置数据迁移脚本")
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
        # 检查新表是否存在
        missing_tables = check_new_tables(conn)
        if missing_tables:
            print(f"缺少新表: {missing_tables}")
            print("正在创建新表...")
            create_new_tables(conn)
        else:
            print("所有新表已存在")
        
        # 从旧表读取设置
        old_settings = read_old_settings(conn)
        print(f"从旧表读取到 {len(old_settings)} 个设置项")
        
        # 解析设置
        settings_dict = {}
        for setting in old_settings:
            key = setting['key']
            value = setting['value']
            try:
                parsed_value = json.loads(value)
                settings_dict[key] = parsed_value
            except json.JSONDecodeError:
                settings_dict[key] = value
        
        # 迁移各个设置
        print("\n开始迁移设置...")
        
        if 'vector' in settings_dict:
            migrate_vector_settings(conn, settings_dict['vector'])
        

        
        if 'notification' in settings_dict:
            migrate_notification_settings(conn, settings_dict['notification'])
        

        
        print("\n" + "=" * 60)
        print("设置迁移完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"迁移过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()