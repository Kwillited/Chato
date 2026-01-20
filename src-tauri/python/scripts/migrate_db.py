#!/usr/bin/env python3
"""
数据库迁移脚本，用于更新表结构
"""
import sys
import os
from sqlalchemy import inspect, text
from app.core.database import engine, Base
from app.models.models import (
    Model, ModelVersion, Chat, Message, VectorSetting, MCPSetting,
    NotificationSetting, AppSetting, SystemSetting, Folder, Document, DocumentChunk
)

def migrate_database():
    """
    迁移数据库表结构
    """
    print("🔄 开始数据库迁移...")
    
    # 获取数据库检查器
    inspector = inspect(engine)
    
    # 1. 检查并创建所有表（如果不存在）
    print("📝 检查并创建所有表...")
    Base.metadata.create_all(bind=engine)
    
    # 2. 检查SystemSetting表是否缺少字段
    print("🔍 检查SystemSetting表结构...")
    system_table_name = "system_settings"
    
    # 获取当前表的列
    if system_table_name in inspector.get_table_names():
        columns = {col['name'] for col in inspector.get_columns(system_table_name)}
        
        # 定义所有必需的列
        required_columns = {
            'id', 'dark_mode', 'font_size', 'font_family', 'language',
            'auto_scroll', 'show_timestamps', 'confirm_delete',
            'streaming_enabled', 'chat_style_document', 'view_mode', 'default_model',
            'rag_view_mode'
        }
        
        # 检查缺少的列
        missing_columns = required_columns - columns
        
        if missing_columns:
            print(f"   ⚠️  发现缺少的列: {missing_columns}")
            
            # 使用ALTER TABLE添加缺少的列
            with engine.connect() as conn:
                for col in missing_columns:
                    # 根据列名确定数据类型和默认值
                    column_type = ""
                    default_value = ""
                    
                    if col == 'default_model':
                        column_type = "TEXT"
                        default_value = "''"
                    elif col == 'font_family':
                        column_type = "TEXT"
                        default_value = "'Inter, system-ui, sans-serif'"
                    elif col == 'language':
                        column_type = "TEXT"
                        default_value = "'zh-CN'"
                    elif col in ['dark_mode', 'auto_scroll', 'show_timestamps', 'confirm_delete', 'streaming_enabled', 'chat_style_document', 'rag_view_mode']:
                        column_type = "INTEGER"
                        default_value = "1"
                    elif col == 'font_size':
                        column_type = "INTEGER"
                        default_value = "16"
                    elif col == 'view_mode':
                        column_type = "TEXT"
                        default_value = "'grid'"
                    
                    print(f"   ➕ 添加列 {col} 到 {system_table_name} 表...")
                    stmt = text(f"ALTER TABLE {system_table_name} ADD COLUMN {col} {column_type} DEFAULT {default_value}")
                    conn.execute(stmt)
                    conn.commit()
            
            print(f"   ✅ 已添加所有缺少的列: {missing_columns}")
        else:
            print("   ✅ SystemSetting表结构完整")
    else:
        print(f"   ⚠️  表 {system_table_name} 不存在，已通过Base.metadata.create_all创建")
    
    # 3. 检查其他表的结构（可选，可根据需要扩展）
    print("🔍 检查其他设置表...")
    
    # 检查VectorSetting表
    vector_table_name = "vector_settings"
    if vector_table_name in inspector.get_table_names():
        columns = {col['name'] for col in inspector.get_columns(vector_table_name)}
        required_columns = {
            'id', 'retrieval_mode', 'top_k', 'score_threshold', 'vector_db_path',
            'embedder_model', 'vector_db_type', 'chunk_size', 'chunk_overlap'
        }
        missing_columns = required_columns - columns
        if missing_columns:
            print(f"   ⚠️  VectorSetting表缺少列: {missing_columns}")
        else:
            print("   ✅ VectorSetting表结构完整")
    
    # 检查MCPSetting表
    mcp_table_name = "mcp_settings"
    if mcp_table_name in inspector.get_table_names():
        columns = {col['name'] for col in inspector.get_columns(mcp_table_name)}
        required_columns = {'id', 'enabled', 'server_address', 'server_port', 'timeout'}
        missing_columns = required_columns - columns
        if missing_columns:
            print(f"   ⚠️  MCPSetting表缺少列: {missing_columns}")
        else:
            print("   ✅ MCPSetting表结构完整")
    
    # 检查NotificationSetting表
    notification_table_name = "notification_settings"
    if notification_table_name in inspector.get_table_names():
        columns = {col['name'] for col in inspector.get_columns(notification_table_name)}
        required_columns = {'id', 'enabled', 'new_message', 'sound', 'system', 'display_time'}
        missing_columns = required_columns - columns
        if missing_columns:
            print(f"   ⚠️  NotificationSetting表缺少列: {missing_columns}")
        else:
            print("   ✅ NotificationSetting表结构完整")
    
    # 检查AppSetting表
    app_table_name = "app_settings"
    if app_table_name in inspector.get_table_names():
        columns = {col['name'] for col in inspector.get_columns(app_table_name)}
        required_columns = {'id', 'debug', 'host', 'port'}
        missing_columns = required_columns - columns
        if missing_columns:
            print(f"   ⚠️  AppSetting表缺少列: {missing_columns}")
        else:
            print("   ✅ AppSetting表结构完整")
    
    print("🎉 数据库迁移完成！")

if __name__ == "__main__":
    migrate_database()
