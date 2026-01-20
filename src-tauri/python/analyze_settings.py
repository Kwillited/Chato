#!/usr/bin/env python3
"""
分析当前settings表中的设置类型，为重构拆分提供依据
"""
import os
import sqlite3
import json

# 获取数据库路径
def get_db_path():
    # 简化路径，直接使用测试路径
    return os.path.join(os.getcwd(), 'test.db')

# 连接数据库并分析设置类型
def analyze_settings():
    # 从默认配置中分析设置结构
    from app.core.config import DEFAULT_CONFIG
    
    print(f"默认配置包含的设置项:")
    for key, value in DEFAULT_CONFIG.items():
        if isinstance(value, dict):
            print(f"  - {key}: 字典类型，包含键: {list(value.keys())}")
        else:
            print(f"  - {key}: {type(value).__name__}类型")
    
    # 查看模型定义
    print(f"\n当前Settings模型结构:")
    print("  - key: String类型，主键")
    print("  - value: Text类型，存储JSON字符串")
    
    # 查看相关代码引用
    print(f"\n当前设置相关的主要代码:")
    print("  - app/repositories/setting_repository.py: 处理设置的CRUD操作")
    print("  - app/core/data_manager.py: 从数据库加载和保存设置")
    print("  - app/models/models.py: Settings模型定义")

if __name__ == "__main__":
    analyze_settings()