"""测试设置同步功能"""
import sys
import os

# 添加项目根目录和backend目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app.core.data_manager import load_data, save_settings_to_db
from app.core.cache import cache_manager
from app.services.settings.setting_service import SettingService

def test_settings_sync():
    """测试设置同步功能"""
    print("开始测试设置同步功能...")
    
    # 初始化数据
    load_data()
    
    # 创建设置服务实例
    setting_service = SettingService()
    
    # 1. 测试获取默认设置
    print("\n1. 获取默认设置:")
    default_settings = setting_service.get_system_setting()
    print(f"默认设置: {default_settings}")
    
    # 2. 测试更新设置
    print("\n2. 更新设置...")
    test_data = {
        'dark_mode': True,
        'streaming_enabled': False,
        'chat_style': 'compact',
        'view_mode': 'list',
        'default_model': 'test-model'
    }
    
    updated_settings = setting_service.save_system_setting(test_data)
    print(f"更新后的设置: {updated_settings}")
    
    # 3. 检查内存缓存
    print("\n3. 检查内存缓存:")
    cache_settings = cache_manager.get('settings')
    print(f"缓存中的设置: {cache_settings}")
    
    # 4. 手动触发保存到数据库
    print("\n4. 手动触发保存到数据库...")
    save_result = save_settings_to_db()
    print(f"保存结果: {save_result}")
    
    # 5. 验证脏标记已清除
    print("\n5. 验证脏标记:")
    is_dirty = cache_manager.is_dirty('settings')
    print(f"设置是否脏: {is_dirty}")
    
    # 6. 重新加载数据并验证
    print("\n6. 重新加载数据并验证...")
    # 清除缓存以模拟重新启动
    cache_manager.set('settings', None)
    # 重新加载
    load_data()
    # 获取重新加载后的设置
    reloaded_settings = setting_service.get_system_setting()
    print(f"重新加载后的设置: {reloaded_settings}")
    
    # 验证设置是否一致
    if reloaded_settings['dark_mode'] == test_data['dark_mode']:
        print("\n✅ 测试通过: 设置成功保存并加载")
    else:
        print("\n❌ 测试失败: 设置未正确保存")

if __name__ == "__main__":
    test_settings_sync()
