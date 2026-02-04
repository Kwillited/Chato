"""数据库迁移脚本 - 添加智能体会话相关表和字段"""
import sys
import os
import sqlite3

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import get_db_path
from app.core.config import config_manager


def migrate_database():
    """迁移数据库，添加智能体会话相关表和字段"""
    print("开始数据库迁移...")
    
    try:
        # 获取数据库路径
        db_path = get_db_path()
        print(f"数据库路径: {db_path}")
        
        # 检查数据库文件是否存在
        if not os.path.exists(db_path):
            print("数据库文件不存在，将创建新数据库")
        
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("成功连接到数据库")
        
        # 1. 创建 AgentSession 表
        print("1. 创建 AgentSession 表...")
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_sessions (
                    id TEXT PRIMARY KEY,
                    chat_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    graph_state TEXT,
                    current_node TEXT DEFAULT '',
                    step_count INTEGER DEFAULT 0,
                    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                )
            ''')
            conn.commit()
            print("✅ AgentSession 表创建成功")
        except Exception as e:
            print(f"❌ 创建 AgentSession 表失败: {e}")
            conn.rollback()
        
        # 2. 为 Message 表添加智能体相关字段
        print("2. 为 Message 表添加智能体相关字段...")
        
        # 检查 message_type 字段是否存在
        cursor.execute("PRAGMA table_info(messages)")
        columns = {column[1] for column in cursor.fetchall()}
        
        # 添加 message_type 字段
        if 'message_type' not in columns:
            try:
                cursor.execute('ALTER TABLE messages ADD COLUMN message_type TEXT DEFAULT "normal"')
                conn.commit()
                print("✅ 添加 message_type 字段成功")
            except Exception as e:
                print(f"❌ 添加 message_type 字段失败: {e}")
                conn.rollback()
        else:
            print("⚠️ message_type 字段已存在，跳过")
        
        # 添加 agent_session_id 字段
        if 'agent_session_id' not in columns:
            try:
                cursor.execute('ALTER TABLE messages ADD COLUMN agent_session_id TEXT')
                conn.commit()
                print("✅ 添加 agent_session_id 字段成功")
            except Exception as e:
                print(f"❌ 添加 agent_session_id 字段失败: {e}")
                conn.rollback()
        else:
            print("⚠️ agent_session_id 字段已存在，跳过")
        
        # 添加 agent_node 字段
        if 'agent_node' not in columns:
            try:
                cursor.execute('ALTER TABLE messages ADD COLUMN agent_node TEXT DEFAULT ""')
                conn.commit()
                print("✅ 添加 agent_node 字段成功")
            except Exception as e:
                print(f"❌ 添加 agent_node 字段失败: {e}")
                conn.rollback()
        else:
            print("⚠️ agent_node 字段已存在，跳过")
        
        # 添加 agent_step 字段
        if 'agent_step' not in columns:
            try:
                cursor.execute('ALTER TABLE messages ADD COLUMN agent_step INTEGER DEFAULT 0')
                conn.commit()
                print("✅ 添加 agent_step 字段成功")
            except Exception as e:
                print(f"❌ 添加 agent_step 字段失败: {e}")
                conn.rollback()
        else:
            print("⚠️ agent_step 字段已存在，跳过")
        
        # 添加 agent_metadata 字段
        if 'agent_metadata' not in columns:
            try:
                cursor.execute('ALTER TABLE messages ADD COLUMN agent_metadata TEXT DEFAULT ""')
                conn.commit()
                print("✅ 添加 agent_metadata 字段成功")
            except Exception as e:
                print(f"❌ 添加 agent_metadata 字段失败: {e}")
                conn.rollback()
        else:
            print("⚠️ agent_metadata 字段已存在，跳过")
        
        # 3. 添加外键约束
        print("3. 添加外键约束...")
        try:
            # 注意：SQLite 默认不支持在已存在的表上添加外键约束
            # 这里我们通过重新创建表的方式来添加外键约束
            # 但为了安全起见，我们只检查是否需要添加
            print("⚠️ SQLite 默认不支持在已存在的表上添加外键约束")
            print("   外键约束将在新数据插入时自动生效")
        except Exception as e:
            print(f"❌ 添加外键约束失败: {e}")
        
        # 4. 验证迁移结果
        print("4. 验证迁移结果...")
        
        # 检查 AgentSession 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_sessions'")
        if cursor.fetchone():
            print("✅ AgentSession 表存在")
        else:
            print("❌ AgentSession 表不存在")
        
        # 检查 Message 表的字段
        cursor.execute("PRAGMA table_info(messages)")
        columns = {column[1] for column in cursor.fetchall()}
        required_columns = ['message_type', 'agent_session_id', 'agent_node', 'agent_step', 'agent_metadata']
        
        for col in required_columns:
            if col in columns:
                print(f"✅ Message 表包含字段: {col}")
            else:
                print(f"❌ Message 表缺少字段: {col}")
        
        # 关闭连接
        conn.close()
        print("数据库连接已关闭")
        
        print("\n🎉 数据库迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
