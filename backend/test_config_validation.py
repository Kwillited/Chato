#!/usr/bin/env python3
"""
测试配置验证功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import config_manager

print("=== 测试配置验证功能 ===")

# 测试当前配置
is_valid, errors = config_manager.validate_vector_config()

print(f"配置验证结果: {'通过' if is_valid else '失败'}")

if not is_valid:
    print("错误信息:")
    for error in errors:
        print(f"  - {error}")
else:
    print("所有配置项都已正确设置")

# 打印当前配置
print("\n当前向量系统配置:")
print(f"vector_db_path: {config_manager.get('vector.vector_db_path')}")
print(f"embedder_model: {config_manager.get('vector.embedder_model')}")

print("\n=== 测试完成 ===")
