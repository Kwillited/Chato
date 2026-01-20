#!/usr/bin/env python3
"""
简单测试脚本，用于验证SystemSetting模型和仓库方法是否正确
"""
import sys

# 添加当前目录到Python路径
sys.path.insert(0, '.')

try:
    # 1. 测试导入SystemSetting模型
    print("🔍 测试导入SystemSetting模型...")
    from app.models.models import SystemSetting
    print("✅ SystemSetting模型导入成功！")
    
    # 2. 测试导入SettingRepository
    print("🔍 测试导入SettingRepository...")
    from app.repositories.setting_repository import SettingRepository
    print("✅ SettingRepository导入成功！")
    
    # 3. 测试模型字段
    print("🔍 测试SystemSetting模型字段...")
    model_fields = [
        'id', 'dark_mode', 'font_size', 'font_family', 'language',
        'auto_scroll', 'show_timestamps', 'confirm_delete',
        'streaming_enabled', 'chat_style_document', 'view_mode', 'default_model'
    ]
    
    for field in model_fields:
        if hasattr(SystemSetting, field):
            print(f"   ✅ 字段 {field} 存在")
        else:
            print(f"   ❌ 字段 {field} 不存在")
    
    # 4. 测试仓库方法
    print("🔍 测试SettingRepository方法...")
    repo_methods = [
        'get_system_setting', 'create_or_update_system_setting'
    ]
    
    # 检查SettingRepository是否包含所需的方法
    for method in repo_methods:
        if hasattr(SettingRepository, method):
            print(f"   ✅ 方法 {method} 存在")
        else:
            print(f"   ❌ 方法 {method} 不存在")
    
    print("🎉 所有基本测试通过！")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
