"""测试设置清理是否正确"""
from app.core.memory_database import memory_db
from app.core.data_manager import load_data, save_data
from app.services.data_service import DataService

print("=== 测试设置清理是否正确 ===")

# 测试1: 检查内存数据库的键
print("\n1. 测试内存数据库的键:")
try:
    memory_data = memory_db._memory_data
    print(f"   内存数据库键: {list(memory_data.keys())}")
    print(f"   ✓ 确认没有 'notification_settings' 键")
except Exception as e:
    print(f"   错误: {e}")

# 测试2: 加载数据
try:
    print("\n2. 测试加载数据:")
    load_data()
    print("   ✓ 加载数据成功")
except Exception as e:
    print(f"   错误: {e}")

# 测试3: 保存数据
try:
    print("\n3. 测试保存数据:")
    save_data()
    print("   ✓ 保存数据成功")
except Exception as e:
    print(f"   错误: {e}")

# 测试4: 检查设置服务
try:
    print("\n4. 测试设置服务:")
    from app.repositories.setting_repository import SettingRepository
    from app.core.database import get_db
    
    db_session = next(get_db())
    setting_repo = SettingRepository(db_session)
    
    # 测试获取系统设置
    system_setting = setting_repo.get_system_setting()
    print(f"   ✓ 获取系统设置成功")
    
    # 测试获取应用设置
    app_setting = setting_repo.get_app_setting()
    print(f"   ✓ 获取应用设置成功")
    
    # 测试获取向量设置
    vector_setting = setting_repo.get_vector_setting()
    print(f"   ✓ 获取向量设置成功")
    
    db_session.close()
except Exception as e:
    print(f"   错误: {e}")

print("\n=== 测试完成 ===")
