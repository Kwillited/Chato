#!/usr/bin/env python3
"""
测试系统设置的CRUD功能
"""
import os
import sys
import tempfile
from app.repositories.setting_repository import SettingRepository
from app.core.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker

# 创建临时数据库进行测试
temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
temp_db.close()

# 修改数据库URL为临时数据库
os.environ['DATABASE_URL'] = f'sqlite:///{temp_db.name}'

# 导入所有模型，确保Base.metadata包含所有表定义
from app.models import models

# 创建所有表
Base.metadata.create_all(bind=engine)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# 测试系统设置的CRUD功能
def test_system_settings_crud():
    """
    测试系统设置的CRUD功能
    """
    print("🔄 开始测试系统设置的CRUD功能...")
    
    # 初始化设置仓库
    setting_repo = SettingRepository(session)
    
    # 1. 测试创建系统设置
    print("📝 测试创建系统设置...")
    system_settings_data = {
        'dark_mode': True,
        'font_size': 16,
        'chat_style_document': True,
        'view_mode': 'list'
    }
    
    created_setting = setting_repo.create_or_update_system_setting(system_settings_data)
    print(f"✅ 创建系统设置成功")
    print(f"   深色模式: {created_setting.dark_mode}")
    print(f"   字体大小: {created_setting.font_size}")
    print(f"   文档样式: {created_setting.chat_style_document}")
    print(f"   视图模式: {created_setting.view_mode}")
    
    # 2. 测试获取系统设置
    print("🔍 测试获取系统设置...")
    retrieved_setting = setting_repo.get_system_setting()
    print(f"✅ 获取系统设置成功")
    assert retrieved_setting is not None
    assert retrieved_setting.dark_mode == True
    assert retrieved_setting.font_size == 16
    assert retrieved_setting.chat_style_document == True
    assert retrieved_setting.view_mode == 'list'
    
    # 3. 测试更新系统设置
    print("🔧 测试更新系统设置...")
    updated_data = {
        'dark_mode': False,
        'font_size': 18,
        'view_mode': 'grid'
    }
    
    updated_setting = setting_repo.create_or_update_system_setting(updated_data)
    print(f"✅ 更新系统设置成功")
    print(f"   深色模式: {updated_setting.dark_mode}")
    print(f"   字体大小: {updated_setting.font_size}")
    print(f"   视图模式: {updated_setting.view_mode}")
    
    # 4. 验证更新后的设置
    print("✅ 验证更新后的设置...")
    final_setting = setting_repo.get_system_setting()
    assert final_setting.dark_mode == False
    assert final_setting.font_size == 18
    assert final_setting.view_mode == 'grid'
    assert final_setting.chat_style_document == True  # 未更新的字段应保持不变
    print("✅ 系统设置更新验证成功！")
    
    print("🎉 系统设置的CRUD功能测试通过！")
    return True

# 主函数
if __name__ == "__main__":
    try:
        if test_system_settings_crud():
            print("✅ 所有测试通过！")
            sys.exit(0)
        else:
            print("❌ 测试失败！")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 清理临时数据库
        session.close()
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)
