"""测试内存缓存同步功能"""
import sys
import os

# 添加项目根目录和backend目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app.core.cache import cache_manager
from app.services.settings.setting_service import SettingService

def test_cache_sync():
    """测试内存缓存同步功能"""
    print("开始测试内存缓存同步功能...")
    
    # 创建设置服务实例
    setting_service = SettingService()
    
    # 1. 清除缓存以确保测试环境干净
    print("\n1. 清除缓存...")
    cache_manager.set('settings', None)
    
    # 2. 测试获取默认设置
    print("\n2. 获取默认设置:")
    default_settings = setting_service.get_system_setting()
    print(f"默认设置: {default_settings}")
    
    # 3. 测试更新设置
    print("\n3. 更新设置...")
    test_data = {
        'dark_mode': True,
        'streaming_enabled': False,
        'chat_style': 'compact',
        'view_mode': 'list',
        'default_model': 'test-model'
    }
    
    updated_settings = setting_service.save_system_setting(test_data)
    print(f"更新后的设置: {updated_settings}")
    
    # 4. 检查内存缓存
    print("\n4. 检查内存缓存:")
    cache_settings = cache_manager.get('settings')
    print(f"缓存中的设置: {cache_settings}")
    
    # 5. 验证脏标记
    print("\n5. 验证脏标记:")
    is_dirty = cache_manager.is_dirty('settings')
    print(f"设置是否脏: {is_dirty}")
    
    # 6. 再次获取设置，验证是否从缓存中读取
    print("\n6. 再次获取设置:")
    reloaded_settings = setting_service.get_system_setting()
    print(f"重新获取的设置: {reloaded_settings}")
    
    # 7. 验证设置是否一致
    if reloaded_settings['dark_mode'] == test_data['dark_mode']:
        print("\n✅ 测试通过: 设置成功保存在内存缓存中")
    else:
        print("\n❌ 测试失败: 设置未正确保存到内存缓存")

if __name__ == "__main__":
    test_cache_sync()
